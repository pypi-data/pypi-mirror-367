from ..._data import Concordance, Dimension, Parameter

dimension = Dimension(
    "data/", productcode="material", activitycode="material_production"
)

parameter = Parameter(["data/industry/mineral"])

concordance = Concordance("data/")
