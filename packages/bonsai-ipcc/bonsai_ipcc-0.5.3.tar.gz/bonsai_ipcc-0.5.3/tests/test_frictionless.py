import glob
import os
from importlib.resources import files, open_binary

import pytest
import yaml
from frictionless import validate

source = files("bonsai_ipcc.data")
metadatapath = source.joinpath("ipcc.datapackage.yaml")


def test_datapackage():
    report = validate(metadatapath)
    assert report.valid == True


def test_missing_metadata():
    """Test if all csv files of the data folder are included in the metadata."""
    get_paths = glob.glob(str(source.joinpath("**/*.csv")), recursive=True)

    all_expected_files = []
    for path in get_paths:
        all_expected_files.append(path.split(os.sep)[-1])

    with open_binary("bonsai_ipcc.data", "ipcc.datapackage.yaml") as fp:
        metadata = yaml.load(fp, Loader=yaml.Loader)
        all_metadata_files = []
        for k in range(len(metadata["resources"])):
            file_name = metadata["resources"][k]["path"]
            all_metadata_files.append(file_name)

    for file in all_expected_files:
        is_included = any(file in s for s in all_metadata_files)
        if is_included == False:
            raise KeyError(
                f"file '{file}' is not described in the 'ipcc.datapackage.yaml' metadata"
            )
