import importlib
import inspect
import logging
import os
from importlib.resources import open_binary
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

ROOT_PATH = Path(os.path.dirname(__file__)).parent


class MetaData:
    def __init__(self, external_metadata=None, external_functions=None):
        with open_binary("bonsai_ipcc.data", "ipcc.datapackage.yaml") as fp:
            self.metadata = yaml.load(fp, Loader=yaml.Loader)

        all_funct = []
        ipcc_modules = [
            "bonsai_ipcc.agriculture.generic.elementary",
            "bonsai_ipcc.agriculture.livestock_manure.elementary",
            "bonsai_ipcc.agriculture.soils.elementary",
            "bonsai_ipcc.industry.chemical.elementary",
            "bonsai_ipcc.industry.metal.elementary",
            "bonsai_ipcc.industry.mineral.elementary",
            "bonsai_ipcc.waste.biological.elementary",
            "bonsai_ipcc.waste.incineration.elementary",
            "bonsai_ipcc.waste.swd.elementary",
            "bonsai_ipcc.waste.waste_generation.elementary",
            "bonsai_ipcc.waste.wastewater.elementary",
        ]

        for m in ipcc_modules:
            module = importlib.import_module(m)
            members = inspect.getmembers(module, inspect.isfunction)
            all_funct.extend(members)

        if external_functions:
            self.functions = all_funct + external_functions
            self.external_functions = external_functions
        else:
            self.functions = all_funct

        self.external_metadata = external_metadata

        # Merge the 'resources' lists from both YAML files
        if self.external_metadata:
            merged_data = {
                "name": f"{external_metadata['name']}",  # Use name of the external
                "resources": self.metadata["resources"]
                + self.external_metadata["resources"],  # Extend the resources
            }
            self.metadata = merged_data
        else:
            pass

    def __getitem__(self, key):
        # Allow subscript access to the metadata dictionary
        return self.metadata[key]

    def __setitem__(self, key, value):
        # Allow setting values via subscript notation
        self.metadata[key] = value
