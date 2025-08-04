"""
@author: Albert
"""

import pandas as pd

from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", activitycode="petrochem", productcode="refined")

parameter = Parameter(["data/industry/chemical", "data/ppf/ethylene", "data/generic"])

concordance = Concordance("data/")

# Extend the existing ef_co2_i_k table with additional co2 emissions data
parameter.ef_co2_i_k = pd.concat(
    [
        parameter.ef_co2_i_k,
        parameter.emission_co2_in_refinery_per_ethylene,
    ]
)


# extend the existing fa_i_j_k table additional ch4 emissions data
parameter.fa_i_j_k = pd.concat(
    [
        parameter.fa_i_j_k,
        parameter.feedstock_use_in_refinery_per_ethylene,
    ]
)
