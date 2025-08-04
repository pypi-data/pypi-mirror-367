import pandas as pd
import pytest

from bonsai_ipcc import IPCC


def test_year_value():
    myipcc = IPCC()

    myipcc.agriculture.livestock_manure.parameter.n = pd.DataFrame(
        {
            "year": [2019, 2019, 2019, 2019, 2019],
            "region": ["DE", "DE", "DE", "DE", "DE"],
            "product": [
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["piece", "piece", "piece", "piece", "piece"],
        }
    ).set_index(["year", "region", "product", "property"])

    s = myipcc.agriculture.livestock_manure.sequence.tier1_n2o(
        year=2009,
        region="DE",
        animal="cattle-other_mature-mal-grazing",
        activity="lagoon",
        uncertainty="def",
    )

    assert s.n.year == 2019
    assert s.n.value == 1.0


def test_year_value_not_neighbor_in_conc_table():
    myipcc = IPCC()

    myipcc.agriculture.livestock_manure.parameter.n = pd.DataFrame(
        {
            "year": [2019, 2019, 2019, 2019, 2019],
            "region": ["DE", "DE", "DE", "DE", "DE"],
            "product": [
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf"],
            "unit": ["piece", "piece", "piece", "piece", "piece"],
        }
    ).set_index(["year", "region", "product", "property"])

    s = myipcc.agriculture.livestock_manure.sequence.tier1_n2o(
        year=2007,
        region="DE",
        animal="cattle-other_mature-mal-grazing",
        activity="lagoon",
        uncertainty="def",
    )

    assert s.n.year == 2019
    assert s.n.value == 1.0


def test_year_value_sample():
    myipcc = IPCC()

    myipcc.agriculture.livestock_manure.parameter.n = pd.DataFrame(
        {
            "year": [2019, 2019, 2019, 2019, 2019, 2019],
            "region": ["DE", "DE", "DE", "DE", "DE", "DE"],
            "product": [
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
                "cattle-other",
            ],
            "property": ["def", "min", "max", "abs_min", "abs_max", "sample"],
            "value": [1.0, 1.0, 1.0, 0.0, "inf", [1.0, 1.0, 0.9, 0.8]],
            "unit": ["piece", "piece", "piece", "piece", "piece", "piece"],
        }
    ).set_index(["year", "region", "product", "property"])

    s = myipcc.agriculture.livestock_manure.sequence.tier1_n2o(
        year=2009,
        region="DE",
        animal="cattle-other_mature-mal-grazing",
        activity="lagoon",
        uncertainty="def",
    )

    assert s.n.year == 2019
    assert s.n.value == 1.0
