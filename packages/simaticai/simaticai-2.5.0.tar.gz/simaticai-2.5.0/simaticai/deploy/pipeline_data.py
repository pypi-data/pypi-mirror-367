# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import sys
import uuid
import logging
from typing import Optional


logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class PipelineData:

    def __init__(self, name: str, version: Optional[str] = None, desc: str = ""):
        """
        A newly initialized `Pipeline` will contain no `Component` or wire, just its name and version will be set.
        The name and version will define together the name of the zip file when the package is saved.

        Args:
            name (str): Name of the package
            desc (str): Package description (optional)
            version (str): Version of the package
        """

        self.name = name
        self.desc = desc

        self.init_version = version  # initial version; used when version is not set in Pipeline.export() and save()
        self.save_version = version  # contains the version determined at exporting/saving
        self.package_id: Optional[uuid.UUID] = None

        self.author = 'AI SDK'

        self.components = {}
        self.wiring = {}
        self.parameters = {}

        self.periodicity = None
        self.timeshift_reference = []

        self.inputs = []
        self.outputs = []
        self.log_level = logging.INFO
