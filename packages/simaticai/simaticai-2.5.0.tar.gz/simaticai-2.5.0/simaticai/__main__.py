# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
AI Software Development Kit CLI
"""

import argparse

from pathlib import Path
from simaticai import deployment
from simaticai.testing.timeseries_stream import TimeSeriesStream
from simaticai.testing.vca_stream import VCAStream
from simaticai.testing.pipeline_runner import LocalPipelineRunner
from simaticai.testing.runner_config import RunnerConfig

_COMMANDS = ["convert_package", "create_delta_package", "run_pipeline"]


def _parse_runner_config(args: argparse.Namespace, argparser):
    if args.config_json is None:
        runner_config = RunnerConfig()
    else:
        runner_config = RunnerConfig.from_json(args.config_json)

    runner_config.data = args.data or runner_config.data
    if runner_config.data is None:
        argparser.error('--data  is required either as a command line argument or as a field in the configuration JSON.')
    else:
        runner_config.data = Path(runner_config.data)
    
    runner_config.test_dir = args.test_dir or runner_config.test_dir
    if runner_config.test_dir is None:
        runner_config.test_dir = None
    else:
        runner_config.test_dir = Path(runner_config.test_dir)
    
    if runner_config.data.is_file():

        data_stream = TimeSeriesStream(
            csv_path=runner_config.data,
            fields=runner_config.time_series_stream.fields,
            count=runner_config.time_series_stream.count,
            offset=runner_config.time_series_stream.offset,
            batch_size=runner_config.time_series_stream.batch_size
        )
    else:
        data_stream = VCAStream(
            data    = runner_config.data,
            variable_name   = runner_config.vca_stream.variable_name,
            image_format    = runner_config.vca_stream.image_format,
            filter  = runner_config.vca_stream.filter
        )

    return data_stream, runner_config

def _parse_args(arg_list: list[str] | None = None):
    argparser = argparse.ArgumentParser(prog='python -m simaticai', description="AI SDK command line interface.", add_help=True)
    cmd_parsers = argparser.add_subparsers(dest='command')

    parser_convert_package = cmd_parsers.add_parser('convert_package', help="Convert a Pipeline Configuration Package to an Edge Configuration Package that can be directly deployed.")
    parser_convert_package.add_argument('package_zip', help="""Path to the input package file.
    For "{path}/{name}_{version}.zip", the output file will be created as "{path}/{name}-edge_{version}.zip".
    If a file with such a name already exists, it is overwritten.""")

    parser_delta_package = cmd_parsers.add_parser('create_delta_package', help="Create a Delta Configuration Package that can be deployed onto the original pipeline on AI Inference Server.")
    parser_delta_package.add_argument('origin_package', help="Path to Origin Edge Package file.")
    parser_delta_package.add_argument('new_package', help="Path to New Edge Package file.")

    parser_run_pipeline = cmd_parsers.add_parser('run_pipeline', help="Run an edge pipeline package locally.")
    parser_run_pipeline.add_argument('package', help="Path to an Edge Package file.", default=None)
    parser_run_pipeline.add_argument("-c", "--config_json", type=str, help="A JSON configuration file that contains additional configuration for the data source.")

    parser_run_pipeline.add_argument('--data', help="Input data source", default=None)
    parser_run_pipeline.add_argument('--test_dir', help="Directory for the test environment", default=None)

    args = argparser.parse_args(arg_list)

    if args.command is None:
        argparser.error("No subcommand selected.")
    elif args.command not in _COMMANDS:
        argparser.error("Invalid subcommand.")

    return args, argparser

def main():
    args, argparser = _parse_args()

    match args.command:
        case "convert_package":
            target_zip = deployment.convert_package(args.package_zip)
            print(f"Package successfully converted and saved as '{target_zip}'")
        case "create_delta_package":
            target_zip = deployment.create_delta_package(args.origin_package, args.new_package)
            print(f"Delta package successfully created and saved as '{target_zip}'")
        case "run_pipeline":
            data_stream, runner_config = _parse_runner_config(args, argparser)

            with LocalPipelineRunner(
                Path(args.package),
                path=runner_config.test_dir,
                cleanup=runner_config.cleanup
            ) as runner:
                pipeline_output = runner.run_pipeline(data_stream)
                print("Pipeline output:")
                print(pipeline_output)

if __name__ == '__main__':
    main()
