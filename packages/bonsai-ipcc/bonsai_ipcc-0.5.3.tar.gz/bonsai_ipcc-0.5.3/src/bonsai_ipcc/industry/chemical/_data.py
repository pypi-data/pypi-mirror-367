from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", activitycode="petrochem", productcode="refined")

parameter = Parameter(["data/industry/chemical"])

concordance = Concordance("data/")
