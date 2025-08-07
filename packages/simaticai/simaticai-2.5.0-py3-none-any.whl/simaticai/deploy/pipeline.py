# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import json
import logging
import math
import os
import uuid
import platform
import shutil
import sys
import zipfile
from datetime import datetime
from importlib import resources as module_resources
from pathlib import Path, PurePath
from typing import Optional, Tuple, Union, List

import jsonschema
import jsonschema.exceptions
import pkg_resources
import yaml

from simaticai.deploy.component import Component
from simaticai.deploy.python_component import PythonComponent, python_version_validator
from simaticai.deploy.pipeline_data import PipelineData
import simaticai.deploy.pipeline_page as p_page

from simaticai.helpers import tempfiles, yaml_helper, calc_sha
from simaticai.packaging.constants import (
    PIPELINE_CONFIG, RUNTIME_CONFIG, DATALINK_METADATA,  # pipeline configuration files
    TELEMETRY_YAML, README_HTML,  # additional pipeline information files
    REQUIREMENTS_TXT, PYTHON_PACKAGES_ZIP,  # component dependency configuration
    PYTHON_PACKAGES, MSG_NOT_FOUND,  # additional constants
    PIPELINE_SIZE_LIMIT
)
from simaticai.packaging.wheelhouse import create_wheelhouse
from simaticai.helpers.reporter import PipelineReportWriter, ReportWriterHandler
from simaticai.packaging.python_dependencies import _logger as _python_dependencies_logger
from simaticai.packaging.wheelhouse import _logger as _wheelhouse_logger

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

__all__ = [
    'Pipeline',
    'convert_package',
    '_validate_with_schema',
    '_package_component',
    '_package_component_dependencies',
    '_generate_runtime_config'
]


class Pipeline(PipelineData):
    """
    `Pipeline` represents a pipeline configuration package with `Components` and wires to provide a data flow on the AI Inference Server.
    The `Components` have inputs and outputs to transfer data to each other and the wires describe this data flow between them.
    The package also contains configuration files required to deploy a pipeline on an Industrial Edge device.

    A newly initialized `Pipeline` does not contain any `Component` or wire, only its name and version will be set.
    The name and version together will define the name of the zip file when the package is saved.

    Args:
        name (str): Name of the package
        version (str): Version of the package
    """
    _wire_hash_string = "{}.{} -> {}.{}"

    def __init__(self, name: str, version: Optional[str] = None, desc: str = ""):
        """
        A newly initialized `Pipeline` will contain no `Component` or wire, just its name and version will be set.
        The name and version will define together the name of the zip file when the package is saved.

        Args:
            name (str): Name of the package
            desc (str): Package description (optional)
            version (str): Version of the package
        """

        super().__init__(name, version, desc)

        self.report_writer = PipelineReportWriter()
        report_writer_handler = ReportWriterHandler(self.report_writer)
        _logger.addHandler(report_writer_handler)
        _python_dependencies_logger.addHandler(report_writer_handler)
        _wheelhouse_logger.addHandler(report_writer_handler)

    def _set_log_level(self, log_level: int):
        self.log_level = log_level
        _logger.setLevel(self.log_level)

    @staticmethod
    def from_components(components: list, name: str, version: Optional[str] = None, desc: str = "") -> "Pipeline":
        """
        Creates a pipeline configuration from the given components.
        The components are linked in a linear sequence with inputs and outputs auto-wired based on the name of the inputs and outputs of the components.
        The inputs of the first component will be wired as the pipeline inputs and the outputs of the last component will be wired as the pipeline outputs.
        The components must have unique names. Two or more versions of the same component can not be packaged simultaneously without renaming them.

        Args:
            components (list): List of PythonComponents
            name (str): Name of the pipeline
            version (str): Version information of the pipeline. (Optional)
        Returns:
            Pipeline: Pipeline object with the auto-wired components
        """
        pipeline = Pipeline(name, version, desc=desc)

        first_component = components[0]
        pipeline.add_component(first_component)
        pipeline.inputs = [(first_component.name, component_input) for component_input in first_component.inputs]
        pipeline.outputs = [(first_component.name, output) for output in first_component.outputs]

        for component in components[1:]:
            pipeline.add_component(component)
            for (wire_component, wire_name) in pipeline.outputs:
                try:
                    pipeline.add_wiring(wire_component, wire_name, component.name, wire_name)
                except Exception as e:
                    _logger.warning(f"Output variable {wire_component}.{wire_name} couldn't be auto-wired.\nCause: {e}")

            unwired_variables = [f'{component.name}.{x}' for x in component.inputs if not any(s.endswith(f'{component.name}.{x}') for s in pipeline.wiring)]
            if len(unwired_variables) > 0:
                for variable in unwired_variables:
                    _logger.warning(f"Input variable {variable} couldn't be auto-wired.\n")
            pipeline.outputs = [(component.name, output) for output in component.outputs]

        return pipeline

    def __repr__(self) -> str:
        """
        Textual representation of the configured package.
        The method shows the `Components` with their inputs, outputs and parameters as well as the wiring between these `Components`.

        Returns:
            [str]: Textual representation of the package
        """
        version = self.save_version if self.save_version is not None else self.init_version

        text = f"[{self.__class__.__name__}] {self.name} ({version})\n"
        if self.desc != "":
            text += f"{self.desc}\n"

        if len(self.parameters) > 0:
            text += "\nPipeline Parameters:\n"
            for name, parameter in self.parameters.items():
                text += f"- {name} ({parameter['type']}, default: '{parameter['defaultValue']}'){(': ' + parameter['desc']) if parameter.get('desc') is not None else ''}\n"

        if len(self.inputs) > 0:
            text += "\nPipeline Inputs:\n"
            for component, name in self.inputs:
                input = self.components[component].inputs[name]
                text += f"> {name} ({input['type']}){': ' + input['desc'] if input.get('desc') is not None else ''}\n"

        if len(self.outputs) > 0:
            text += "\nPipeline Outputs:\n"
            for component, name in self.outputs:
                output = self.components[component].outputs[name]
                text += f"< {name} ({output['type']}){': ' + output['desc'] if output.get('desc') is not None else ''}\n"

        metrics = [(name, metric, component_name) for component_name, component in self.components.items() if isinstance(component, PythonComponent) for name, metric in component.metrics.items()]
        if len(metrics) > 0:
            text += "\nMetrics:\n"
            for name, metric, _ in metrics:
                text += f"< {name}{': ' + metric['desc'] if metric.get('desc') is not None else ''}\n"

        if len(self.wiring) > 0:
            text += "\nI/O Wiring:\n"
            for component, name in self.inputs:
                text += f"  {name} -> {component}.{name}\n"
            for wire_hash in self.wiring:
                text += f"  {wire_hash}\n"
            for component, name in self.outputs:
                text += f"  {component}.{name} -> {name}\n"
            for name, metric, component_name in metrics:
                text += f"  {component_name}.{name} -> {name}\n"

        if self.periodicity is not None:
            text += "\nTimeshifting:\n"
            text += f"  Periodicity: {self.periodicity} ms\n"
            if len(self.timeshift_reference) > 0:
                text += "  References:\n"
                for ref in self.timeshift_reference:
                    text += f"  - {ref}\n"

        for component in self.components.values():
            text += "\n" + component.__repr__()

        return text

    def add_input(self, component, variable):
        """
        Defines an input variable on the given component as a pipeline input.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable
        """
        try:
            _ = self.components[component].inputs[variable]
        except KeyError:
            raise AssertionError("The component with input variable must exist in the pipeline.")

        if self.inputs is None:
            self.inputs = []

        if (component, variable) in self.inputs:
            raise AssertionError("The pipeline input already exists.")

        self.inputs.append((component, variable))

    def delete_input(self, component: str, variable: str):
        """
        Deletes a pipeline input.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable

        """
        if (component, variable) not in self.inputs:
            raise AssertionError("The pipeline input does not exist.")

        self.inputs.remove((component, variable))

    def add_output(self, component, variable):
        """
        Defines an output variable on the given component as a pipeline output.

        Args:
            component (str): Name of the component
            variable (str): Name of the output variable

        """
        try:
            _ = self.components[component].outputs[variable]
        except KeyError:
            raise AssertionError("The component with output variable must exist in the pipeline.")

        if self.outputs is None:
            self.outputs = []

        if (component, variable) in self.outputs:
            raise AssertionError("The pipeline output already exists.")

        self.outputs.append((component, variable))

    def delete_output(self, component: str, variable: str):
        """
        Deletes a pipeline output.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable

        """
        if (component, variable) not in self.outputs:
            raise AssertionError("The pipeline output does not exist.")

        self.outputs.remove((component, variable))

    def add_component(self, component: Component):
        """
        Adds a `Component` to the pipeline configuration without any connection.
        The `Component` can be marked as an input or output component of the pipeline.
        When these parameters are True, the `Component` is responsible for input or output data of the pipeline.
        The component must have a unique name. Two or more versions of the same component can not be added to the same pipeline with the same component name.

        Args:
            component (Component): `Component` to be added
        """

        if component.name in self.components:
            raise AssertionError(f"Component with name {component.name} already exists. Please rename the component.")
        self.components[component.name] = component

    def add_wiring(self, from_component: str, from_output: str, to_component: str, to_input: str):
        """
        Creates a one-to-one connection between the input and output of two components.
        The method checks if the connection is allowed with the following requirements:

        - The components exist with the given inputs/outputs
        - The given inputs and outputs are not connected to any wire
        - The types of the connected input and output are compatible

        Args:
            from_component (str): Name of the component which provides data to the `to_component`
            from_output (str): Name of the output variable of the `from_component`
            to_component (str): Name of the component which consumes data from the `from_component`
            to_input (str): Name of the input variable of the `to_component`
        """
        if from_component not in self.components:
            raise AssertionError(f"No component named '{from_component}'")
        if to_component not in self.components:
            raise AssertionError(f"No component named '{to_component}'")
        if from_output not in self.components[from_component].outputs:
            raise AssertionError(f"Component '{from_component}' has no output named '{from_output}'")
        if to_input not in self.components[to_component].inputs:
            raise AssertionError(f"Component '{to_component}' has no input named '{to_input}'")
        if self.get_wire_for_input(to_component, to_input) is not None:
            raise AssertionError(f"Input '{to_input}' of component '{to_component}' is already wired")

        _output_type = self.components[from_component].outputs[from_output]["type"]
        _input_type = self.components[to_component].inputs[to_input]["type"]
        if _output_type != _input_type:
            raise AssertionError("Output and input types do not match")

        wire_hash = self._wire_hash_string.format(from_component, from_output, to_component, to_input)
        self.wiring[wire_hash] = {
            "fromComponent": from_component,
            "fromOutput": from_output,
            "toComponent": to_component,
            "toInput": to_input,
        }

    def get_wire_for_output(self, component_name: str, output_name: str):
        """
        Searches for the wire which connects a component with `component_name` as data provider through its output with name output_name.

        Args:
            component_name (str): Name of the data provider component.
            output_name (str): Name of the output variable of `component_name`.

        Returns:
            [dict]: Wire which contains the data provider and receiver with their names and the names of their variables.
        """
        wires = [x for x in self.wiring.values() if x["fromComponent"] == component_name and x["fromOutput"] == output_name]
        return wires[0] if wires else None

    def get_wire_for_input(self, component_name: str, input_name: str):
        """
        Searches for the wire which connects a component with `component_name` as data consumer through its input with name `input_name`.

        Args:
            component_name (str): Name of the data consumer component.
            input_name (str): Name of the input variable of `component_name`.

        Returns:
            dict: Wire which contains the data provider and receiver with their names and the names of their variables.
        """
        wires = [x for x in self.wiring.values() if x["toComponent"] == component_name and x["toInput"] == input_name]
        return wires[0] if wires else None

    def delete_input_wire(self, component: str, variable: str, with_input: bool = True):
        """
        Deletes an existing connection between two components.
        The connection must be given with the name of the consumer component and its input variable.
        If an inter signal alignment reference variable is affected it cannot be deleted.
        By default, the input variable will be also deleted.

        Args:
            component (str): Name of the component which has the input given the name variable
            variable (str): Name of the input variable on the component which connected by the wire
            with_input (bool, optional): If set, the input variable will be also deleted from the component. Defaults to True.

        Raises:
            AssertionError: When the variable acts as inter signal alignment reference, it cannot be deleted, and an `AssertionError` will be raised.
        """
        wire = self.get_wire_for_input(component, variable)
        if wire is None:
            raise AssertionError(f"There is no wiring for input '{variable}' of component '{component}'")
        if variable in self.timeshift_reference:
            raise AssertionError("Inter signal alignment reference variables can not be deleted.")
        wire_hash = self._wire_hash_string.format(wire['fromComponent'], wire['fromOutput'], wire['toComponent'], wire['toInput'])
        self.wiring.pop(wire_hash)

        if with_input:
            self.components[component].delete_input(variable)

    def add_dependencies(self, packages: list):
        """
        @Deprecated, reason: components can have different Python versions and/or platform, therefore it's better to specify dependencies on a case-by-case basis.
        Collects the given Python packages with their versions from the executing Python environment and add them to all components of type `PythonComponent`.
        This step is necessary in order to execute the pipeline configuration on the Edge side.
        The method can be called multiple times but each time the previously-collected dependencies are cleared.
        The reason for this is to ensure a consistent dependency list for the `requirements.txt` file when the package is saved.

        Args:
            packages (list): List of the necessary python packages to execute the script defined by self.entrypoint
        """
        python_components = [self.components[name] for name in self.components if type(self.components[name]) is PythonComponent]
        for component in python_components:
            component.add_dependencies(packages)

    def set_timeshifting_periodicity(self, periodicity: int):
        """
        Enables inter-signal alignment with the given sampling period.

        With inter-signal alignment enabled, the AI Inference Server collects data for different input variables before it triggers the model.
        By default, `startingPoint` property is set to `First timestamp`, which means that inter-signal alignment is started at the
        first incoming value for any input variable.

        This property can be changed to `Signal reference` by adding inter-signal alignment reference variables
        via the `add_timeshifting_reference(..)` method. In this case, inter-signal alignment is started when the first value arrives
        for the defined input variables.

        Args:
            periodicity (int): Periodicity time in milliseconds for the AI Inference Server to perform inter-signal alignment. Valid range is [10, 2^31).
        """

        periodicity = int(periodicity)
        if periodicity not in range(10, int(math.pow(2, 31))):
            raise AssertionError("Inter signal alignment periodicity must be an integer and in range [10, 2^31)")

        self.periodicity = periodicity
        _logger.info(f"Inter signal alignment periodicity has been set to {self.periodicity}.")

    def add_timeshifting_reference(self, reference: str):
        """
        Enables signal alignment mode `Signal reference` by declaring input variables as reference variables.

        Args:
            reference (str): Variable name to be added to `self.timeshift_reference` list.
        """
        if reference not in [name for _, name in self.inputs]:
            raise AssertionError(f"There is no input variable defined with name '{reference}'")
        if reference in self.timeshift_reference:
            _logger.warning(f"Reference variable with name '{reference}' has been already added.")
            return
        self.timeshift_reference.append(reference)

    def remove_timeshifting_reference(self, reference: str):
        """
        Removes previously-defined inter-signal alignment reference variables.
        If no reference variables remain, the `startingPoint` will be `First timestamp`.

        Args:
            reference (str): Variable name to be removed from `self.timeshift_reference` list.
        """
        if reference not in self.timeshift_reference:
            raise AssertionError(f"Reference variable with name {'reference'} does not exist.")
        self.timeshift_reference.remove(reference)

    def get_pipeline_config(self):
        """
        Saves the information on the composed pipeline configuration package into a YAML file.

        This YAML file describes the components and the data flow between them for the AI Inference Server.
        The file is created in the `destination` folder with name `pipeline_config.yml`
        """
        version = self.save_version if self.save_version is not None else self.init_version

        filtered_pipeline_outputs = [(component_name, name) for component_name, name in self.outputs if self.components[component_name].outputs[name]['type'].lower() != 'imageset']
        metric_fields = [(component_name, field) for component_name, component in self.components.items() if isinstance(component, PythonComponent) for field in component.metrics.keys()]

        pipeline_inputs = [{
            'name': name,
            'type': self.components[component_name].inputs[name]['type']
        } for component_name, name in self.inputs]

        pipeline_outputs = [{
            'name': name,
            'type': self.components[component_name].outputs[name]['type'],
            'metric': False,
        } for component_name, name in filtered_pipeline_outputs]
        pipeline_outputs += [{
            'name': field,
            'type': 'String',
            'metric': True,
            'topic': f"/siemens/edge/aiinference/{self.name}/{version}/metrics/{component_name}/{field}",
        } for component_name, field in metric_fields]

        pipeline_dag = [{
            'source': f"{wire['fromComponent']}.{wire['fromOutput']}",
            'target': f"{wire['toComponent']}.{wire['toInput']}",
        } for wire in self.wiring.values()]
        pipeline_dag += [{
            'source': f'Databus.{name}',
            'target': f'{component_name}.{name}',
        } for component_name, name in self.inputs]
        pipeline_dag += [{
            'source': f'{component_name}.{name}',
            'target': f'Databus.{name}',
        } for component_name, name in filtered_pipeline_outputs]
        pipeline_dag += [{
            'source': f'{component_name}.{field}',
            'target': f'Databus.{field}',
        } for component_name, field in metric_fields]

        config_yml_content = {
            'fileFormatVersion': '1.2.0',
            'dataFlowPipelineInfo': {
                'author': self.author,
                'createdOn': datetime.now(),
                'dataFlowPipelineVersion': version,
                'description': self.desc if self.desc else 'Created by AI SDK',
                'projectName': self.name,
                'packageId': str(self.package_id)
            },
            'dataFlowPipeline': {
                'components': [component._to_dict() for component in self.components.values()],
                'pipelineDag': pipeline_dag,
                'pipelineInputs': pipeline_inputs,
                'pipelineOutputs': pipeline_outputs,
            },
            'packageType': 'full'
        }
        if len(self.parameters.items()) != 0:
            config_yml_content["dataFlowPipeline"]["pipelineParameters"] = []
            for name, parameter in self.parameters.items():
                if parameter["topicBased"]:
                    config_yml_content["dataFlowPipeline"]["pipelineParameters"].append({
                        'name': name, 'type': parameter['type'],
                        'defaultValue': parameter['defaultValue'],
                        'topicBased': parameter['topicBased'], 'valueTopic': parameter['valueTopic']
                    })
                else:
                    config_yml_content["dataFlowPipeline"]["pipelineParameters"].append({
                        'name': name, 'type': parameter['type'],
                        'defaultValue': parameter['defaultValue']
                    })

        return config_yml_content

    def save_pipeline_config(self, destination):
        """
        Saves the information about the composed pipeline configuration package into a YAML file.

        This YAML file describes the components and the data flow between them for AI Inference Server.
        The file will be created in the `destination` folder with name `pipeline_config.yml`

        Args:
            destination (path-like): Path of the `destination` directory.
        """

        with open(Path(destination) / PIPELINE_CONFIG, "w") as f:
            yaml.dump(self.get_pipeline_config(), f)

    def get_datalink_metadata(self):
        """
        The method generates metadata information based on available information.

        Returns:
            dict: Dictionary with the necessary information for the AI Inference Server.
        """

        timeshifting = {
            "id": None,
            "enabled": False,
            "periodicity": self.periodicity,
            "startingPoint": None,
        }

        if self.periodicity is not None:
            timeshifting["enabled"] = True
            timeshifting["startingPoint"] = 'First timestamp'

        if len(self.timeshift_reference) > 0:
            timeshifting["startingPoint"] = 'Signal reference'

        exported_metadata = {
            "fileFormatVersion": "1.0.0",
            "id": None,
            "version": None,
            "createdOn": datetime.now(),
            "updatedOn": datetime.now(),
            "timeShifting": timeshifting,
            "inputs": [
                {
                    'name': _name,
                    'mapping': None,
                    'timeShiftingReference': _name in self.timeshift_reference,
                    'type': self.components[_component].inputs[_name]['type']
                } for _component, _name in self.inputs
            ]
        }
        return exported_metadata

    def save_datalink_metadata(self, destination):
        """
        Saves metadata for pipeline input variables.
        This method saves metadata for the AI Inference Server into a YAML file.
        This metadata determines how the AI Inference Server feeds input to the pipeline, especially inter-signal alignment.
        The file is created in the `destination` folder with the name `datalink_metadata.yml`

        Args:
            destination (path-like): Path of the destination directory.
        """
        with open(Path(destination) / DATALINK_METADATA, "w") as f:
            yaml.dump(self.get_datalink_metadata(), f)

    def save_telemetry_data(self, destination: Path):
        """
        Save telemetry data to a specified destination.

        Args:
            destination (Path): The path where the telemetry data should be saved.

        Returns:
            None

        Raises:
            None
        """
        telemetry_path = destination / TELEMETRY_YAML
        telemetry_data = {}

        telemetry_data["platform"] = {}
        telemetry_data["platform"]["os"] = platform.system()
        telemetry_data["platform"]["release"] = platform.release()
        telemetry_data["platform"]["python_version"] = platform.python_version()

        _logger.info(f"locals: {locals()}")
        telemetry_data["environment"] = {}

        telemetry_data["environment"]["jupyter"]        = any(k for k in locals() if k in ["__IPYTHON__", "get_ipython"])

        telemetry_data["environment"]["gitlab_ci"]      = True if "GITLAB_CI" in os.environ else MSG_NOT_FOUND
        telemetry_data["environment"]["azure_devops"]   = True if "TF_BUILD" in os.environ else MSG_NOT_FOUND
        telemetry_data["environment"]["github_actions"] = True if "GITHUB_ACTIONS" in os.environ else MSG_NOT_FOUND

        telemetry_data["industrial_ai"] = {}
        telemetry_data["industrial_ai"]["simaticai"] = MSG_NOT_FOUND
        telemetry_data["industrial_ai"]["vep-template-sdk"] = MSG_NOT_FOUND
        try:
            telemetry_data["industrial_ai"]["simaticai"] = pkg_resources.get_distribution("simaticai").version
        except pkg_resources.DistributionNotFound:
            _logger.debug("simaticai package not found")

        try:
            telemetry_data["industrial_ai"]["vep-template-sdk"] = pkg_resources.get_distribution("vep-template-sdk").version
        except pkg_resources.DistributionNotFound:
            _logger.debug("vep-template-sdk package not found")

        telemetry_data["pipeline"] = {}
        telemetry_data["pipeline"]["python_versions"] = list(set(self.components[component].python_version for component in self.components if isinstance(self.components[component], PythonComponent)))
        telemetry_data["pipeline"]["file_extensions"] = list(set(f.suffix for f in Path(destination).rglob("*") if f.suffix not in ["", ".zip", ".yml", ".yaml", ".html"]))

        yaml.dump(telemetry_data, open(telemetry_path, 'w'))

    def validate(self, destination="."):
        """
        Validates whether the package configuration is compatible with the expected runtime environment.

        The method verifies:

        - If the package has at least one component
        - If all wires create connections between existing components and their variables
        - If metadata is defined and valid.
        - If a package with the same name already exists in the `destination` folder. In this case a warning message appears and the `save(..)` method overwrites the existing package.
        - If the package has multiple components and if they are using the same Python version

        Args:
            destination (str, optional): Path of the expected destination folder. Defaults to ".".
        """
        version = self.save_version if self.save_version is not None else self.init_version

        if len(self.components) < 1:
            raise AssertionError("The package must have at least one component.")

        for name, variable in self.outputs:
            if self.components[name].batch.outputBatch:
                raise AssertionError(f"The component '{name}' has pipeline output defined with variable name '{variable}'. \
                                      None of component with pipeline output is allowed to provide batch output.")

        for wire_hash in self.wiring.copy():
            wire = self.wiring[wire_hash]
            self._check_wiring(wire, wire_hash)

        pipeline_inputs = [variable for _, variable in self.inputs]
        pipeline_outputs = [variable for _, variable in self.outputs]
        if any(variable in pipeline_outputs for variable in pipeline_inputs):
            conflicts = set(pipeline_inputs).intersection(set(pipeline_outputs))
            raise AssertionError(f"Pipeline input and output variables must be unique. Conflicting variables: {conflicts}")

        self._check_timeshifting()

        package_path = Path(destination) / f"{self.name}_{version}".replace(" ", "-")
        if package_path.is_dir():
            _logger.warning(f"Target folder ({package_path}) already exists! Unless changing the package name the package could be invalid and your files will be overwritten!")

        python_versions = set()

        for component in self.components:
            self.components[component].validate()

            if isinstance(self.components[component], PythonComponent):
                python_versions.add(self.components[component].python_version)

        if (1 < len(python_versions)):
            _logger.warning("The use of multiple python version in a single pipeline is not recommended. We recommend using only one of the supported versions, which are Python 3.10 or 3.11.")

        _logger.info(f"Package '{self.name}' is valid and ready to save.")

    def _check_timeshifting(self):
        if len(self.timeshift_reference) > 0 and self.periodicity is None:
            raise AssertionError("When using inter signal alignment reference variables, the periodicity must be set.")

    def _check_wiring(self, wire, wire_hash):
        error_messages = []
        if wire['fromComponent'] not in self.components:
            error_messages.append(f"From component {wire['fromComponent']} does not exist")
        if wire['toComponent'] not in self.components:
            error_messages.append(f"To component {wire['toComponent']} does not exist")
        if wire['fromOutput'] not in self.components[wire['fromComponent']].outputs:
            error_messages.append(f"Output variable {wire['fromOutput']} does not exist on component {wire['fromComponent']}")
        if wire['toInput'] not in self.components[wire['toComponent']].inputs:
            error_messages.append(f"Input variable {wire['toInput']} does not exist on component {wire['toComponent']}")
        if len(error_messages) == 0:
            from_type_ = self.components[wire['fromComponent']].outputs[wire['fromOutput']]['type']
            to_type_ = self.components[wire['toComponent']].inputs[wire['toInput']]['type']
            if from_type_ != to_type_:
                error_messages.append(f"The types of input and output variables does not match for wiring {wire_hash}.")
        if len(error_messages) > 0:
            self.wiring.pop(wire_hash)
            error_messages.append("The wire has been deleted, please check the variables and re-create the connection.")
            raise AssertionError(error_messages.__str__())

    def save(self, destination = ".", package_id: Optional[uuid.UUID] = None, version: Optional[str] = None) -> Path:
        """
        @Deprecated, reason: only edge package generation will be supported in the future. Use export instead.

        Saves the assembled package in a zip format.
        The name of the file is defined as `{package_name}_{package_version}.zip`.
        If a file with such a name already exists in the `destination` folder, it gets overwritten and a warning message appears.

        The package is also available as a subfolder on the destination path with the name `{package_name}_{package_version}`.
        If the assembled content does not meet the expected one, this content can be changed and simply packed into a zip file.

        The package contains files and folders in the following structure:

        - Package folder with name `{package_name}_{package_version}`
            - `datalink-metadata.yml`
            - `pipeline-config.yml`
            - Component folder with name `{component_name}`

            When the component is a `PythonComponent`, this folder contains:

            - `requirements.txt`
            - Entrypoint script defined by the entrypoint of the component
            - Extra files as added to the specified folders
            - Source folder with name `src` with necessary python scripts

        If a package ID is specified, and a package with the same ID and version is already present in the `destination` folder,
        an error is raised.

        Args:
            destination (str, optional): Target directory for saving the package. Defaults to ".".
            package_id (UUID): The optional package ID. If None, a new UUID is generated.
        """
        self._set_save_version_and_package_id(Path(destination), package_id, version)

        self.validate(destination)
        destination = Path(destination)
        name = self.name.replace(" ", "-")
        package_name = f"{name}_{self.save_version}"

        destination = destination / package_name
        destination.mkdir(parents=True, exist_ok=True)

        # Save
        for component in self.components:
            self.components[component].save(destination, False)
            if isinstance(self.components[component], PythonComponent):
                self.report_writer.add_direct_dependencies(self.components[component].name, self.components[component].python_dependencies.dependencies)

        self.save_datalink_metadata(destination)
        self.save_pipeline_config(destination)
        p_page.save_readme_html(self, destination)
        self.save_telemetry_data(destination)

        zip_destination = shutil.make_archive(
            base_name=str(destination.parent / package_name), format='zip',
            root_dir=destination.parent, base_dir=package_name,
            verbose=True, logger=_logger)

        pipeline_size = os.path.getsize(zip_destination)  # zipped package size in bytes
        pipeline_size_GB = "{:.2f}".format(pipeline_size / 1000 / 1000 / 1000)
        pipeline_size_limit_GB = "{:.2f}".format(PIPELINE_SIZE_LIMIT / 1000 / 1000 / 1000)
        if pipeline_size > PIPELINE_SIZE_LIMIT:
            error_msg = f"Pipeline size {pipeline_size} bytes ({pipeline_size_GB} GB) exceeds the limit of " \
                        f"{PIPELINE_SIZE_LIMIT} bytes ({pipeline_size_limit_GB} GB). " \
                        "Please remove unnecessary files and dependencies and try again."

            _logger.error(error_msg)
            raise RuntimeError(error_msg)

        return Path(zip_destination)

    def _set_save_version_and_package_id(self, destination: Path, package_id: Optional[uuid.UUID], version: Optional[str]):
        previous_versions_and_ids = self._get_versions_and_package_ids_of_existing_packages(destination)
        previous_versions, previous_package_ids = zip(*previous_versions_and_ids) if previous_versions_and_ids else ([], [])

        # if package id is provided, we use that
        if package_id is not None:
            self.package_id = package_id
        # auto-generate package id if not provided
        else:
            previous_package_ids_set = {pkg_id for pkg_id in previous_package_ids if pkg_id is not None}
            if self.package_id is not None:
                previous_package_ids_set.add(self.package_id)

            if len(previous_package_ids_set) == 0:
                self.package_id = uuid.uuid4()
            elif len(previous_package_ids_set) == 1:
                self.package_id = previous_package_ids_set.pop()
            else:
                _logger.error(f"Multiple package IDs found in the destination folder: {previous_package_ids_set}. Set a package ID.")
                raise RuntimeError(f"Multiple package IDs found in the destination folder: {previous_package_ids_set}. Set a package ID.")

        # Preference #1: use the provided version
        if version is not None:
            self.save_version = version
        # Preference #2: use the version set at init time
        elif self.init_version is not None:
            self.save_version = self.init_version
        # Preference #3: auto-generate version
        else:
            previous_decimal_versions_set = {int(v) for v in previous_versions if v is not None and v.isdecimal()}
            if len(previous_decimal_versions_set) == 0:
                self.save_version = "1"
            else:
                self.save_version = str(max(previous_decimal_versions_set) + 1)

        # check if the package zip already exists
        name = self.name.replace(" ", "-")
        package_name = f"{name}_{self.save_version}"
        package_file = destination / f"{package_name}.zip"
        if package_file.exists():
            _logger.warning(f"Target package with version '{self.save_version}' already exists: '{package_file}. The package will be overwritten.")
        edge_package_file = destination / f"{name}-edge_{self.save_version}.zip"
        if edge_package_file.exists():
            _logger.warning(f"Target package with version '{self.save_version}' already exists: '{edge_package_file}. The package will be overwritten.")

    def _get_versions_and_package_ids_of_existing_packages(self, destination: Path) -> List[Tuple[str, Optional[uuid.UUID]]]:
        package_versions_and_ids = []
        for file in destination.glob(f"{self.name.replace(' ', '-')}*.zip"):
            with zipfile.ZipFile(file) as zip_file:
                config_path = next(f for f in zip_file.namelist() if f.endswith("pipeline_config.yml"))
                with zip_file.open(config_path) as config_file:
                    config = yaml.load(config_file, Loader=yaml.SafeLoader)
                    pipeline_info = config.get("dataFlowPipelineInfo", {})
                    name = pipeline_info.get("projectName", None)
                    if name is None or name != self.name:
                        continue
                    version = pipeline_info.get("dataFlowPipelineVersion", None)
                    package_id = pipeline_info.get("packageId", None)
                    package_id = uuid.UUID(package_id) if package_id is not None else None
                    package_versions_and_ids.append((version, package_id))
        return package_versions_and_ids

    def export(self, destination = ".", package_id: Optional[uuid.UUID] = None, version: Optional[str] = None) -> Path:
        """
        Export a runnable pipeline package.

        Args:
            destination (str): optional target directory for saving the package. Defaults to ".".
            package_id (UUID): optional package ID. If None, a new UUID is generated.
            version (str): optional version. If None, an automatic version number is generated.
        """
        config_package = None
        try:
            config_package = self.save(destination, package_id, version)
            runtime_package = convert_package(config_package, self.report_writer)
            return runtime_package
        finally:
            if config_package is not None:
                Path(config_package).unlink(missing_ok=True)

    def add_parameter(self, name: str, default_value, type_name: str = "String", topic_based: bool = False, desc: str = None):
        """
        Adds a parameter to the pipeline configuration, which alters the behavior of the pipeline.
        The parameter's default value and its properties are saved in the pipeline configuration
        and the value of the parameter can later be changed on AI Inference Server.

        Args:
            name (str): Name of the parameter
            desc (str): Description of the parameter (optional)
            type_name (str, optional): Data type of the parameter. Defaults to "String".
            default_value (str): Default value of the parameter
            topic_based (bool, optional): If true, the parameter can be updated from a message queue.

        Raises:

            ValueError:
                When:
                - the default value of the parameter is not of the specified data type (`type_name`) or
                - the specified data type itself is not an allowed data type (not a part of `parameter_types` dict) or
                - the specified data type is not given in the right format or
                - the type of the given `topic_based` parameter is not `bool`.
                - the name of the parameter starts with `__AI_IS_` prefix. These are reserved parameters by AI Inference Server
        """
        parameter_types = {
            "String": 'str',
            "Integer": 'int',
            "Double": 'float',
            "Boolean": 'bool'
        }

        default_value_type = type(default_value).__name__

        if name.startswith("__AI_IS_"):
            raise ValueError("Pipeline parameters with `__AI_IS_` prefix should not be specified in the pipeline configuration. However, the entrypoint script should be able to handle them in the `update_parameters` method.")

        if type_name not in parameter_types.keys():
            raise ValueError(f"The given value type is not supported. Please use one of these: {parameter_types.keys()}")

        if default_value_type != parameter_types[type_name]:
            raise ValueError(f"The given value type does not match the type of '{type_name}'. Please use the correct one from these: {list(parameter_types.keys())}")

        if not isinstance(topic_based, bool):
            raise ValueError("Type of the given `topic_based` parameter is not `bool`.")

        self.parameters[name] = {
            "name": name,
            "type": type_name,
            "defaultValue": default_value,
            "topicBased": topic_based,
            "valueTopic": None
        }
        if desc is not None:
            self.parameters[name]["desc"] = desc


def convert_package(zip_path: Union[str, os.PathLike], report_writer: Optional[PipelineReportWriter] = None) -> Path:
    """
    @Deprecated, reason: only edge package generation will be supported in the future. Use Pipeline.export(...) instead.

    Create an Edge Configuration Package from a given Pipeline Configuration Package.

    If the input zip file is `{path}/{name}_{version}.zip`, the output file will be created as `{path}/{name}-edge_{version}.zip`.
    Please make sure that the given zip file comes from a trusted source!

    If a file with such a name already exists, it is overwritten.

    First, this method verifies that the requirements identified by name and version are either included
    in `PythonPackages.zip` or available on pypi.org for the target platform.

    Currently, the supported edge devices run Linux on 64-bit x86 architecture, so the accepted Python libraries are restricted to the platform independent ones and packages built for 'x86_64' platforms.
    AI Inference Server also provides a Python 3.10 and runtime environment, so the supported Python libraries are restricted to Python 3.10 and 3.11 compatible packages.

    If for the target platform the required dependency is not available on pypi.org
    and not present in `PythonPackages.zip`,  it will log the problem at ERROR level.
    Then it downloads all dependencies (either direct or transitive), and creates a new zip
    file, which is validated against the AI Inference Server's schema.
    This functionality requires pip with version of 21.3.1 or greater.

    This method can be used from the command line too.
    Example usage:
    ```
    python -m simaticai convert_package <path_to_pipeline_configuration_package.zip>
    ```

    Args:
        zip_path (path-like): path to the pipeline configuration package zip file.
        report_writer (ReportWriter, optional): a ReportWriter object to write the report for a pipeline. Defaults to None.

    Returns:
        os.PathLike: The path of the created zip file.

    Exceptions:
        PipelineValidationError: If the validation fails. See the logger output for details.
    """
    zip_path = Path(zip_path)
    if zip_path.stem.find('_') < 0:
        raise AssertionError("The input zip file name must contain an underscore character.")
    with tempfiles.OpenZipInTemp(zip_path) as zip_dir:
        top_level_items = list(zip_dir.iterdir())
        if len(top_level_items) != 1:
            raise AssertionError("The Pipeline Configuration Package must contain a single top level directory.")
        package_dir = zip_dir / top_level_items[0]
        runtime_dir = zip_dir / "edge_config_package"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        config = yaml_helper.read_yaml(package_dir / PIPELINE_CONFIG)
        _validate_with_schema("input pipeline_config.yml", config, "pipeline.schema.json")
        runtime_config = _generate_runtime_config(config)
        if report_writer is not None:
            # TODO: consider moving zip_path to the parameter of report_writer.write_report()
            report_writer.set_path(Path(zip_path.parent / f"{zip_path.stem}_package_report.md"))
            report_writer.set_pipeline_config(config)

        for component in config['dataFlowPipeline']['components']:
            source_dir = package_dir / component["name"]

            if component["runtime"]["type"] == "python":
                python_version = component['runtime']['version']
                try:
                    python_version_validator(python_version)
                except ValueError as error:
                    raise AssertionError(error)

                dependency_set = _package_component_dependencies(source_dir, python_version)
                if report_writer is not None:
                    report_writer.add_full_dependency_set(component_name=component["name"], dependency_set=dependency_set)
                runtime_config["runtimeConfiguration"]["components"].append({
                    "name": component["name"],
                    "device": "IED1",
                    "targetRuntime": "Python",
                })

            if component["runtime"]["type"] == "gpuruntime":
                runtime_config["runtimeConfiguration"]["components"].append({
                    "name": component["name"],
                    "device": "IED1",
                    "targetRuntime": "gpuruntime",
                })

            _package_component(source_dir, runtime_dir / 'components' / f"{component['name']}_{component['version']}")

        if report_writer is not None:
            report_writer.write_report()
        _logger.info(f"Report on {zip_path.stem} is saved to {zip_path.parent}.")
        shutil.copy(str(package_dir / PIPELINE_CONFIG), str(runtime_dir / PIPELINE_CONFIG))
        datalink_metadata_yaml = package_dir / DATALINK_METADATA
        if datalink_metadata_yaml.is_file():
            shutil.copy(str(datalink_metadata_yaml), runtime_dir / DATALINK_METADATA)

        _validate_with_schema(f"generated {RUNTIME_CONFIG}", runtime_config, "runtime.schema.json")
        with open(runtime_dir / RUNTIME_CONFIG, "w", encoding="utf8") as file:
            yaml.dump(runtime_config, file)

        readme_html = package_dir / README_HTML
        if readme_html.exists():
            (runtime_dir / README_HTML).write_text(readme_html.read_text())

        telemetry_yaml = package_dir / TELEMETRY_YAML
        if telemetry_yaml.exists():
            (runtime_dir / TELEMETRY_YAML).write_text(telemetry_yaml.read_text())

        edge_package_path = Path(shutil.make_archive(
            # One Pythonic Way to replace the last occurrence of "_" with "-edge".
            base_name=str(PurePath(zip_path).parent / "-edge_".join(zip_path.stem.rsplit("_", 1))),
            format='zip',
            root_dir=runtime_dir,
            verbose=True,
            logger=_logger))

        sha256_hash = calc_sha(edge_package_path)
        sha_format = f"{sha256_hash}  {edge_package_path.name}"
        edge_package_path.with_suffix('.sha256').write_text(sha_format)

        return edge_package_path


def _validate_with_schema(name: str, data: dict, schema_name: str):
    try:
        schema_path = module_resources.files("simaticai") / "data" / "schemas" / schema_name
        with open(schema_path, "r", encoding="utf8") as schema_file:
            schema = json.load(schema_file)
            jsonschema.validate( instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        # f"""$id: {e.schema['$id']}
        # title: {e.schema['title']}
        # description: {e.schema['description']}"""
        raise AssertionError(f"""Schema validation failed for {name} using '{schema}'!
        message: {e.message}
        """) from None


def _package_component(source_dir, target_name):
    return shutil.make_archive(
        base_name=target_name,
        format='zip',
        root_dir=source_dir,
        verbose=True,
        logger=_logger)


def _package_component_dependencies(component_dir: Path, python_version: str) -> set:
    python_packages_folder = component_dir / 'packages'
    requirements_file_path = component_dir / REQUIREMENTS_TXT
    packages_file = component_dir / PYTHON_PACKAGES_ZIP
    dependency_set = set()

    python_packages_folder.mkdir(exist_ok=True)

    if packages_file.is_file():
        with zipfile.ZipFile(packages_file) as zip_file:
            zip_file.extractall(python_packages_folder)
        packages_file.unlink()
    requirements_file_path.touch(exist_ok=True)
    try:
        dependency_set = create_wheelhouse(requirements_file_path, python_version, python_packages_folder)

        if any(Path(python_packages_folder).iterdir()):
            shutil.make_archive(
                base_name=str(component_dir / PYTHON_PACKAGES),
                format='zip',
                root_dir=python_packages_folder,
                verbose=True,
                logger=_logger)
    finally:
        shutil.rmtree(python_packages_folder)

    # This filtering needs to happen here, not in PythonDependencies,
    # because create_wheelhouse still needs the original requirements.txt
    # with the extra index urls.
    with open(requirements_file_path, "r") as f:
        lines = f.readlines()
    filtered_lines = list(filter(lambda x: not (x.startswith("# Extra") or x.startswith("--extra-index-url") or x.startswith("# Index") or x.startswith("--index-url")), lines))
    with open(requirements_file_path, "w") as f:
        f.writelines(filtered_lines)

    return dependency_set


def _generate_runtime_config(pipeline_config: dict):
    project_name = pipeline_config["dataFlowPipelineInfo"]["projectName"]

    return {
        "fileFormatVersion": "1",
        "runtimeInfo": {
            "projectName": project_name,
            "runtimeConfigurationVersion": "1.0.0",
            "createdOn": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "runtimeConfiguration": {
            "devices": [{
                "name": "IED1",
                "address": "localhost",  # Optional
                "arch": "x86_64",  # Optional, TODO: validate target keys
            }],
            "components": [],
        },
    }
