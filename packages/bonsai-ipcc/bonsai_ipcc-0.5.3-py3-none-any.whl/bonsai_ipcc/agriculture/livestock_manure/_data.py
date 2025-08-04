from ..._data import Concordance, Dimension, Parameter

dimension = Dimension(
    path_in="data/", activitycode="manuretreatment", productcode="animal"
)

parameter = Parameter(["data/agriculture/livestock_manure", "data/waste/swd"])

concordance = Concordance("data/")
