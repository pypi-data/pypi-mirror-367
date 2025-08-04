import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import bonsai_ipcc

TEST_DATA_PATH = Path(os.path.dirname(__file__)) / "data/"

from bonsai_ipcc._sequence import Sequence
from bonsai_ipcc.industry.metal import elementary as elem
from bonsai_ipcc.industry.metal._data import concordance as conc
from bonsai_ipcc.industry.metal._data import dimension as dim
from bonsai_ipcc.industry.metal._data import parameter as par

bonsai_ipcc.industry.metal.dimension.agent_type = pd.DataFrame(
    {"code": ["a", "b"], "description": ["test a", "test b"]}
).set_index(["code"])

bonsai_ipcc.industry.metal.parameter.m_agent = pd.DataFrame(
    {
        "year": [2019, 2019, 2019, 2019, 2019],
        "region": ["DE", "DE", "DE", "IT", "DE"],
        "product": [
            "ferrosilicon_45perc_si",
            "silicon_metal",
            "ferrosilicon_45perc_si",
            "ferrosilicon_45perc_si",
            "ferrosilicon_45perc_si",
        ],
        "agent_type": ["a", "b", "b", "b", "b"],
        "property": ["def", "def", "def", "def", "max"],
        "value": [100.0, 50.0, 50.0, 50.0, 1000000.0],
        "unit": ["t/yr", "t/yr", "t/yr", "t/yr", "t/yr"],
    }
).set_index(["year", "region", "product", "agent_type", "property"])

bonsai_ipcc.industry.metal.parameter.ef_agent = pd.DataFrame(
    {
        "year": [2019, 2019, 2019, 2019],
        "region": ["DE", "DE", "IT", "IT"],
        "agent_type": ["a", "b", "a", "b"],
        "property": ["def", "def", "def", "def"],
        "value": [1.0, 2.0, 50.0, 50.0],
        "unit": ["t/t", "t/t", "t/t", "t/t"],
    }
).set_index(["year", "region", "agent_type", "property"])


def test_get_dimension_levels_one(
    tables=["m_agent", "ef_agent"],
    uncert="def",
    year=2019,
    region="DE",
    product="silicon_metal",
):

    seq = Sequence(dim, par, elem, conc, uncert="def")
    l = seq.get_dimension_levels(year, region, product, uncert=uncert, table=tables[0])

    value = 0.0
    for a in l:
        seq.read_parameter(
            name=tables[0],
            table=tables[0],
            coords=[year, region, product, a],
        )
        seq.read_parameter(
            name=tables[1],
            table=tables[1],
            coords=[year, region, a],
        )
        value += seq.elementary.co2_in_agent_tier2_(
            m=seq.step.m_agent.value, ef=seq.step.ef_agent.value
        )
    assert l == ["b"]
    assert value == 100.0


def test_get_dimension_levels_multiple(
    tables=["m_agent", "ef_agent"],
    uncert="def",
    year=2019,
    region="DE",
    product="ferrosilicon_45perc_si",
):

    seq = Sequence(dim, par, elem, conc, uncert="def")
    l = seq.get_dimension_levels(year, region, product, uncert=uncert, table=tables[0])

    value = 0.0
    for a in l:
        seq.read_parameter(
            name=tables[0],
            table=tables[0],
            coords=[year, region, product, a],
        )
        seq.read_parameter(
            name=tables[1],
            table=tables[1],
            coords=[year, region, a],
        )
        value += seq.elementary.co2_in_agent_tier2_(
            m=seq.step.m_agent.value, ef=seq.step.ef_agent.value
        )
    assert l == ["a", "b"]
    assert value == 200.0


def test_metadata(volume="industry", chapter="chemical", parameter="pp_i"):
    test_obj = bonsai_ipcc.IPCC()
    par_metadata = test_obj.get_metadata(
        volume=volume, chapter=chapter, parameter=parameter
    )
    assert par_metadata["name"] == f"par_{parameter}"


def test_to_frames_bonsai():
    my_ipcc = bonsai_ipcc.IPCC()

    # Mock data for fa_i_k (ensure it matches the expected structure)
    d = {
        "year": [2006, 2006, 2006, 2006, 2006, 2006, 2006, 2006, 2006, 2006],
        "region": ["GB"] * 10,
        "activity": ["sc"] * 10,
        "product": ["ethylene"] * 10,
        "feedstocktype": ["gas_oil"] * 5 + ["naphtha"] * 5,
        "property": [
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
        ],
        "value": [10000, 1000, 110000, 0.0, np.inf, 1, 0.9, 1.1, 0.0, np.inf],
        "unit": ["t/year"] * 10,
    }

    # Create the fa_i_k DataFrame and set the multi-index
    fa_i_k = pd.DataFrame(d).set_index(
        ["year", "region", "activity", "product", "feedstocktype", "property"]
    )

    # Set the parameter fa_i_k in the IPCC object
    my_ipcc.industry.chemical.parameter.fa_i_k = fa_i_k

    # Run the tier1_co2_fa function and check the frames
    s = my_ipcc.industry.chemical.sequence.tier1_co2_fa(
        year=2006, region="GB", product="ethylene", activity="sc", uncertainty="def"
    )

    # Convert to frames (bonsai format) and validate the output
    df = s.to_frames(bonsai="uncertainty")
    assert df["bonsai"]["use"].loc[0]["product"] == "gas_oil"
    assert df["bonsai"]["use"].loc[1]["product"] == "naphtha"
    assert df["bonsai"]["use"].loc[0]["value"] == 10000.0
    assert df["bonsai"]["use"].loc[1]["value"] == 1.0
    assert pd.isna(df["bonsai"]["use"].loc[0]["standard_deviation"]) == True
    assert pd.isna(df["bonsai"]["use"].loc[1]["standard_deviation"]) == True
    assert df["bonsai"]["transf_coeff"].loc[0]["output_product"] == "ethylene"
    assert df["bonsai"]["transf_coeff"].loc[1]["output_product"] == "ethylene"
    assert df["bonsai"]["transf_coeff"].loc[0]["input_product"] == "gas_oil"
    assert df["bonsai"]["transf_coeff"].loc[1]["input_product"] == "naphtha"


def test_to_frames_bonsai_montecarlo():
    my_ipcc = bonsai_ipcc.IPCC()

    # Mock data for fa_i_k (used for Monte Carlo testing)
    d = {
        "year": [2006] * 10,
        "region": ["GB"] * 10,
        "activity": ["sc"] * 10,
        "product": ["ethylene"] * 10,
        "feedstocktype": ["gas_oil"] * 5 + ["naphtha"] * 5,
        "property": [
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
        ],
        "value": [2000, 1000, 3000, 0.0, np.inf, 1, 0.9, 1.1, 0.0, np.inf],
        "unit": ["t/year"] * 10,
    }

    # Create the fa_i_k DataFrame and set the multi-index
    fa_i_k = pd.DataFrame(d).set_index(
        ["year", "region", "activity", "product", "feedstocktype", "property"]
    )

    # Assign fa_i_k to the parameter in the IPCC object
    my_ipcc.industry.chemical.parameter.fa_i_k = fa_i_k

    # Run the tier1_co2_fa function to perform Monte Carlo simulation
    s = my_ipcc.industry.chemical.sequence.tier1_co2_fa(
        year=2006,
        region="GB",
        product="ethylene",
        activity="sc",
        uncertainty="monte_carlo",
    )

    # Convert the result to bonsai frames and validate output
    df = s.to_frames(bonsai="uncertainty")
    assert df["bonsai"]["use"].loc[0]["product"] == "gas_oil"
    assert df["bonsai"]["use"].loc[1]["product"] == "naphtha"
    assert abs((2000 - df["bonsai"]["use"].loc[0]["value"]) / 2000) <= 0.25
    assert abs((0.992 - df["bonsai"]["use"].loc[1]["value"]) / 0.992) <= 0.25
    assert pd.isna(df["bonsai"]["use"].loc[0]["standard_deviation"]) == False
    assert pd.isna(df["bonsai"]["use"].loc[1]["standard_deviation"]) == False
    assert (
        isinstance(
            df["bonsai"]["transf_coeff"].loc[0]["confidence_interval_95min"], float
        )
        == True
    )
    assert (
        isinstance(
            df["bonsai"]["transf_coeff"].loc[1]["confidence_interval_95min"], float
        )
        == True
    )


def test_to_frames_bonsai_samples():
    my_ipcc = bonsai_ipcc.IPCC()

    # Mock data for fa_i_k (used for Monte Carlo testing)
    d = {
        "year": [2006] * 10,
        "region": ["GB"] * 10,
        "activity": ["sc"] * 10,
        "product": ["ethylene"] * 10,
        "feedstocktype": ["gas_oil"] * 5 + ["naphtha"] * 5,
        "property": [
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
            "def",
            "min",
            "max",
            "abs_min",
            "abs_max",
        ],
        "value": [2000, 1000, 3000, 0.0, np.inf, 1, 0.9, 1.1, 0.0, np.inf],
        "unit": ["t/year"] * 10,
    }

    # Create the fa_i_k DataFrame and set the multi-index
    fa_i_k = pd.DataFrame(d).set_index(
        ["year", "region", "activity", "product", "feedstocktype", "property"]
    )

    # Assign fa_i_k to the parameter in the IPCC object
    my_ipcc.industry.chemical.parameter.fa_i_k = fa_i_k

    # Run the tier1_co2_fa function to perform Monte Carlo simulation
    s = my_ipcc.industry.chemical.sequence.tier1_co2_fa(
        year=2006,
        region="GB",
        product="ethylene",
        activity="sc",
        uncertainty="monte_carlo",
    )
    # Convert the result to bonsai frames and validate output
    df = s.to_frames(bonsai="samples")
    assert isinstance(df["bonsai"]["use"], pd.DataFrame) == True
    # assert isinstance(df["bonsai"]["use"].loc[0]["samples"], np.array) == True
    assert len(df["bonsai"]["use"].loc[0]["samples"]) == 1000


# def test_to_frames_emissions():
#    my_ipcc = bonsai_ipcc.IPCC()
#
#    d = {
#        "year": [2010, 2010, 2010, 2010, 2010, 2009, 2009, 2009, 2009, 2009],
#        "region": ["BG", "BG", "BG", "BG", "BG", "BG", "BG", "BG", "BG", "BG"],
#        "property": [
#            "def",
#            "min",
#            "max",
#            "abs_min",
#            "abs_max",
#            "def",
#            "min",
#            "max",
#            "abs_min",
#            "abs_max",
#        ],
#        "value": [
#            62940432.0,
#            61996325.52,
#            63884538.48,
#            0.0,
#            np.inf,
#            62940432.0,
#            61996325.52,
#            63884538.48,
#            0.0,
#            np.inf,
#        ],
#        "unit": [
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#            "cap/yr",
#        ],
#    }
#    urb_pop = pd.DataFrame(d).set_index(["year", "region", "property"])
#
#    my_ipcc.waste.swd.parameter.urb_population = urb_pop
#    my_ipcc.waste.incineration.parameter.urb_population = urb_pop
#
#    s = my_ipcc.waste.swd.sequence.tier1_ch4_prospective(
#        year=2010,
#        prospective_years=3,
#        region="BG",
#        product="msw_food",
#        activity="uncharacterised",
#        uncertainty="def",
#    )
#
#    df = s.to_frames(bonsai=True)
#
#    assert df["bonsai"]["emission"]["year_emission"].to_list() == [2011, 2012, 2013]
