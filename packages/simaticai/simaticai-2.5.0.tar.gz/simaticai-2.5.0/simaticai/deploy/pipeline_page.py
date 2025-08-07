# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import logging
import sys
import os
from MarkupPy import markup
from pathlib import Path
from typing import Union

from simaticai.packaging.constants import README_HTML
from simaticai.deploy.component import Component
from simaticai.deploy.python_component import PythonComponent
from simaticai.deploy.pipeline_data import PipelineData

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

__all__ = ['_PipelinePage', 'save_readme_html']

class _PipelinePage(markup.page):

    def __init__(self, pipeline: PipelineData):
        super().__init__('strict_html', 'lower')

        self.twotags.append("section")
        self.init(
            title=f"{pipeline.name} ({pipeline.save_version})",
            doctype="<!DOCTYPE html>",
            charset="utf-8",
            lang="en")

        self.section()

        self.h1(f"Pipeline {pipeline.name} ({pipeline.save_version})")
        if pipeline.desc:
            self.p(pipeline.desc)
        self.html_generate_parameters(pipeline)
        self.html_generate_pipeline_inputs(pipeline)
        self.html_generate_pipeline_outputs(pipeline)
        self.html_generate_io_wiring(pipeline)
        self.html_generate_timeshifting(pipeline)

        for component in pipeline.components.values():
            self.html_generate_components(component)

        self.section.close()

    def html_generate_components(self, component: Component):
        self.hr()
        self.section()

        self.h1(f"{component.__class__.__name__} {component.name}")
        if component.desc:
            self.p(component.desc)
        self.html_generate_component_inputs(component)
        self.html_generate_component_outputs(component)
        self.html_generate_metrics(component)
        if issubclass(component.__class__, PythonComponent):
            self.html_generate_resources(component)
            self.html_generate_entrypoints(component)

        self.section.close()

    def html_generate_parameters(self, pipeline: PipelineData):
        if len(pipeline.parameters) > 0:
            self.strong("Parameters")
            self.ul()

            for name, parameter in pipeline.parameters.items():
                self.li()
                self.i(f"{name} ({parameter['type']}, default: '{parameter['defaultValue']}')")
                self.br()
                if parameter.get('desc') is not None:
                    self.span(parameter['desc'])
                self.li.close()

            self.ul.close()

    def html_generate_pipeline_inputs(self, pipeline: PipelineData):
        if len(pipeline.inputs) > 0:
            self.strong("Inputs")
            self.ul()

            for component, name in pipeline.inputs:
                input = pipeline.components[component].inputs[name]
                self.li()
                self.i(f"{name} ({input['type']})")
                self.br()
                if input.get('desc') is not None:
                    self.span(input['desc'])
                self.li.close()
            self.ul.close()

    def html_generate_pipeline_outputs(self, pipeline: PipelineData):
        if len(pipeline.outputs) > 0:
            self.strong("Outputs")
            self.ul()

            for component, name in pipeline.outputs:
                output = pipeline.components[component].outputs[name]
                self.li()
                self.i(f"{name} ({output['type']})")
                self.br()
                if output.get('desc') is not None:
                    self.span(output['desc'])
                self.li.close()

            self.ul.close()

    def html_generate_component_inputs(self, component: Component):
        self.strong("Inputs")
        self.ul()

        for name, input in component.inputs.items():
            self.li()
            self.i(f"{name} ({input['type']})")
            self.br()
            if input.get('desc') is not None:
                self.span(input['desc'])
            self.li.close()

        self.ul.close()

    def html_generate_component_outputs(self, component: Component):
        self.strong("Outputs")
        self.ul()

        for name, output in component.outputs.items():
            self.li()
            self.i(f"{name} ({output['type']})")
            self.br()
            if output.get('desc') is not None:
                self.span(output['desc'])
            self.li.close()

        self.ul.close()

    def html_generate_io_wiring(self, pipeline: PipelineData):
        if len(pipeline.wiring) > 0:
            self.strong("I/O Wiring")
            self.ul()

            for component, name in pipeline.inputs:
                self.li(f"{name} &#8594 {component}.{name}")
            for wire_hash in pipeline.wiring:
                self.li(wire_hash.replace("->", "&#8594"))
            for component, name in pipeline.outputs:
                self.li(f"{component}.{name} &#8594 {name}")

            self.ul.close()

    def html_generate_timeshifting(self, pipeline: PipelineData):
        if pipeline.periodicity is not None:
            self.strong("Timeshifting")
            self.ul()
            self.li(f"Periodicity: {pipeline.periodicity} ms")
            self.ul.close()

            if len(pipeline.timeshift_reference) > 0:
                self.strong("References")
                self.ul()
                for ref in pipeline.timeshift_reference:
                    self.li(ref)
                self.ul.close()

    def html_generate_resources(self, component: Component):
        if isinstance(component, PythonComponent) and component.resources is not None and len(component.resources) > 0:
            self.strong("Resources")
            self.ul()
            for path, base in component.resources.items():
                self.li(f"{base}/{path.name}".replace('./', ''))
            self.ul.close()

    def html_generate_entrypoints(self, component: Component):
        if isinstance(component, PythonComponent) and component.entrypoint is not None:
            self.strong("Entrypoint")
            self.ul()
            self.li(component.entrypoint.name)
            self.ul.close()

    def html_generate_metrics(self, component: Component):
        if isinstance(component, PythonComponent) and component.metrics is not None and len(component.metrics) > 0:
            self.strong("Metrics")
            self.ul()
            for name, metric in component.metrics.items():
                self.li()
                self.i(name)
                if metric.get('desc') is not None:
                    self.br()
                    self.span(metric['desc'])
                self.li.close()
            self.ul.close()

def save_readme_html(pipeline: PipelineData, destination: Union[str, os.PathLike]):
    """
    Saves a `README.html` in the `destination` folder that describes the pipeline.

    Args:
        destination (path-like): Path of the destination folder.
    """
    pipelinePage = _PipelinePage(pipeline)
    readme_html_path = Path(destination) / README_HTML
    readme_html_path.write_text(pipelinePage.__str__())

