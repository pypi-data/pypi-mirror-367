from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", activitycode="landfill", productcode="waste")

parameter = Parameter(["data/waste/swd/", "data/waste/waste_generation/"])

concordance = Concordance("data/")
