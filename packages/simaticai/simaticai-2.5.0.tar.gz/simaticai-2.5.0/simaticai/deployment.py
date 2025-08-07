# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Packaging ML models for deployment on the AI Inference Server.

The AI SDK offers the functionality to create a pipeline configuration package and wrap trained models, which can be converted to an
edge configuration package and then uploaded and run on an AI Inference Server on an Industrial Edge device.

From a deployment perspective, the inference pipeline can consist of one or more components. This is independent of the logical structure of
the inference pipeline. For example, a typical time series pipeline that consists of multiple Scikit Learn pipeline elements can be packaged
into a single pipeline component, which includes both a feature extractor and a classifier. Alternatively, you can deploy the same pipeline
split into two components, one for the feature extractor and another for the classifier.

To keep things simple and less error-prone, a pipeline should have as few components as possible.
In many cases, a single component will be sufficient.
However, there might be reasons why you might consider using separate components, such as:

- You need a different Python environment for different parts of your processing, e.g., you have components requiring conflicting package versions.
- You want to exploit parallelism between components without implementing multithreading.
- You want to modularize and build your pipeline from a pool of component variants, which you can combine flexibly.

The AI SDK allows you to create pipeline components implemented in Python and compose linear pipelines of one or multiple of such components.
The API is designed to anticipate future possible types of components that might be based on a different technology than Python, e.g. ONNX or
native TensorFlow Serving. Currently, only Python is supported.

For a comprehensive overview on how to package ML models in the context of a machine learning workflow, we recommend you refer to
the AI SDK User Manual, especially the chapter concerning packaging models into an inference pipeline. We also recommend you
follow the project templates for the AI SDK, which provide packaging notebooks as examples, and where source code and
saved trained models are organized into a given folder structure.

"""

import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import yaml

from simaticai.deploy.component import Component
from simaticai.deploy.python_component import PythonComponent, python_version_validator
from simaticai.deploy.gpuruntime_component import GPURuntimeComponent, _validate_gpuruntime_config
from simaticai.deploy.pipeline import (
    Pipeline, convert_package,
    _validate_with_schema, _generate_runtime_config,
    _package_component, _package_component_dependencies
)

from simaticai.helpers import pep508, yaml_helper, calc_sha, model_config
from simaticai.packaging.constants import PIPELINE_CONFIG, PYTHON_PACKAGES_ZIP, PYTHON_PACKAGES


logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_version_matcher = re.compile('Version: ([^ ]+).*')
_transitive_matcher = re.compile('Requires: (.+)')

__all__ = [
    'Component',
    'PythonComponent',
    'GPURuntimeComponent',
    'Pipeline',
    'convert_package',
    'create_delta_package',
    'python_version_validator',
    'model_config',
    '_package_component',
    '_package_component_dependencies',
    '_generate_runtime_config',
    '_validate_with_schema',
    '_get_pipeline_info',
    '_validate_delta_package_inputs',
    '_change_pipeline_config',
    '_extract_edge_package',
    '_copy_file',
    '_zip_delta_package',
    '_validate_gpuruntime_config',
    'find_dependencies',
]


def find_dependencies(name: str, dependencies: dict):
    """
    @Deprecated, reason: uses 'pip show' which only works for installed packages on the current platform.

    Collects all dependencies of the Python module given with its `name` in the current Python environment.

    All inherited dependencies will be added to the `dependencies` dictionary with the installed version of the module.
    The method executes an OS command like `python -m pip show scikit-learn`.

    Args:
        name (str): Name of the Python module to be searched through for its dependencies.
        dependencies (dict): Dictionary to collect the dependencies with the module name as key, and the installed version as value.

    Returns:
        dict: The `dependencies` dictionary with the collected module names and versions.
    """

    cmd_line = [sys.executable, '-m', 'pip', 'show', name]
    result = subprocess.run(cmd_line, stdout=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Dependency {name} is not found and cannot be added.")
        return dependencies

    version = None
    for line in result.stdout.splitlines():

        version_matches = _version_matcher.match(line)
        if version_matches:
            version = version_matches.groups()[0].strip()

        transitive_matches = _transitive_matcher.match(line)
        if transitive_matches:
            transitives = transitive_matches.groups()[0].split(", ")
            for dependency in transitives:
                if dependency not in dependencies:
                    find_dependencies(dependency, dependencies)

    if name not in dependencies:
        spec = pep508.Spec(name, [], [('==', version)] if version else [], None)
        dependencies[name] = spec
        print("Found:", spec)
    return dependencies


def _get_pipeline_info(pipeline_config: str):
    pipeline_config = yaml_helper.read_yaml(pipeline_config)
    pipeline_info = pipeline_config["dataFlowPipelineInfo"]
    pipeline_info["packageType"] = pipeline_config.get("packageType", "full")
    pipeline_info["originVersion"] = pipeline_config.get("originVersion", None)
    return pipeline_info


def _validate_delta_package_inputs(origin_package_info: dict, new_package_info: dict):
    if origin_package_info["packageType"] == "delta" or new_package_info["packageType"] == "delta":
        raise AssertionError("Neither of the packages can be delta package!")

    if origin_package_info["projectName"] != new_package_info["projectName"]:
        raise AssertionError("The new edge package must have the same name as the origin edge package!")

    if origin_package_info["dataFlowPipelineVersion"] == new_package_info["dataFlowPipelineVersion"]:
        raise AssertionError("The new edge package can not have the same version as the origin edge package!")


def _change_pipeline_config(config_path: str, origin_package_version: str):
    data = yaml_helper.read_yaml(config_path)
    data["packageType"] = "delta"
    data["originVersion"] = origin_package_version
    with open(config_path, "w") as f:
        yaml.dump(data, f)


def _extract_edge_package(edge_package_zip_path: str, path_to_extract: Path):
    zipfile.ZipFile(edge_package_zip_path).extractall(path_to_extract)
    for f in path_to_extract.rglob("*.zip"):
        component_path = path_to_extract / "components" / f.stem
        packages = Path(component_path, PYTHON_PACKAGES_ZIP)

        zipfile.ZipFile(f).extractall(component_path)
        if packages.is_file():
            zipfile.ZipFile(component_path / PYTHON_PACKAGES_ZIP).extractall(component_path / PYTHON_PACKAGES)
            os.remove(packages)
        os.remove(f)
    return path_to_extract


def _copy_file(file_path: Path, from_dir: Path, to_dir: Path):
    new_path = to_dir / file_path.relative_to(from_dir)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(file_path, to_dir / file_path.relative_to(from_dir))


def create_delta_package(origin_edge_package_zip_path: str, new_edge_package_zip_path: str):
    """
    Creates a Delta Edge Configuration Package from two given Edge Configuration Packages.
    The created Delta Configuration Package is applicable to import into AI Inference Server,
    if the Original Edge Configuration Package is already imported there.
    The Delta Configuration Package only contains the additions and modifications
    in the New Edge Configuration Package compared to the Original one.
    That also means that no file deletion is possible in a deployed pipeline via this option.
    Please make sure that both of the given zip files come from a trusted source!

    Usage:
    ~~~python
    delta_package_path = deployment.create_delta_package('Edge-Config-edge-1.0.0.zip', 'Edge-Config-edge-1.1.0.zip')
    ~~~

    This method can be used from the command line, too.
    ```
    python -m simaticai create_delta_package <origin_package.zip> <modified_package.zip>
    ```

    Once the package is calculated, you will have an `Edge-Config-edge-delta-1.1.0.zip` file beside the updated package zip file.
    <ul>This package will contain
    <li><ul>the three configuration file for the package;
        <li>pipeline_config.yml</li>
        <li>runtime_config.yml</li>
        <li>datalink_metadata.yml</li>
    </li></ul>
    <li>the newly added files,</li>
    <li>and the updated files.</li>
    </ul>

    The package will not contain any information on the deleted files and they will be copied from the original pipeline.

    **Caution!**
    *If you change the version of a component in the pipeline, the delta package will contain all the files of the component because AI Inference Server identifies
    a component with a different version as a different component!*

    Args:
        origin_edge_package_zip_path (str): Path to the origin edge configuration package zip file.
        new_edge_package_zip_path (str): Path to the new edge configuration package zip file.

    Returns:
        os.PathLike: The path of the created delta edge package zip file.

    Raises:

        AssertionError:
            When:
            - either of the given edge packages is a delta package or
            - the names of the given edge packages differ or
            - the versions of the given edge packages are equal.
    """

    workdir = Path(tempfile.mkdtemp(prefix="aisdk_deltapack-"))
    delta_dir  = Path(workdir / "delta")
    delta_dir.mkdir(parents=True)

    origin_dir = _extract_edge_package(origin_edge_package_zip_path, Path(workdir / "orig"))
    new_dir    = _extract_edge_package(new_edge_package_zip_path, Path(workdir / "new"))

    origin_package_info = _get_pipeline_info(origin_dir / PIPELINE_CONFIG)
    new_package_info = _get_pipeline_info(new_dir / PIPELINE_CONFIG)

    _validate_delta_package_inputs(origin_package_info, new_package_info)

    files_in_new_package = new_dir.rglob("*")
    for f in files_in_new_package:
        if f.is_dir():
            continue
        orig_file_path = origin_dir / f.relative_to(new_dir)
        if not orig_file_path.exists():
            _copy_file(f, new_dir, delta_dir)
        else:
            checksum_original = calc_sha(orig_file_path)
            checksum_new = calc_sha(f)
            if checksum_original != checksum_new:
                _copy_file(f, new_dir, delta_dir)

    _change_pipeline_config(delta_dir / PIPELINE_CONFIG, origin_package_info["dataFlowPipelineVersion"])

    new_edge_package_zip_path = Path(new_edge_package_zip_path)
    delta_path = _zip_delta_package(delta_dir, new_edge_package_zip_path)

    shutil.rmtree(workdir, ignore_errors=True)
    return Path(delta_path)


def _zip_delta_package(delta_dir: Path, new_package_path: Path):
    target_folder = new_package_path.parent
    splitted_name = str(new_package_path.stem).split("_")
    target_name = "_".join(splitted_name[:-1]) + "_delta_" + "".join(splitted_name[-1:])

    for dir in Path(delta_dir / "components").glob("*"):
        if Path(dir / PYTHON_PACKAGES).is_dir():
            shutil.make_archive(dir / PYTHON_PACKAGES, "zip", dir / PYTHON_PACKAGES)
            shutil.rmtree(dir / PYTHON_PACKAGES)
        shutil.make_archive(dir, "zip", dir)
        shutil.rmtree(dir)

    delta_path = shutil.make_archive(target_folder / target_name, "zip", delta_dir)
    return delta_path
