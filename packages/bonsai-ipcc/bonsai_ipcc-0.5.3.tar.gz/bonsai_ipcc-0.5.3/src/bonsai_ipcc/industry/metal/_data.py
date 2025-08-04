from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", productcode="metal", activitycode="metal_production")

parameter = Parameter(["data/industry/metal", "data/generic"])

concordance = Concordance("data/")
