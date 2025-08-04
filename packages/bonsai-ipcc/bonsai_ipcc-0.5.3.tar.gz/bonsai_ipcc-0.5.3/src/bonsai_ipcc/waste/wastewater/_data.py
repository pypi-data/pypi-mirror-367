from ..._data import Concordance, Dimension, Parameter

dimension = Dimension(
    "data/", activitycode="wastewater_treatment", productcode="wastewater"
)

parameter = Parameter(["data/waste/wastewater/", "data/waste/waste_generation/"])

concordance = Concordance("data/")
