# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 10:48:40 2023

@author: Mathieu Delpierre (2.-0 LCA Consultants)
"""


####################################################################################
# ---------------------- New version: merge ppf to IPCC -------------------------- #
####################################################################################

from ..._data import Concordance, Dimension, Parameter

dimension = Dimension("data/", productcode="cement_production")

parameter = Parameter(["data/industry/mineral", "data/ppf/cement"])

concordance = Concordance("data/")
