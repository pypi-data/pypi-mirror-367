# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
This module provides a base class for creating and managing Docker containers
with Python virtual environments. It is designed to be used in a context where
Docker is available and the user has the necessary permissions to create and
manage containers.
"""
import logging
from pathlib import Path
import subprocess

logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class VesselBaseDocker:
    is_vessel: bool = False
    python_3_10: str = 'python'
    python_3_11: str = 'python'

    def __init__(self):
        if Path("/.ai_sdk_docker").is_file():
            self.is_vessel = True  # Check if running in a Docker container
            self.python_3_10 = 'python3.10'  # Set the Python executable for the container
            self.python_3_11 = 'python3.11'  # Set the Python executable for the container

    def _create_venv(self, path: str, version: str):
        """
        Creates a virtual environment in which the given component can run.

        Args:
            path (str): Path to the virtual environment.
            version (str): Python version to use for the virtual environment.
        """
        
        context_dir = Path(path) / ".venv"
        python_path = context_dir / "bin" / "python"

        match version:
            case "3.10":
                python = self.python_3_10
            case "3.11":
                python = self.python_3_11
            case _:
                python = self.python
        _logger.info(f"Creating virtual environment for Python '{version}' in '{path}/.venv' with Python {python}...")

        command = [
            python,
            "-m", "venv", str(context_dir),
            "--copies"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            _logger.error(f"Error creating virtual environment: {result.stderr}")
            raise RuntimeError(f"Error creating virtual environment: {result.stderr}")

        return context_dir.resolve(), python_path.resolve()
