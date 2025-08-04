from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", activitycode="biological", productcode="waste")

parameter = Parameter(["data/waste/biological/", "data/waste/waste_generation/"])

concordance = Concordance("data/")
