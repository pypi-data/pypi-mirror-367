import inspect
import re
from importlib.resources import open_binary

import pandas as pd
import yaml

from . import agriculture, industry, ppf, waste
from ._metadata import MetaData  # TODO
from .sample import create_sample


class IPCC:
    def __init__(self, _external_metadata=None, _ext_functions=None):
        self.waste = waste
        self.agriculture = agriculture
        self.industry = industry
        # self.ppf = ppf
        self._metadata = MetaData(
            external_metadata=_external_metadata, external_functions=_ext_functions
        )

    # TODO: when specifying sequence in yaml config, this needs revision
    @staticmethod
    def inspect(func):
        """Get the required parameters of a tier method.

        Argument
        --------
        func : function
            tier sequence of a volume, chapter

        Returns
        -------
        VALUE: list of str
            parameter names
        """
        s = inspect.getsource(func)
        parameters = list(set(re.findall('table="([a-z,_,A-Z,0-9,-]+)', s)))
        return parameters

    def get_metadata(self, volume, chapter, parameter):
        """Get the metadata of a parameter.

        Argument
        --------
        volume : string
            volume name
        chapter : string
            chapter name
        paramater : string
            parameter name

        Returns
        -------
        VALUE: dict
            metadata pointing to the source in the IPCC pdf documents
            (year, volume, chapter, page, equation)
        """
        # use metadata from import instead for yaml
        # with open_binary("bonsai_ipcc.data", "ipcc.datapackage.yaml") as fp:
        #    metadata = yaml.load(fp, Loader=yaml.Loader)
        # metadata = MetaData(external=self._external_metadata)
        metadata = self._metadata
        for k in range(len(metadata["resources"])):
            if (
                metadata["resources"][k]["path"]
                == f"{volume}/{chapter}/par_{parameter}.csv"
            ):
                d = metadata["resources"][k]
        try:
            return d
        except UnboundLocalError:
            raise KeyError(
                f"parameter '{parameter}' for volume '{volume}', chapter '{chapter}' not found in the metadata"
            )

    def create_sample(self, dfs, constraints=None):
        """Add sample to parameter tables.

        For parameter tables in which values are related and constraint, Dirichlet distribution is used for samples.
        For other parameter tables, sample is determined independently using the best fit distribution.

        Argument
        --------
        dfs : dict
            key is name of paramter, value is df
        constraints: dict
            key is name of parameter, value is dict with
                group_py: ["year", "region", "product"]
        size : int
            sample size

        Returns
        -------
        dict of dfs
            revised parameter tables with sample array
        """
        return create_sample(dfs, constraints=constraints)

    def search_metadata(self, keyword):
        """Get parameters that contain keyword in the description.

        Argument
        --------
        volume : string
            volume name
        chapter : string
            chapter name
        keyword : string
            keyword to search for

        Returns
        -------
        list of tuples
            (parameter name, description)
        """
        # use metadata from import instead for yaml
        # with open_binary("bonsai_ipcc.data", "ipcc.datapackage.yaml") as fp:
        #    metadata = yaml.load(fp, Loader=yaml.Loader)
        # metadata = MetaData(external=self._external_metadata)
        metadata = self._metadata
        name = []
        description = []
        volume = []
        chapter = []
        unit = []
        for k in range(len(metadata["resources"])):
            try:
                if keyword in metadata["resources"][k]["description"]:
                    name.append(metadata["resources"][k]["name"].removeprefix("par_"))
                    description.append(metadata["resources"][k]["description"])
                    path_string = metadata["resources"][k]["path"].split("/")
                    volume.append(path_string[0])
                    chapter.append(path_string[1])
                    unit.append(metadata["resources"][k]["unit"])
            except KeyError:
                pass
        data = {
            "name": name,
            "unit": unit,
            "description": description,
            "volume": volume,
            "chapter": chapter,
        }
        return pd.DataFrame(data)


class PPF(IPCC):
    def __init__(self):
        self.ppf_vol = ppf
