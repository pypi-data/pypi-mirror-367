from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/")

dimension = Dimension(
    path_in="data/", activitycode="agriculture", productcode="agforfi"
)

parameter = Parameter(
    [
        "data/agriculture/soils",
        "data/agriculture/livestock_manure",
        "data/agriculture/generic",
    ]
)

concordance = Concordance("data/")
