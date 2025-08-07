# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.
"""
RunnerConfig module and class is responsible to handle the configuration json.  
An instance of RunnerConfig class is being used to setup a LocalPipelineRunner with the required parameters.
"""

from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from logging import getLogger

logger = getLogger(__name__)

@dataclass
class TimeSeriesStreamConfig:
    """
    TimeSeriesStreamConfig is a configuration class used to manage settings for the time series stream.
    Attributes:
        fields (list): List of fields to be included in the time series stream. Defaults to None.
        count (int): Number of records to be included in the time series stream. Defaults to None.
        offset (int): Offset to be applied in the time series stream. Defaults to None.
        batch_size (int): Size of the batch to be used in the time series stream. Defaults to None.
    """
    fields: list = field(default=None)
    count: int = field(default=None)
    offset: int = field(default=None)
    batch_size: int = field(default=None)

@dataclass
class VCAStreamConfig:
    """
    VCAStreamConfig is a configuration class used to manage settings for the VCA stream.
    Attributes:
        variable_name (str): Name of the variable to be used in the VCA stream. Defaults to None.
        image_format (str): Format of the images to be used in the VCA stream. Defaults to None.
        filter (str): Filter to be applied in the VCA stream. Defaults to None.
    """
    variable_name: str = field(default=None)
    image_format: str = field(default=None)
    filter: str = field(default=None)

@dataclass
class RunnerConfig:
    """
    RunnerConfig is a configuration class used to manage settings for running tests and streams.
    Attributes:
        data (PathLike): Path to the data file or directory. Defaults to None.
        test_dir (PathLike): Path to the test directory. Defaults to None.
        cleanup (bool): Indicates whether to clean up resources after execution. Defaults to True.
        time_series_stream (TimeSeriesStreamConfig): Configuration for the time series stream.
        vca_stream (VCAStreamConfig): Configuration for the VCA stream.
    Methods:
        __post_init__():
            Converts `data` and `test_dir` attributes to `Path` objects if they are not None.
        __dict__():
            Returns a dictionary representation of the configuration, including nested stream configurations.
        from_json(config_path: PathLike | str) -> RunnerConfig:
            Creates a `RunnerConfig` instance from a JSON configuration file.
            Args:
                config_path (PathLike | str): Path to the JSON configuration file.
            Returns:
                RunnerConfig: An instance of the `RunnerConfig` class populated with values from the JSON file.
            Exceptions:
                - Logs a warning and returns a default `RunnerConfig` instance if the file is not found.
                - Logs a warning and returns a default `RunnerConfig` instance if the file is not a valid JSON.
                - Logs a warning and returns a default `RunnerConfig` instance if any other error occurs during file reading.

    """
    data: PathLike = field(default=None)
    test_dir: PathLike = field(default=None)
    cleanup: bool = field(default=True)
    time_series_stream: TimeSeriesStreamConfig = field(default_factory=TimeSeriesStreamConfig)
    vca_stream: VCAStreamConfig = field(default_factory=VCAStreamConfig)

    def __post_init__(self):
        if self.data is not None:
            self.data = Path(self.data)
        if self.test_dir is not None:
            self.test_dir = Path(self.test_dir)
    
    @property
    def __dict__(self):
        return {
            "data": self.data,
            "test_dir": self.test_dir,
            "cleanup": self.cleanup,
            "TimeSeriesStream": {
                "fields": self.time_series_stream.fields,
                "count": self.time_series_stream.count,
                "offset": self.time_series_stream.offset,
                "batch_size": self.time_series_stream.batch_size
            },
            "VCAStream": {
                "variable_name": self.vca_stream.variable_name,
                "image_format": self.vca_stream.image_format,
                "filter": self.vca_stream.filter
            }
        }

    @classmethod
    def from_json(cls, config_path: PathLike | str):
        import json

        try:
            config_path = Path(config_path)
            with open(config_path, 'r') as file:
                json_config = json.load(file)

        except FileNotFoundError:
            logger.warning(f"Configuration file {config_path} does not exist.")
            return cls()
        except json.JSONDecodeError:
            logger.warning(f"Configuration file {config_path} is not a valid JSON.")
            return cls()
        except Exception as e:
            logger.warning(f"An error occurred while reading the configuration file {config_path}: {e}")
            return cls()
        
        data = json_config.get('data')
        test_dir = json_config.get('test_dir')
        cleanup = json_config.get('cleanup', True)
        
        time_series_stream = TimeSeriesStreamConfig(
            fields=json_config.get('TimeSeriesStream', {}).get('fields'),
            count=json_config.get('TimeSeriesStream', {}).get('count'),
            offset=json_config.get('TimeSeriesStream', {}).get('offset'),
            batch_size=json_config.get('TimeSeriesStream', {}).get('batch_size')
        )
        
        vca_stream = VCAStreamConfig(
            variable_name=json_config.get('VCAStream', {}).get('variable_name'),
            image_format=json_config.get('VCAStream', {}).get('image_format'),
            filter=json_config.get('VCAStream', {}).get('filter')
        )
        return cls(
            data=data,
            test_dir=test_dir,
            cleanup=cleanup,
            time_series_stream=time_series_stream,
            vca_stream=vca_stream,
        )
