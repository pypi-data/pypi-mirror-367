# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import logging
import os
import shutil
import sys
import re
from pathlib import Path
from typing import Optional, Union

from simaticai.deploy.component import Component
from simaticai.packaging.python_dependencies import PythonDependencies

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

__all__ = ['PythonComponent', 'python_version_validator']


def python_version_validator(version: str):
    """
    Checks if Python version string is valid and describes supported version.

    Only version 3.10 and 3.11 is supported. A patch version is optional and accepted but logs a warning.

    Accepted syntaxes are:

        - {major}.{minor}
        - {major}.{minor}.{patch}

    Args:
        version (str): Python version string

    Raises:
        ValueError: if the provided version is not supported
    """

    supported_versions = ["3.10", "3.11"]

    error_message = "The defined python version is not supported. Currently supported Python versions are 3.10 and 3.11. Python version must be specified only with major and minor version, e.g. '3.10'."

    warning_message = """Required Python version was specified with patch version.
                Please note that the patch digit of the required Python version is often not taken into account by the Python ecosystem,
                so there is no guarantee it has the desired effect."""

    python_version_matcher = re.match(r'^(3)\.(0|[1-9][0-9]*)\.?(0|[1-9][0-9]*)?$', str(version))

    major_minor_version = "0.0"
    has_patch_version = False

    if python_version_matcher is not None:
        major_minor_version = f"{python_version_matcher.group(1)}.{python_version_matcher.group(2)}"
        has_patch_version = python_version_matcher.group(3) is not None

    if major_minor_version not in supported_versions:
        raise ValueError(error_message)

    if has_patch_version:
        _logger.warning(warning_message)


class PythonComponent(Component):
    """
    A pipeline component implemented using Python scripts and libraries.

    A `PythonComponent` wraps Python code resource files such as saved models into a structured folder, which can be added to a pipeline
    configuration package.

    For a comprehensive overview on how to wrap ML models into Python components, we recommend you refer to
    the AI SDK User Manual, especially the guideline for writing pipeline components. We also recommend you
    study the example Python components in the E2E Tutorials for the AI SDK.

    A new `PythonComponent` is empty.

    Args:
        name (str): Component name. (default: inference)
        desc (str): Component description (optional)
        version (str): Component version. (default: 0.0.1)
        python_version (str): Python version on the target AI Inference Server.
            At the moment of writing, the current version supports Python 3.10 and 3.11.
    """

    def __init__(self, name="inference", version="0.0.1", python_version='3.10', desc: str = ""):
        """
        Creates a new, empty Python component.

        Args:
            name (str): Component name. (default: inference)
            desc (str): Component description (optional)
            version (str): Component version. (default: 0.0.1)
            python_version (str): Python version on the target AI Inference Server. At the moment of writing, AI Inference Server supports Python 3.10 and 3.11.
        """

        super().__init__(name=name, desc=desc)

        try:
            python_version_validator(python_version)
        except ValueError as error:
            raise AssertionError(error)

        self.python_version = python_version
        self.version = version
        self.metrics = {}
        self.entrypoint: Optional[Path] = None
        self.resources = {}
        self.python_dependencies = PythonDependencies(python_version)
        self._replicas = 1
        self.is_valid = False

    def __repr__(self) -> str:
        text = super().__repr__()

        if len(self.metrics) > 0:
            text += "\nMetrics:\n"
            for name, metric in self.metrics.items():
                text += f"< {name}{': ' + metric['desc'] if metric.get('desc') is not None else ''}\n"

        if len(self.resources):
            text += "\nResources:\n"
            for path, base in self.resources.items():
                text += f"  {base}/{path.name}\n".replace('./', '')

        if self.entrypoint is not None:
            text += f"Entrypoint: {self.entrypoint}\n"

        return text

    def set_entrypoint(self, entrypoint: str):
        """
        Sets the entrypoint module for the component.

        The entrypoint is the Python code which is responsible for receiving the input data and producing a structured response with the output for the AI Inference Server.
        The script should consume a JSON string and produce another. See the short example below.

        The file will be copied into the root directory of the component on the AI Inference Server, so every file reference should be aligned.

        The example code below shows a basic structure of the entrypoint Python code.
        ```python
        import json
        import sys
        from pathlib import Path

        # by adding the parent folder of your modules to system path makes them available for relative import
        sys.path.insert(0, str(Path('./src').resolve()))
        from my_module import processor  # then the processor module can be imported

        def run(data: str):
            input_data = json.loads(data)  # incoming JSON string is loaded as a dictionary

            result = processor.process_data(input_data)  # the process_data can be called to process the incoming data

            # the code below creates the formatted output for the AI Inference Server
            if result is None:
                answer = {"ready": False, "output": None}
            else:
                answer = {"ready": True, "output": json.dumps(result)}

            return answer
        ```

        Args:
            entrypoint (str): Name of the new entrypoint script to be copied

        """
        self.is_valid = False

        if not any(key.name for key, value in self.resources.items() if key.name == entrypoint and value == '.'):
            raise AssertionError("Entrypoint must be added as resource to the root directory before setting up as entrypoint.")

        self.entrypoint = Path(entrypoint)

    def add_resources(self, base_dir: os.PathLike, resources: Union[os.PathLike, list]):
        """
        Adds files to a component.

        To make your file resources available on the AI Inference Server you need to add them to the package resources.
        These resources can be Python or config files, serialized ML models or reference data.
        They are then available on path {component_root}/{resources} in the runtime environment.
        When saving the package they will be copied from {base_dir}/{resources} into the package.
        Files in '__pycache__' folders will be excluded.
        Until version 2.3.0 of AI SDK hidden files and folders (starting with '.') are also excluded.

        Args:
            base_dir (path-like): Root folder of your code from which the resources are referred
            resources (os.PathLike or List): A single path or list of relative paths to resource files

        """
        self.is_valid = False

        base_dir = Path(base_dir).resolve().absolute()
        if not base_dir.is_dir():
            raise AssertionError(f"Parameter 'base_dir' must be a directory and available in path {base_dir}.")
        resources = resources if type(resources) is list else [resources]

        for resource in resources:
            self._add_resource(base_dir, resource)

    def _add_resource(self, base_dir: Path, resource: os.PathLike):
        self.is_valid = False
        if Path(resource).is_absolute() or '..' in resource:
            raise AssertionError("The resource path must be relative and cannot contain '/../' elements.")

        resource_path = base_dir / resource

        if resource_path.is_file():
            self._add_resource_file(base_dir, resource_path)
            return

        if resource_path.is_dir():
            for glob_path in resource_path.rglob("*"):
                if glob_path.is_file():
                    self._add_resource_file(base_dir, glob_path)
            return

        raise AssertionError(f"Specified resource is not a file or directory: '{resource}'")

    def _add_resource_file(self, base_dir: Path, resource_path: Path):
        self.is_valid = False
        for parent in resource_path.parents:
            if parent.name == '__pycache__':
                return

        if resource_path in self.resources.keys():
            _logger.warning(f"Resource '{resource_path}' is already added to target directory '{self.resources[resource_path]}'")
            return

        self.resources[resource_path] = f"{resource_path.parent.relative_to(base_dir)}"

    def add_dependencies(self, packages: list):
        """
        Adds required dependencies for the Python code.

        The list must contain the name of the Python packages or tuples in the form of (name, version) which are required to execute the component on AI Inference Server.
        The method will search for the packages for the target platform and collect their transitive dependencies as well.
        Packages that are distributed only in source format can be added too, but only if they are pure Python packages.

        Args:
            packages (list): Can be a list of strings (name) or a list of tuples (name, version) of the required packages for component execution
        """
        self.is_valid = False
        self.python_dependencies.add_dependencies(packages)

    def set_requirements(self, requirements_path: os.PathLike):
        """
        Reads the defined dependencies from the given `requirements.txt` file and creates a new dependency list. Previously added dependencies will be cleared.

        The file format must follow Python's requirements file format defined in PEP 508.
        It can contain URLs to additional repositories in the form of `--extra-index-url=my.repo.example.com`.

        Args:
            requirements_path (str): Path of the given `requirements.txt` file
        """
        self.is_valid = False
        self.python_dependencies.set_requirements(requirements_path)

    def set_pyproject_toml(self, pyproject_path: os.PathLike):
        """
        Reads the defined dependencies from the given `pyproject.toml` file and adds it to the requirements list.

        Only the dependencies defined in the `[project]` section will be added to the component.

        Args:
            pyproject_path (str): Path of the given `pyproject.toml` file
        """
        self.is_valid = False
        self.python_dependencies.set_pyproject_toml(pyproject_path)

    def add_python_packages(self, path: str) -> None:
        """
        Adds Python package(s) to the `PythonPackages.zip` file of the component.

        The `path` parameter can refer to either a `whl`, a `zip` or a `tar.gz` file.
        Zip files can be either a source distribution package or a collection of Python packages. Only pure Python source distributions are allowed.
        The dependency list of the component will be extended with the files added here, so that they will also get installed on the AI Inference Server.
        The method uses the `tempfile.tempdir` folder, so make sure that the folder is writeable.

        The wheel files must fulfill the requirements of the targeted device environment
        (e.g., the Python version must match the supported Python version of the targeted AI Inference Server, and the platform should be one of the supported ones too).

        Args:
            path (str): Path of the distribution file

        Examples:
            `component.add_python_packages('../resources/my_package-0.0.1-py3-none-any.wheel')`
                adds the wheel file to `PythonPackages.zip` and adds dictionary item `component.dependencies['my_package'] = '0.0.1'`

            `component.add_python_packages('../resources/inference-wheels.zip')`
                adds all the wheel files in the zip to `PythonPackages.zip` and `component.dependencies`
        """
        self.is_valid = False
        self.python_dependencies.add_python_packages(path)

    def set_parallel_steps(self, replicas):
        """
        Sets the number of parallel executors.

        This method configures how many instances of the component can be
        executed at the same time.
        The component must be suitable for parallel execution. The inputs arriving
        to the component will be processed by different instances in parallel,
        and these instances do not share their state (e.g. variables). Every
        instance is initialized separately and receives only a fraction of the inputs.
        AI Inference Server supports at most 8 parallel instances.```

        Args:
            replicas (int): Number of parallel executors. Default is 1.

        Raises:
            ValueError: if the given argument is not a positive integer.
        """
        self.is_valid = False
        if (not isinstance(replicas, int)) or replicas < 1:
            raise ValueError("Replica count must be a positive integer.")
        if 8 < replicas:
            _logger.warning("The current maximum of parallel executors is 8.")
        self._replicas = replicas

    def add_metric(self, name: str, desc: Optional[str] = None):
        """
        Adds a metric that will be automatically used as a pipeline output.

        Args:
            name (str): Name of the metric.
            desc (str): Description of the metric. (optional)
        """
        if "_" not in name:
            raise AssertionError("The metric name must contain at least one underscore")
        if self.metrics is None:
            self.metrics = {}
        if name in self.metrics:
            raise AssertionError(f"Metric '{name}' already exists")
        self.metrics[name] = {}
        if desc is not None:
            self.metrics[name]['desc'] = desc

    def delete_metric(self, name: str):
        """
        Remove a previously added metric.

        Args:
            name (str): Name of the metric to be deleted.
        """
        if name not in self.metrics:
            raise AssertionError(f"Component '{self.name}' has no metric '{name}'")
        self.metrics.pop(name)

    def _to_dict(self):
        component_dict = {
            **super()._to_dict(),
            'version': self.version,
            'entrypoint': f"./{self.entrypoint.name}",
            'hwType': 'CPU',
            'runtime': {
                'type': 'python',
                'version': self.python_version
            },
            'replicas': self._replicas
        }

        component_dict["outputType"] += [{
            'name': name,
            'type': 'String',
            'metric': True,
        } for name in self.metrics.keys()]

        return component_dict

    def enable_dependency_optimization(self):
        """
        Allows changing repository URLs to optimize the package size

        Allows the replacement of the `--index-url` argument during `pip download` to download
        CPU runtime optimized dependencies only. Enabling this optimization, the present
        `--index-url` will be prepended to the `--extra-index-url` list, and the Pytorch CPU only repository
        will be set as the `--index-url`.
        A warning message will be printed if the repository URL modification was necessary.
        Some dependencies have both CPU and GPU runtime
        versions, pytorch for example, but a `PythonComponent` can only run on CPU, so
        packaging the additional GPU runtime dependencies just enlarges the package size.
        If you want to run your model on GPU, convert it to an `ONNX` model and use it within a
        `GPURuntimeComponent`.
        """
        self.python_dependencies.enable_dependency_optimization()

    def disable_dependency_optimization(self):
        """
        Disables any modification to repository URLs

        Disables the replacement of the `--index-url` argument during `pip download`.
        This way all `--index-url` or `--extra-index-url` arguments will be preserved if they
        were present in the requirements.txt file.
        Some dependencies have both CPU and GPU runtime
        versions, pytorch for example, but a `PythonComponent` can only run on CPU, so
        packaging the additional GPU runtime dependencies just enlarges the package size.
        A warning message will be printed about the package size if this optimization is disabled and
        the dependency list contains GPU optimized dependencies.
        Disabling this optimization will not allow the component to run on GPU.
        If you want to run your model on GPU, convert it to an `ONNX` model and use it within a
        `GPURuntimeComponent`.
        """
        self.python_dependencies.disable_dependency_optimization()

    def validate(self):
        """
        Validates that the component is ready to be serialized and packaged as part of a pipeline.
        """
        if not self.is_valid:
            if self.entrypoint is None:
                raise AssertionError("Entrypoint must be defined")
            if not any(key.name for key, value in self.resources.items() if key.name == self.entrypoint.name and value == '.'):
                raise AssertionError("Entrypoint must be added as resource to the root directory before setting up as entrypoint.")

            if len(self.python_dependencies.dependencies) < 1:
                _logger.warning(f"WARNING! There are no dependencies defined for component '{self.name}'. Please make sure that all necessary dependencies have been added.")

            self.python_dependencies.validate()

            self.is_valid = True

        _logger.info(f"Component '{self.name}' is valid and ready to use.")

    def save(self, destination, validate=True):
        """
        Saves the component to a folder structure, so it can be used as part of a pipeline configuration package.
        Validation can be skipped by setting parameter `validate` to False.
        This is useful when the component is already validated and only intended to be saved.

        The component folder contains the following:

        - `requirements.txt` with a list of Python dependencies
        - Entry point script defined by the `entrypoint` attribute of the component
        - Extra files as added to the specified folders
        - `PythonPackages.zip` with the wheel binaries for the environment to be installed

        Args:
            destination (path-like): Target directory to which the component will be saved.
            validate (bool): With value True, triggers component validation. Defaults to True.
        """
        if validate:
            self.validate()

        folder_path = Path(destination) / self.name
        folder_path.mkdir(parents=True, exist_ok=True)

        for file_path in self.resources:
            dir_path = folder_path / self.resources[file_path]
            os.makedirs(dir_path, exist_ok=True)
            shutil.copy(file_path, dir_path / file_path.name)

        self.python_dependencies.save(folder_path)

