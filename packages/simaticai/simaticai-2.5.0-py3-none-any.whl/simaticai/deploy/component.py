# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

from dataclasses import dataclass
import logging
import re
import sys
from typing import Optional

from simaticai.packaging.constants import supported_types

__all__ = ['Component']

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_allowed_characters_in_names = re.compile('^[-a-zA-Z0-9_]+$')

class Component:
    """
    Base class for pipeline components, with name, description, and a list of inputs and outputs.

    A new component is created with the given name and an empty input and output list.

    Args:
        name (str): Name of the component
        desc (str): Optional description of the component
        inputs (dict): Dictionary of (name, type) pairs, which describe the input variables
        outputs (dict): Dictionary of (name, type) pairs, which describe the output variables
    """
    reserved_names = ["timestamp"]

    @dataclass
    class BatchInfo:
        """
        Batch information for the component.

        This attribute specifies whether the component can handle batch input or output data.
        When set to True, the component will receive data in the form of a list of dictionaries instead of a single dictionary.
        It is important to note that the input and output variables on the component should still be defined as if they are single variables.

        If the input of the pipeline is configured for batch processing, it is recommended not to configure timeshifting, as the list will have the same timestamp for all elements, potentially resulting in data loss.
        """
        inputBatch: bool = False
        outputBatch: bool = False

        def dict(self):
            return {
                'inputBatch': 'Yes' if self.inputBatch is True else 'No',
                'outputBatch': 'Yes' if self.outputBatch is True else 'No'
            }

    def __init__(self, name: str, desc: str = ""):
        """
        Creates a new component with the given name and an empty input and output list.

        Args:
            name (str): Name of the component.
            desc (str): Optional description of the component
        """

        if _allowed_characters_in_names.match(name) is None:
            raise AssertionError("Component name contains invalid character. The allowed characters are [-a-zA-Z0-9_].")
        self.name = name
        self.desc = desc
        self.inputs = {}
        self.outputs = {}

        self.batch = self.BatchInfo(False, False)

    def __repr__(self) -> str:
        text = f"[{self.__class__.__name__}] {self.name}\n"
        if self.desc != "":
            text += f"{self.desc}\n"
        if len(self.inputs) > 0:
            text += "\nComponent Inputs:\n"
            for name, input in self.inputs.items():
                text += f"> {name} ({input['type']}){': ' + input['desc'] if input.get('desc') is not None else ''}\n"
        if len(self.outputs) > 0:
            text += "\nComponent Outputs:\n"
            for name, output in self.outputs.items():
                text += f"< {name} ({output['type']}){': ' + output['desc'] if output.get('desc') is not None else ''}\n"
        return text

    def add_input(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Adds a new input to the component with its type.
        Name of the variables cannot be reserved name like 'timestamp'.
        Input variable 'timestamp' is a prebuilt key in the payload and its value contains the timestamp when the payload is created by AI Inference Server.

        Types supported by AI Inference Server version 1.6 are contained in the `type_dictionary`. Newer AI Inference server version may support additional types.
        In case the type is not known by the AI SDK, a warning message will be printed.
        The most frequently used types are
        - String:
            Typically used for data received from Databus
        - Object:
            Object type variables are designed to receive from Vision Connect or transfer images between components
        - Numeric scalar types:
            Typically used for data received from S7 Connector

        The example payload below shows the format of image received from VCA Connector
        ```python
            payload = { "image":
                {
                    "resolutionWidth": image.width,
                    "resolutionHeight": image.height,
                    "mimeType": ["image/raw"],
                    "dataType": "uint8",
                    "channelsPerPixel": 3,
                    "image": _swap_bytes(image.tobytes())
                }
            }
        ```
        Between components the format is the same format as the format of Object as an output.
        ```python
            "processedImage": {
                "metadata": json.dumps( {
                                "resolutionWidth": image.width,
                                "resolutionHeight": image.height
                                }
                            ),
                "bytes": image.tobytes()
            }
        ```

        Args:
            name (str): Name of the new input.
            _type (str): Type of the new input.
            desc (str): Description of the input. (optional)
        """
        if self.inputs is None:
            self.inputs = {}
        if name in self.inputs:
            raise AssertionError(f"Input '{name}' already exists.")
        if name.lower() in self.reserved_names:
            raise AssertionError(f"Input '{name}' is a reserved keyword.")

        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")

        self.inputs[name] = {
            "type": _type,
        }
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def change_input(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Changes one of the inputs of the component.

        Args:
            name (str): Name of the input to be changed.
            _type (str): New type of the input.
            desc (str): Description of the input. (optional)
        """
        if name not in self.inputs:
            raise AssertionError(f"There is no input with name '{name}'")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.inputs[name]['type'] = _type
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def delete_input(self, name: str):
        """
        Deletes an input from the component by name.
        Once the package has been created with the given component, it is recommended not to change the component directly.
        Instead, all necessary methods to change it are available through the package to avoid component inconsistencies.
        It is recommended to use `package.delete_input_wire(...)` with default parameter `with_input=True`.

        Args:
            name (str): Name of the input to be deleted.
        """
        if name not in self.inputs:
            raise AssertionError(f"Component '{self.name}' has no input '{name}'")
        self.inputs.pop(name)

    def add_output(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Adds a new output to the component.

        Types supported by AI Inference Server version 1.6 are contained in the `type_dictionary`. Newer AI Inference server version may support additional types.
        In case the type is not known by the AI SDK, a warning message will be printed.
        The most frequently used types are
        - String:
            Typically used for data to be sent to Databus
        - Object:
            Typically used for images to be sent to ZMQ Connector
        - Numeric scalar types:
            Typically used for data sent to S7 Connector

        For outputs of type `Object` the entrypoint must return with a `dictionary` containing two fields, where one field has type `str` and the other field has type `bytes`.
        The example below shows the required format, assuming that 'image' is a PIL Image.
        ```python
            "processedImage": {
                "metadata": json.dumps( {
                                "resolutionWidth": image.width,
                                "resolutionHeight": image.height
                                }
                            ),
                "bytes": image.tobytes()
            }
        ```

        Args:
            name (str): Name of the new output.
            _type (str): Type of the new output.
            desc (str): Description of the output. (optional)
        """
        if self.outputs is None:
            self.outputs = {}
        if name in self.outputs:
            raise AssertionError(f"Output '{name}' already exists")
        if name.lower() in self.reserved_names:
            raise AssertionError(f"Output '{name}' is a reserved keyword.")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.outputs[name] = {
            "type": _type,
        }
        if desc is not None:
            self.outputs[name]['desc'] = desc

    def change_output(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Changes one of the outputs of the component.

        Args:
            name (str): Name of the output to be changed.
            _type (str): The new type of the output.
            desc (str): Description of the output. (optional)
        """
        if name not in self.outputs:
            raise AssertionError(f"There is no output with name '{name}'")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.outputs[name]['type'] = _type
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def delete_output(self, name: str):
        """
        Deletes an output from the component by name.
        Once the package has been created with the given component, it is recommended not to change the component directly.
        Instead, all necessary methods to change it are available through the package to avoid component inconsistencies.
        Deleting an output which is represented in any wire will cause package inconsistency.

        Args:
            name (str): Name of the output to be deleted.
        """
        if name not in self.outputs:
            raise AssertionError(f"Component '{self.name}' has no output '{name}'")
        self.outputs.pop(name)

    def _to_dict(self):
        inputs = []
        inputs += [{
            'name': name,
            'type': self.inputs[name]['type'],
        } for name in self.inputs]

        outputs = []
        outputs += [{
            'name': name,
            'type': self.outputs[name]['type'],
            'metric': False,
        } for name in self.outputs]

        return {
            'name': self.name,
            'description': self.desc,
            'batch': self.batch.dict(),
            'inputType': inputs,
            'outputType': outputs,
        }

    def validate(self):
        """
        Empty method for child classess to implement.
        """
        pass

    def save(self, destination, validate):
        """
        Empty method for child classess to implement.
        """
        pass
