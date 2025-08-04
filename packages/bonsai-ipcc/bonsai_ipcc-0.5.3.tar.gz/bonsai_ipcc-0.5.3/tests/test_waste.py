import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

TEST_DATA_PATH = Path(os.path.dirname(__file__)).parent / "tests/data/"

from bonsai_ipcc import IPCC
from bonsai_ipcc.waste.swd import elementary as elem


class IncTestDataDE:
    def __init__(self):
        # Set up all the pandas DataFrames needed for tests
        # urban population
        d = {
            "year": [2010, 2010, 2010, 2010, 2010, 2011],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE"],
            "property": ["def", "min", "max", "abs_min", "abs_max", "sample"],
            "value": [
                62940432.0,
                61996325.52,
                63884538.48,
                0.0,
                np.inf,
                np.array([62940432.0, 72940432.0, 82940432.0, 65540432.0]),
            ],
            "unit": [
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
            ],
        }
        self.urb_pop = pd.DataFrame(d).set_index(["year", "region", "property"])

        # GDP
        d = {
            "year": [2010, 2010, 2010, 2010, 2010, 2011],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE"],
            "property": ["def", "min", "max", "abs_min", "abs_max", "sample"],
            "value": [
                34000000.0,
                34000000.0,
                34000000.0,
                0.0,
                np.inf,
                np.array([38000000.0, 36000000.0, 39000000.0, 32000000.0]),
            ],
            "unit": [
                "MUSD/yr",
                "MUSD/yr",
                "MUSD/yr",
                "MUSD/yr",
                "MUSD/yr",
                "MUSD/yr",
            ],
        }
        self.gdp = pd.DataFrame(d).set_index(["year", "region", "property"])

        # isw gen rate per GDP (waste from mining and construction is not considerred)
        d = {
            "year": [2010, 2010, 2010, 2010, 2010, 2011],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE"],
            "property": ["def", "min", "max", "abs_min", "abs_max", "sample"],
            "value": [
                0.0016,
                0.0016,
                0.0016,
                0.0016,
                np.inf,
                np.array([0.0012, 0.0018, 0.0018, 0.0012]),
            ],
            "unit": [
                "Gg/MUSD",
                "Gg/MUSD",
                "Gg/MUSD",
                "Gg/MUSD",
                "Gg/MUSD",
                "Gg/MUSD",
            ],
        }
        self.isw_gen_rate = pd.DataFrame(d).set_index(["year", "region", "property"])

        # isw type frac (data based on eurostat, isw_ equivilant to non-hazardous waste from nace industries)
        d = {
            "year": [
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2010,
                2011,
            ],
            "region": [
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
                "DE",
            ],
            "product": [
                "isw_rubber",
                "isw_rubber",
                "isw_rubber",
                "isw_rubber",
                "isw_rubber",
                "isw_food",
                "isw_food",
                "isw_food",
                "isw_food",
                "isw_food",
                "isw_construction",
                "isw_construction",
                "isw_construction",
                "isw_construction",
                "isw_construction",
                "isw_rubber",
            ],
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
                "def",
                "min",
                "max",
                "abs_min",
                "abs_max",
                "sample",
            ],
            "value": [
                0.07,
                0.07,
                0.07,
                0.07,
                np.inf,
                0.02,
                0.02,
                0.02,
                0.02,
                np.inf,
                0.65,
                0.65,
                0.65,
                0.65,
                np.inf,
                np.array([0.1, 0.07, 0.08, 0.05]),
            ],
            "unit": [
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
                "t/t",
            ],
        }
        self.isw_type_frac = pd.DataFrame(d).set_index(
            ["year", "region", "product", "property"]
        )


class SwdTestDataDE:
    def __init__(self):
        # same data as in the IPCC waste model example
        d = {
            "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "product": [
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
                "msw_food",
            ],
            "property": [
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
            ],
            "value": [
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
                2300.322,
            ],
            "unit": [
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
                "Gg/year",
            ],
        }
        self.sw = pd.DataFrame(d).set_index(["year", "region", "product", "property"])

        d = {
            "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "property": [
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
            ],
            "value": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "unit": [
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
            ],
        }
        self.msw_frac_to_swds = pd.DataFrame(d).set_index(
            ["year", "region", "property"]
        )

        d = {
            "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "activity": [
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
            ],
            "property": [
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
            ],
            "value": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "unit": [
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
            ],
        }
        self.swdstype_frac = pd.DataFrame(d).set_index(
            ["year", "region", "activity", "property"]
        )

        d = {
            "year": [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "activity": [
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
                "uncharacterised",
            ],
            "property": [
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
                "def",
            ],
            "value": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "unit": [
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
            ],
        }
        self.r_swd = pd.DataFrame(d).set_index(
            ["year", "region", "activity", "property"]
        )


class WwaterTestDataDE:
    def __init__(self):

        # urban population
        d = {
            "year": [2006, 2006, 2006, 2006, 2006, 2009, 2009, 2009, 2009, 2009],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
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
            "value": [
                80000000.0,
                80000000.0,
                80000000.0,
                0.0,
                np.inf,
                80000000.0,
                80000000.0,
                80000000.0,
                0.0,
                np.inf,
            ],
            "unit": [
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
                "cap/yr",
            ],
        }
        self.total_population = pd.DataFrame(d).set_index(
            ["year", "region", "property"]
        )

        d = {
            "year": [2006, 2006, 2006, 2006, 2006, 2009, 2009, 2009, 2009, 2009],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "activity": [
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
            ],
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
            "value": [
                1.0,
                1.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.0,
                1.0,
            ],
            "unit": [
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
                "kg/kg",
            ],
        }
        self.ww_per_tech = pd.DataFrame(d).set_index(
            ["year", "region", "activity", "property"]
        )

        d = {
            "year": [2006, 2006, 2006, 2006, 2006, 2009, 2009, 2009, 2009, 2009],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE", "DE"],
            "activity": [
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
                "coll_treat_aerob_centralised_primary",
            ],
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
            "value": [
                0.0,
                0.0,
                0.0,
                0.0,
                np.inf,
                0.0,
                0.0,
                0.0,
                0.0,
                np.inf,
            ],
            "unit": [
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
                "t/yr",
            ],
        }
        self.s_mass = pd.DataFrame(d).set_index(
            ["year", "region", "activity", "property"]
        )


@pytest.fixture
def inc_test_data_DE():
    return IncTestDataDE()


@pytest.fixture
def swd_test_data_DE():
    return SwdTestDataDE()


@pytest.fixture
def wwater_test_data_DE():
    return WwaterTestDataDE()


def test_msw_to_swds():
    obs = elem.msw_to_swds(
        urb_population=200, msw_gen_rate=0.5, msw_frac_to_swds=0.5, msw_type_frac=0.5
    )
    assert obs == 200 * 0.5 * 0.5 * 0.5


def test_C_balance():
    DDOCm = 100
    F = 0.5
    R = 0.1
    OX = 0.1

    CH4_gen = elem.ch4_generated(ddocm=DDOCm, f=F)
    CH4 = elem.ch4_emissions(ch4_gen=CH4_gen, ox=OX, r=R)
    CO2_d = elem.co2_emissions_direct(ddocm=DDOCm, f=F)
    CO2_i = elem.co2_emissions_from_ch4(ddocm=DDOCm, f=F, ox=OX)

    obs = (
        CH4 * (12 / 16)  # Carbon in CH4 emissions
        + (CO2_d + CO2_i) * (12 / 44)  # Carbon in CO2 emissions
        + (CH4_gen * R) * (1 - OX) * 12 / 16  # Carbon in recovered CH4
    )
    expected = DDOCm

    assert obs == expected


def test_swd_tier2_CH4(swd_test_data_DE):
    test = IPCC()

    test.waste.swd.parameter.sw = swd_test_data_DE.sw

    test.waste.swd.parameter.msw_frac_to_swds = swd_test_data_DE.msw_frac_to_swds

    test.waste.swd.parameter.swdstype_frac = swd_test_data_DE.swdstype_frac

    test.waste.swd.parameter.r_swd = swd_test_data_DE.r_swd

    test.waste.swd.parameter.mcf.loc[("uncharacterised", "def"), "value"] = 0.705

    sequence = test.waste.swd.sequence.tier2_ch4(
        year=1959,
        region="DE",
        product="msw_food",
        wastemoisture="wet",
        past_years=9,
        activity="uncharacterised",
        uncertainty="def",
    )

    # read the expected result
    TEST_DF = pd.read_excel(
        TEST_DATA_PATH / "test_waste_CH4_food_waste.xlsx",
        sheet_name="Food",
        header=[13],
    ).drop(index=[0, 1, 2])

    assert (
        sequence.ch4_emissions.value
        == TEST_DF.loc[TEST_DF["Year"] == 1959]["CH4 generated "].item()
    )


def test_incineraion_tier1_co2(
    inc_test_data_DE, expected_inc_plastic_waste=3000, TOLERANCE=0.8
):
    """This test compares the results of incinerated plastic waste in DE with data of Umweltbundesamt.
    https://www.umweltbundesamt.de/daten/ressourcen-abfall/verwertung-entsorgung-ausgewaehlter-abfallarten/kunststoffabfaelle#kunststoffe-produktion-verwendung-und-verwertung

    Based on UBA, in year 2010 ca 3000 Gg plastic waste were energetically used in DE.
    """
    # plastic waste fraction in municipal waste
    msw_plastic_incinerated = IPCC()

    msw_plastic_incinerated.waste.incineration.parameter.urb_population = (
        inc_test_data_DE.urb_pop
    )

    # plastic waste fraction in industrial waste
    isw_rubber_incinerated = IPCC()

    isw_rubber_incinerated.waste.incineration.parameter.gdp = inc_test_data_DE.gdp

    isw_rubber_incinerated.waste.incineration.parameter.isw_gen_rate = (
        inc_test_data_DE.isw_gen_rate
    )

    isw_rubber_incinerated.waste.incineration.parameter.isw_type_frac = (
        inc_test_data_DE.isw_type_frac
    )

    # run both sequences
    my_tier1 = msw_plastic_incinerated.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="msw_plastics",
        activity="inc_unspecified",
        uncertainty="def",
    )
    my_tier2 = isw_rubber_incinerated.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="isw_rubber",
        activity="inc_unspecified",
        uncertainty="def",
    )

    result_inc_plastic_waste = my_tier1.msw_to_incin.value + my_tier2.isw_to_incin.value

    assert (
        abs(
            (expected_inc_plastic_waste - result_inc_plastic_waste)
            / expected_inc_plastic_waste
        )
        <= TOLERANCE
    )


def test_isw_food_tier1(
    inc_test_data_DE,
    expected_isw_food=4500,
    expected_isw_rubber=19700,
    expected_isw_construction=184500,
    TOLERANCE=0.9,
):
    """Test against data of eurostat for 2010"""
    my_ipcc = IPCC()
    my_ipcc.waste.incineration.parameter.gdp = inc_test_data_DE.gdp

    my_ipcc.waste.incineration.parameter.isw_gen_rate = inc_test_data_DE.isw_gen_rate

    my_ipcc.waste.incineration.parameter.isw_type_frac = inc_test_data_DE.isw_type_frac

    # run sequences
    tier_isw_food = my_ipcc.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="isw_food",
        activity="inc_unspecified",
        uncertainty="def",
    )
    tier_isw_construction = my_ipcc.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="isw_construction",
        activity="inc_unspecified",
        uncertainty="def",
    )
    tier_isw_rubber = my_ipcc.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="isw_rubber",
        activity="inc_unspecified",
        uncertainty="def",
    )
    result_isw_food = (
        tier_isw_food.isw_to_incin.value / tier_isw_food.isw_frac_to_incin.value
    )
    result_isw_construction = (
        tier_isw_construction.isw_to_incin.value
        / tier_isw_construction.isw_frac_to_incin.value
    )
    result_isw_rubber = (
        tier_isw_rubber.isw_to_incin.value / tier_isw_rubber.isw_frac_to_incin.value
    )

    assert abs((expected_isw_food - result_isw_food) / expected_isw_food) <= TOLERANCE
    assert (
        abs(
            (expected_isw_construction - result_isw_construction)
            / expected_isw_construction
        )
        <= TOLERANCE
    )
    assert (
        abs((expected_isw_rubber - result_isw_rubber) / expected_isw_rubber)
        <= TOLERANCE
    )


def test_biotreat_waste_tier1(
    inc_test_data_DE,
    expected_msw_to_biotreat=8100,
    TOLERANCE=0.7,
):
    """Test biotreated waste amount in DE against data from UBA for 2010.

    https://www.umweltbundesamt.de/daten/ressourcen-abfall/verwertung-entsorgung-ausgewaehlter-abfallarten/bioabfaelle#sammlung-von-bioabfall

    13 Mio t biodegradable waste to treatment (incl. biogasification)
    ca 62% from msw ("Biotonnenabfälle", "Garten- und Parkabfälle")  = 8.1 Mio t
    assumption: unit refers to wet waste
    """

    my_ipcc = IPCC()

    my_ipcc.waste.biological.parameter.urb_population = inc_test_data_DE.urb_pop

    # run sequences for all bio waste fractions
    tier_msw_food = my_ipcc.waste.biological.sequence.tier1_ch4(
        year=2010,
        region="DE",
        product="msw_food",
        activity="compost",
        uncertainty="def",
    )
    tier_msw_wood = my_ipcc.waste.biological.sequence.tier1_ch4(
        year=2010,
        region="DE",
        product="msw_wood",
        activity="compost",
        uncertainty="def",
    )
    tier_msw_garden = my_ipcc.waste.biological.sequence.tier1_ch4(
        year=2010,
        region="DE",
        product="msw_garden",
        activity="compost",
        uncertainty="def",
    )
    tier_msw_paper = my_ipcc.waste.biological.sequence.tier1_ch4(
        year=2010,
        region="DE",
        product="msw_paper",
        activity="compost",
        uncertainty="def",
    )

    result = (
        tier_msw_food.msw_to_biotreat.value
        + tier_msw_wood.msw_to_biotreat.value
        + tier_msw_garden.msw_to_biotreat.value
        + tier_msw_paper.msw_to_biotreat.value
    )
    assert (
        abs((expected_msw_to_biotreat - result) / expected_msw_to_biotreat) <= TOLERANCE
    )


def test_wastewater_domestic_tier1(
    wwater_test_data_DE,
    expected_ch4=70.9,  # Gg CH4 in 2010 (domestic + commercial)
    TOLERANCE=0.6,
):
    """Data for DE from national inventory.

    https://www.umweltbundesamt.de/sites/default/files/medien/461/publikationen/4292.pdf
    2010: 70.9 Gg CH4 emissions (domestic + commercial)
    1990: 2226.2 Gg CH4 emissions (domestic + commercial)


    https://de.statista.com/statistik/daten/studie/311625/umfrage/gewinnung-von-klaergas-aus-abwasserbehandlungsanlagen-in-deutschland/
    2010: 19139 TJ Methane recovered -> 11 kWh/m3 (1TJ/277778kWh) (0.657kg/m3) -> 317533663 kg
    """
    pass


def test_incineraion_tier1_co2_sample_with_concordance(
    inc_test_data_DE, TOLERANCE=0.05
):
    """This test compares the results of incinerated plastic waste in DE with data of Umweltbundesamt.
    https://www.umweltbundesamt.de/daten/ressourcen-abfall/verwertung-entsorgung-ausgewaehlter-abfallarten/kunststoffabfaelle#kunststoffe-produktion-verwendung-und-verwertung

    Based on UBA, in year 2010 ca 3000 Gg plastic waste were energetically used in DE.
    """
    # plastic waste fraction in municipal waste
    # msw_plastic_incinerated = IPCC()

    # msw_plastic_incinerated.waste.incineration.parameter.urb_population = (
    #    inc_test_data_DE.urb_pop
    # )

    # plastic waste fraction in industrial waste
    isw_rubber_incinerated = IPCC()

    isw_rubber_incinerated.waste.incineration.parameter.gdp = inc_test_data_DE.gdp

    isw_rubber_incinerated.waste.incineration.parameter.isw_gen_rate = (
        inc_test_data_DE.isw_gen_rate
    )

    isw_rubber_incinerated.waste.incineration.parameter.isw_type_frac = (
        inc_test_data_DE.isw_type_frac
    )

    d = {
        "year": [2010, 2011],
        "region": ["DE", "DE"],
        "property": ["def", "sample"],
        "value": [0.36, np.array([0.37, 0.38, 0.36, 0.35])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.isw_frac_to_incin = (
        pd.DataFrame(d).set_index(["year", "region", "property"])
    )

    d = {
        "year": [2010, 2011],
        "region": ["DE", "DE"],
        "activity": ["inc_unspecified", "inc_unspecified"],
        "property": ["def", "sample"],
        "value": [1.0, np.array([0.9, 0.99, 0.98, 0.97])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.incintype_frac = pd.DataFrame(
        d
    ).set_index(["year", "region", "activity", "property"])

    d = {
        "year": [2010, 2011],
        "region": ["DE", "DE"],
        "waste_type": ["isw_rubber", "isw_rubber"],
        "property": ["def", "sample"],
        "value": [0.88, np.array([0.86, 0.89, 0.86, 0.88])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.dm = pd.DataFrame(d).set_index(
        ["year", "region", "waste_type", "property"]
    )

    d = {
        "year": [2010, 2011],
        "region": ["DE", "DE"],
        "waste_type": ["isw_rubber", "isw_rubber"],
        "property": ["def", "sample"],
        "value": [0.66, np.array([0.67, 0.66, 0.64, 0.67])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.cf = pd.DataFrame(d).set_index(
        ["year", "region", "waste_type", "property"]
    )

    d = {
        "region": ["DE", "DE"],
        "waste_type": ["isw_rubber", "isw_rubber"],
        "incin_type": ["inc_unspecified", "inc_unspecified"],
        "property": ["def", "sample"],
        "value": [0.35, np.array([0.32, 0.33, 0.34, 0.37])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.fcf = pd.DataFrame(d).set_index(
        ["region", "waste_type", "incin_type", "property"]
    )

    d = {
        "region": ["DE", "EUR"],
        "waste_type": ["isw_rubber", "isw_rubber"],
        "incin_type": ["inc_unspecified", "inc_unspecified"],
        "property": ["def", "sample"],
        "value": [1.0, np.array([1.0, 1.0, 0.98, 0.99])],
        "unit": ["kg/kg", "kg/kg"],
    }
    isw_rubber_incinerated.waste.incineration.parameter.of = pd.DataFrame(d).set_index(
        ["region", "waste_type", "incin_type", "property"]
    )

    my_tier1 = isw_rubber_incinerated.waste.incineration.sequence.tier1_co2(
        year=2010,
        region="DE",
        product="isw_rubber",
        activity="inc_unspecified",
        uncertainty="def",
    )

    my_tier2 = isw_rubber_incinerated.waste.incineration.sequence.tier1_co2(
        year=2011,
        region="DE",
        product="isw_rubber",
        activity="inc_unspecified",
        uncertainty="sample",
    )
    result = my_tier2.co2_emissions.value.mean()
    expected_co2 = my_tier1.co2_emissions.value

    assert len(my_tier2.isw_to_incin.value) == 4
    assert abs((expected_co2 - result) / expected_co2) <= TOLERANCE
