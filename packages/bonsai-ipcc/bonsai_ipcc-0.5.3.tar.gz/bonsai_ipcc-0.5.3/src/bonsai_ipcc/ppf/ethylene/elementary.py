"""
Utility functions for calculating the product and elementary flow of plastics in the PPF model.

Author: Albert K. Osei-Owusu (ako@plan.aau.dk)
Department of Planning and Sustainability, Aalborg University, Copenhagen
Created: 2025-05-27
"""

from ...industry.chemical.elementary import (
    ech4_fugitive,
    ech4_process_vent,
    ech4_tier1,
    eco2_tier1,
    pp_i_j_k,
)


def by_product_supply(pp_i_j_k: float, lci_coefficient: float) -> float:
    """Calculate the amount of by-products produced during petrochemical i's production (t/yr).

    Parameters
    ----------
    pp_i_j_k : float
        Amount of petrochemical i produced from activity j using feedstock (e.g., naphtha, ethane) k (t/yr)
    lci_coefficient : float
        LCI coefficient for the by-product produced per petrochemical i)
    Returns
    -------
    float
        Amount of by-product produced by the activity (t/yr)
    """
    return pp_i_j_k * lci_coefficient


def input_use(pp_i_j_k: float, lci_coefficient: float) -> float:
    """Calculate the amount of product flow (eg. steam, electricty, water etc) i used as input to produce unit of some petrochemical/plastic output (t/t).

    Parameters
    ----------
    pp_i_j_k : float
        Amount of petrochemical i produced from activity j using feedstock (e.g., naphtha, ethane) k (t/yr)
    lci_coefficient : float
        LCI coefficient for the input use of petrochemical i

    Returns
    -------
    float
        Amount of petrochemical i used as input (t/yr)
    """
    return pp_i_j_k * lci_coefficient


def plastic_supply(fdstk_i_j_k: float, lci_coefficient: float) -> float:
    """Calculate the amount of plastic produced from a specific petrochemical process, product, and technology.

    Parameters
    ----------
    fdstk_i_j_k : float
        Amount of petrochemical feedstock i from activity j, required to produced plastic k (t/yr)
    lci_coefficient : float
        Life Cycle Inventory (LCI) coefficient for petrochemical required to produce a unit of plastic k (t/t)

    Returns
    -------
    float
        Amount of plastic produced by the specified activity (t/yr)
    """
    return fdstk_i_j_k * lci_coefficient


def ethylene_input_for_monomer(pp_m: float, lci_coefficient: float) -> float:
    """Calculate the amount of ethylene required as input to produce a given amount of monomer.

    Parameters
    ----------
    monomer_production : float
        Amount of monomer produced (t/yr)
    ethylene_lci_coefficient : float
        LCI coefficient for ethylene required per unit of monomer produced (t/t)

    Returns
    -------
    float
        Amount of ethylene used as input (t/yr)
    """
    return pp_m * lci_coefficient
