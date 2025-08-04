"""
Methanol production pathways:
Chemical reactions and utilities for sequences of reactions.

References:
   [1]  Levi, P. G., & Cullen, J. M. (2018). Mapping Global Flows of Chemicals: From Fossil Fuel Feedstocks to Chemical Products. Environmental Science & Technology, 52(4), 1725-1734. https://doi.org/10.1021/acs.est.7b04573

   [2]  Kajaste, R., Hurme, M., & Oinas, P. (2018). Methanol-Managing greenhouse gas emissions in the production chain by optimizing the resource base. AIMS Energy, 6(6), 1074-1102. https://doi.org/10.3934/energy.2018.6.1074

   [3]  Behr, A. (2014). Methanol: The Basic Chemical and Energy Feedstock of the Future. Asinger’s Vision Today. Edited by Martin Bertau, Heribert Offermanns, Ludolf Plass, Friedrich Schmidt and Hans-Jürgen Wernicke. Angewandte Chemie International Edition, 53(47), 12674. https://doi.org/10.1002/anie.201409583

   [4]  Bertau, M., Offermanns, H., Plass, L., Schmidt, F., & Wernicke, H.-J. (2013). Methanol: The Basic Chemical and Energy Feedstock of the Future. Springer. https://doi.org/10.1007/978-3-642-39709-7

   [5]  Stephan, D. W. (2013). Beyond Oil and Gas: The Methanol Economy. Second Updated and Enlarged Edition.
        By George A. Olah, Alain Goeppert, G. K. Surya Prakash. Energy Technology, 1(12), 777. https://doi.org/10.1002/ente.201305018


Created: 2024-06-13
Description: Methanol parameterised production function equations.
Scope: KR Project WP5.2 Data Collection for disaggregated production functions
Author: Albert K. Osei-Owusu
Institution: Department of Sustainability and Planning, Aalborg University
Email: ako@plan.aau.dk
"""

import math
from typing import Dict, Literal, Tuple

from ...industry.chemical.elementary import (
    ech4_fugitive,
    ech4_process_vent,
    ech4_tier1,
    eco2_tier1,
    pp_i_j_k,
)

# Molecular weights (g/mol)
MW_C = 12.010  # Carbon
MW_CH4 = 16.040  # Methane
MW_CH4O = 32.042  # Methanol
MW_H2O = 18.015  # Water
MW_O2 = 32.000  # Oxygen
MW_CO = 28.010  # Carbon monoxide
MW_H = 1.008  # Hydrogen
MW_H2 = 2.016  # Hydrogen
MW_CO2 = 44.010  # Carbon dioxide


# Input requirements function
def by_product_supply(pp_i: float, lci_coefficient: float) -> float:
    """Calculate the amount of by-products produced during methanol production.

    Parameters
    ----------
    pp_i : float
        Amount of produced methanol (t/yr)
    lci_coefficient : float
        Ratio factor for by-product production (t/t)

    Returns
    -------
    float
        Amount of by-product produced by the activity (t/yr)
    """
    return pp_i * lci_coefficient


def gas_requirements(
    tons_CH4: float, density_gas: float, CH4_vol_percent: float
) -> (float, float):
    """
    Calculate the required quantity of gas from the mass of methane (CH4) in tonnes.

    Parameters
    ----------
    tons_CH4 : float
        The mass of methane (CH4) in tonnes intended for methanol production.
    density_gas : float
        The density of gas in kg/m³ under specific conditions.
    CH4_vol_percent : float
        The volume percentage of methane (CH4) in the gas mixture.

    Returns
    -------
    float
        The quantity of gas required in tonnes.
    float
        The volume of gas required in cubic meters.
    """
    # Convert tonnes of CH4 to kilograms
    kg_CH4 = tons_CH4 * 1e3

    # Convert the volume percentage to a decimal
    decimal_CH4_in_gas = CH4_vol_percent / 100

    # Calculate the volume of gas in cubic meters that contains the given mass of methane
    gas_volume_m3 = kg_CH4 / (density_gas * decimal_CH4_in_gas)

    # Calculate the mass of gas in tonnes
    gas_mass_tonnes = gas_volume_m3 * density_gas / 1e3

    return gas_mass_tonnes, gas_volume_m3


def coal_requirements(tons_CH4: float, carbon_fraction_coal: float) -> float:
    """
    Calculate the mass of coal required, given the tonnes of methane obtained from coal-based CSR
    and the carbon fraction of coal in weight percent (expressed as a decimal).

    Parameters
    ----------
    tons_CH4 : float
        Tonnes of methane (CH4) derived from coal for CSR.
    carbon_fraction_coal : float
        Fraction of coal mass that is carbon (e.g. 0.65 for 65 wt% carbon).

    Returns
    -------
    float
        The mass of coal required in tonnes.
    """
    # Stoichiometric ratio: 1 tonne of CH4 requires 0.75 tonnes of carbon
    carbon_needed_tonnes = 0.75 * tons_CH4

    # Calculate total coal needed based on its carbon fraction
    coal_needed_tonnes = carbon_needed_tonnes / carbon_fraction_coal

    return coal_needed_tonnes


def calculate_feedstock_requirements(
    pp_meoh: float, lci_coefficients: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate feedstock requirements for multiple resources, handling None or NaN values.

    Parameters:
    ----------
    pp_meoh : float
        The total volume of methanol produced in tonnes.
    lci_coefficients : dict
        A dictionary where the key is the name of the resource and the value is the corresponding LCI coefficient.

    Returns:
    -------
    dict
        A dictionary where the key is the name of the resource and the value is the calculated feedstock requirement.
        If the coefficient is None or NaN, the value will be NaN.
    """

    requirements = {}
    for resource, coefficient in lci_coefficients.items():
        if coefficient is None or math.isnan(coefficient):
            requirements[resource] = math.nan
        else:
            requirements[resource] = pp_meoh * coefficient
    return requirements


#####################################################################################################################################
# The following equations are sourced from [1]
#####################################################################################################################################


# Syngas production functions for methanol production
def syngas_from_csr(
    CHn_tonnes: float, H2O_tonnes: float, n: int
) -> (float, float, str, str, float):
    """
    Conventional steam methane reforming (CSR) process to produce syngas (carbon monoxide and hydrogen).
    The reaction is as follows, with all quantities in moles:
    CHn + H2O -> CO + (n-1)H2

    Parameters
    ----------
    CHn : float
        Moles of hydrocarbon (CHn).
    H2O : float
        Moles of water.
    n : int
        Number of hydrogen atoms in the hydrocarbon.

    Returns
    -------
    float
        Moles of carbon monoxide produced.
    float
        Moles of hydrogen produced.
    """
    # Calculate the molecular weight of the hydrocarbon (assuming it's an alkane)
    MW_CHn = MW_C + n * MW_H

    # Convert tonnes to moles
    moles_CHn = (CHn_tonnes * 1e6) / MW_CHn  # tonnes -> grams -> moles
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Determine limiting reagent
    if moles_CHn <= moles_H2O:
        limiting_reagent = "CHn"
        excess_reagent = "H2O"
        moles_reacted = moles_CHn
        excess_moles = moles_H2O - moles_reacted
    else:
        limiting_reagent = "H2O"
        excess_reagent = "CHn"
        moles_reacted = moles_H2O
        excess_moles = moles_CHn - moles_reacted

    # Products
    CO_tonnes = (moles_reacted * MW_CO) / 1e6
    H2_tonnes = ((n - 1) * moles_reacted * MW_H2) / 1e6

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CHn if excess_reagent == "CHn" else MW_H2O)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def syngas_from_pox(
    CHn_tonnes: float, O2_tonnes: float, n: int
) -> (float, float, str, str, float):
    """
    Partial Oxidation (POX) process to produce syngas (carbon monoxide and hydrogen), with inputs in tonnes and outputs in tonnes.

    Parameters:
    - CHn_tonnes: float, tonnes of hydrocarbon (CHn).
    - O2_tonnes: float, tonnes of oxygen.
    - n: int, number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.

    Notes:
    The reaction is as follows, with all quantities in tonnes:
    2CHn + O2 -> 2CO + nH2
    """
    # Calculate the molecular weight of the hydrocarbon (assuming it's an alkane)
    MW_CHn = MW_C + n * MW_H

    # Convert tonnes to moles
    moles_CHn = (CHn_tonnes * 1e6) / MW_CHn
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent and the moles reacted
    moles_reacted_CHn = moles_CHn / 2
    moles_reacted_O2 = moles_O2
    if moles_reacted_CHn < moles_reacted_O2:
        limiting_reagent = "CHn"
        excess_reagent = "O2"
        moles_reacted = moles_reacted_CHn
        excess_moles = moles_O2 - moles_reacted
    else:
        limiting_reagent = "O2"
        excess_reagent = "CHn"
        moles_reacted = moles_reacted_O2
        excess_moles = moles_CHn - (2 * moles_reacted)

    # Calculate products based on the moles reacted
    CO_tonnes = (2 * moles_reacted * MW_CO) / 1e6
    H2_tonnes = (n * moles_reacted * MW_H2) / 1e6

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CHn if excess_reagent == "CHn" else MW_O2)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


# Combined syngas production and water gas shift conversion process for methanol for each process route
def csr_combined(
    CHn_tonnes: float, H2O_tonnes: float, CO2_tonnes: float, n: float
) -> (float, float, float, str, str, float):
    """
    Steam methane reforming/Conventional steam reforming process for syngas production used in methanol synthesis for n > 3, with inputs in tonnes and outputs in tonnes.
    CHn + H2O + (n - 3)/3 CO2 -> (n/3) CO + (2n/3) H2 + (n-3)/3 H2O

    Parameters:
    - CHn_tonnes: float, tonnes of hydrocarbon (CHn).
    - H2O_tonnes: float, tonnes of water.
    - CO2_tonnes: float, tonnes of carbon dioxide.
    - n: float, Number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon monoxide (CO) produced.
    - float, tonnes of hydrogen (H2) produced.
    - float, tonnes of water (H2O) produced or consumed net.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    if n <= 3:
        raise ValueError("n must be greater than 3 for this reaction.")

    # Assuming molecular weights for calculations
    MW_CHn = 14.01 + (n * 1.008)  # Generic approximation

    # Convert tonnes to moles
    moles_CHn = CHn_tonnes * 1e6 / MW_CHn
    moles_H2O = H2O_tonnes * 1e6 / MW_H2O
    moles_CO2 = CO2_tonnes * 1e6 / MW_CO2

    # Stoichiometry calculation to find the limiting reagent
    stoichiometric_ratio_CHn = moles_CHn
    stoichiometric_ratio_H2O = moles_H2O + (
        moles_CO2 * 3 / (n - 3)
    )  # Total H2O available for reaction
    stoichiometric_ratio_CO2 = moles_CO2

    # Calculate the limiting ratio and identify the limiting reagent
    limiting_ratios = {
        "CHn": stoichiometric_ratio_CHn,
        "H2O": stoichiometric_ratio_H2O,
        "CO2": stoichiometric_ratio_CO2,
    }
    limiting_reagent = min(limiting_ratios, key=limiting_ratios.get)
    limiting_value = limiting_ratios[limiting_reagent]

    # Calculate the amounts of products based on the limiting reagent
    moles_CO_produced = (n / 3) * limiting_value
    moles_H2_produced = (2 * n / 3) * limiting_value
    moles_H2O_net = (n - 3) / 3 * limiting_value  # Net H2O produced or consumed

    # Convert moles back to tonnes
    CO_tonnes = moles_CO_produced * MW_CO / 1e6
    H2_tonnes = moles_H2_produced * MW_H2 / 1e6
    H2O_net_tonnes = (
        moles_H2O_net * MW_H2O / 1e6
    )  # Adjusted for net consumption or production

    # Calculate the excess amount for non-limiting reagents
    excess_amount = 0  # Initialize excess amount
    for reagent, value in limiting_ratios.items():
        if reagent != limiting_reagent:
            excess = value - limiting_value
            if excess > 0:
                excess_amount = (
                    excess
                    * (
                        MW_CHn
                        if reagent == "CHn"
                        else MW_H2O
                        if reagent == "H2O"
                        else MW_CO2
                    )
                    / 1e6
                )
                excess_reagent = reagent
                break

    return (
        CO_tonnes,
        H2_tonnes,
        H2O_net_tonnes,
        limiting_reagent,
        excess_reagent,
        excess_amount,
    )


def partial_oxidation_combined(
    CHn_tonnes: float, O2_tonnes: float, H2O_tonnes: float, n: float
) -> (float, float, float, str, float):
    """
    Methanol production from oil or coal using the partial oxidation process, with all quantities in tonnes.
    The reaction is as follows:
    2CHn + O2 + (4-n)/3 H2O -> (n+2)/3 CH4O + (4-n)/3 CO2

    Parameters:
    - CHn_tonnes: float, Tonnes of hydrocarbon (CHn).
    - O2_tonnes: float, Tonnes of oxygen.
    - H2O_tonnes: float, Tonnes of water.
    - n: float, Number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, Tonnes of methanol (CH4O) produced.
    - float, Tonnes of carbon dioxide (CO2) produced.
    - float, Tonnes of water (H2O) consumed.
    - str, The limiting reactant in the reaction.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    if n >= 4:
        raise ValueError("The value of n must be less than 4.")

    # Molecular weights
    MW_CHn = 14.01 + (n * 1.008)  # Approximation for generic hydrocarbon CHn
    MW_O2 = 32.00
    MW_H2O = 18.01528
    MW_CH4O = 32.04  # Methanol
    MW_CO2 = 44.01

    # Convert tonnes to moles
    moles_CHn = (CHn_tonnes * 1e6) / MW_CHn
    moles_O2 = (O2_tonnes * 1e6) / MW_O2
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Calculate stoichiometric ratios
    stoichiometric_ratio_CHn = moles_CHn / 2
    stoichiometric_ratio_O2 = moles_O2
    stoichiometric_ratio_H2O = moles_H2O * 3 / (4 - n)

    # Determine the limiting reactant
    limiting_value = min(
        stoichiometric_ratio_CHn, stoichiometric_ratio_O2, stoichiometric_ratio_H2O
    )
    limiting_reactant = (
        "CHn"
        if limiting_value == stoichiometric_ratio_CHn
        else ("O2" if limiting_value == stoichiometric_ratio_O2 else "H2O")
    )

    # Calculate products based on limiting reactant
    moles_reacted = limiting_value
    CH4O_produced = (
        (n + 2) / 3 * moles_reacted
    )  # Adjust for the actual reaction based on limiting reactant
    CO2_produced = (4 - n) / 3 * moles_reacted
    H2O_consumed = (4 - n) / 3 * moles_reacted

    # Convert moles back to tonnes
    CH4O_tonnes_produced = CH4O_produced * MW_CH4O / 1e6
    CO2_tonnes_produced = CO2_produced * MW_CO2 / 1e6
    H2O_tonnes_consumed = H2O_consumed * MW_H2O / 1e6

    # Calculating excess amount for the limiting reactant
    excess_amount_tonnes = 0  # Additional calculation needed based on reactant availability and stoichiometry

    return (
        CH4O_tonnes_produced,
        CO2_tonnes_produced,
        H2O_tonnes_consumed,
        limiting_reactant,
        excess_amount_tonnes,
    )


###########################################################################################
#  Reverse processes for methanol production
##########################################################################################
def reverse_csr_combined_with_TCs(
    CH4O_tonnes: float,
    n: float,
) -> (float, float, float, float, str, float, dict):
    """
    Generalised 'reverse CSR' function to calculate reactants and products
    for the equation:
        CH_n + H₂O + ((n-3)/3) CO₂ -> ((n)/3) CH₄O + ((n-3)/3) H₂O

    This function calculates the ideal (100% efficient) stoichiometric amounts
    required to produce the target methanol, with all units in tonnes.
    It also identifies the limiting reagent and computes any excess.

    Additionally, it returns transfer coefficients for each input.
    The dictionary has six keys:
        - "CHn_meoh":  % of CH_n feed (by mass, based on carbon) transferred to methanol.
        - "CHn_water": % of CH_n feed not transferred to methanol.
        - "H2O_meoh":  % of H₂O feed contributing to methanol (by difference).
        - "H2O_water": % of H₂O feed appearing as by-product.
        - "CO2_meoh":  % of CO₂ feed (by mass, based on carbon) transferred to methanol.
        - "CO2_water": % of CO₂ feed not transferred to methanol.

    Parameters
    ----------
    CH4O_tonnes : float
        Tonnes of methanol (CH₄O) to be produced.
    n : float
        Number of hydrogen atoms in the feedstock hydrocarbon (CH_n).
        For natural gas (methane), n = 4. Must be >= 3.

    Returns
    -------
    CHn_tonnes_required : float
        Tonnes of hydrocarbon (CH_n) required.
    H2O_tonnes_input_required : float
        Tonnes of water (H₂O) required as input.
    H2O_tonnes_output : float
        Tonnes of water (H₂O) produced as by-product.
    CO2_tonnes_consumed : float
        Tonnes of carbon dioxide (CO₂) consumed.
    limiting_reagent_name : str
        The reagent that is limiting (smallest in moles).
    excess_tonnes : float
        Tonnes of excess reagent remaining after the reaction.
    transfer_coeffs : dict
        A dictionary with six keys (see above).
    """
    if n < 3:
        raise ValueError("The value of n must be at least 3 for this process.")

    # --- Molecular weights (g/mol) ---
    MW_CHn = MW_C + (n * 1.008)  # e.g. for n=4, ~16.042 g/mol

    # --- Convert target methanol production (tonnes) to moles ---
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # --- Ideal stoichiometric ratios (per 1 mole CH4O) based on the equation ---
    ratio_CHn = 3.0 / n  # CH_n: 3/n moles
    ratio_H2O_input = 3.0 / n  # H₂O (input): 3/n moles
    ratio_CO2 = (n - 3.0) / n  # CO₂: (n-3)/n moles
    ratio_H2O_output = (n - 3.0) / n  # H₂O (by-product): (n-3)/n moles

    # --- Calculate ideal (100% efficiency) moles required/produced ---
    ideal_moles_CHn = moles_CH4O * ratio_CHn
    ideal_moles_H2O = moles_CH4O * ratio_H2O_input
    ideal_moles_CO2 = moles_CH4O * ratio_CO2
    ideal_moles_H2O_out = moles_CH4O * ratio_H2O_output

    # In the ideal case (100% conversion):
    moles_CHn_required = ideal_moles_CHn
    moles_H2O_input_required = ideal_moles_H2O
    moles_CO2_required = ideal_moles_CO2
    moles_H2O_output = ideal_moles_H2O_out

    # --- Convert moles back to tonnes ---
    CHn_tonnes_required = (moles_CHn_required * MW_CHn) / 1e6
    H2O_tonnes_input_required = (moles_H2O_input_required * MW_H2O) / 1e6
    CO2_tonnes_consumed = (moles_CO2_required * MW_CO2) / 1e6
    H2O_tonnes_output = (moles_H2O_output * MW_H2O) / 1e6

    # --- Determine limiting reagent (ideal case) ---
    limiting_moles = min(
        moles_CHn_required, moles_H2O_input_required, moles_CO2_required
    )
    if limiting_moles == moles_CHn_required:
        limiting_reagent_name = "CH_n"
        excess_moles_H2O = moles_H2O_input_required - moles_CHn_required
        excess_moles_CO2 = moles_CO2_required - moles_CHn_required
        excess_tonnes = (excess_moles_H2O * MW_H2O + excess_moles_CO2 * MW_CO2) / 1e6
    elif limiting_moles == moles_H2O_input_required:
        limiting_reagent_name = "H₂O"
        excess_moles_CHn = moles_CHn_required - moles_H2O_input_required
        excess_moles_CO2 = moles_CO2_required - moles_H2O_input_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_CO2 * MW_CO2) / 1e6
    else:
        limiting_reagent_name = "CO₂"
        excess_moles_CHn = moles_CHn_required - moles_CO2_required
        excess_moles_H2O = moles_H2O_input_required - moles_CO2_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_H2O * MW_H2O) / 1e6

    # --- Calculate transfer coefficients (ideal case) ---
    # For CH_n:
    # Only the carbon in CH_n goes into methanol. The mass of carbon in CH_n is 12.010 g.
    TC_CHn_meoh = (
        MW_C / MW_CHn
    ) * 100  # e.g. for n=4, 12.010/16.042*100 = (appr.) 74.9%
    TC_CHn_water = 100.0 - TC_CHn_meoh  # = (appr.) 25.1%

    # For CO₂:
    # Only the carbon in CO₂ goes into methanol. The mass of carbon in CO₂ is 12.010 g.
    TC_CO2_meoh = (MW_C / MW_CO2) * 100  # e.g. 12.010/44.010*100 = (appr.) 27.3%
    TC_CO2_water = 100.0 - TC_CO2_meoh  # = (appr.) 72.7%

    # For H₂O:
    # Ideal water input per mole CH₄O = 3/n and water by-product = (n-3)/n.
    # The fraction of water input that becomes by-product is:
    ideal_water_fraction = (
        ratio_H2O_output / ratio_H2O_input
    )  # For n=4, 0.25/0.75 = 0.3333
    TC_H2O_water = ideal_water_fraction * 100  # = (appr.) 33.33%
    TC_H2O_meoh = 100.0 - TC_H2O_water  # = (appr.) 66.67%

    transfer_coeffs = {
        "CHn_meoh": TC_CHn_meoh,
        "CHn_water": TC_CHn_water,
        "H2O_meoh": TC_H2O_meoh,
        "H2O_water": TC_H2O_water,
        "CO2_meoh": TC_CO2_meoh,
        "CO2_water": TC_CO2_water,
    }

    return (
        CHn_tonnes_required,
        H2O_tonnes_input_required,
        H2O_tonnes_output,
        CO2_tonnes_consumed,
        limiting_reagent_name,
        excess_tonnes,
        transfer_coeffs,
    )


def adjusted_reverse_csr_with_TCs(
    CH4O_tonnes: float,
    n: float,
    sg_efficiency: float = 81,
    ms_efficiency: float = 93,
) -> (float, float, float, float, str, float, dict):
    """
    Adjusted 'reverse CSR' function to calculate the required reactants and the by‐product water
    for the reaction:

        CH_n + H₂O + ((n-3)/3) CO₂ → ((n)/3) CH₄O + ((n-3)/3) H₂O

    The ideal stoichiometric ratios (per 1 mole CH₄O produced) are:
      • CH_n (input):         3/n moles
      • H₂O (input):         3/n moles
      • CO₂ (input):         (n-3)/n moles
      • H₂O (by‐product):    (n-3)/n moles

    Because the process is not 100% efficient, extra reactants must be fed.
    The overall efficiency is sg_efficiency × ms_efficiency and the ideal (100% efficient)
    feed is scaled by the usage multiplier = 1 / (sg_efficiency * 0.01) × (ms_efficiency * 0.01)

    **Transfer Coefficients** – defined on the basis of the reacted (ideal) feed:
      - For CH_n and CO₂: All the carbon in the reacted feed is incorporated into methanol.
          • TC_meoh = 100% (i.e. 100% of the reacted CH_n and CO₂ goes to CH₄O)
          • TC_water = 0%
      - For H₂O: The ideal stoichiometric split is:
          • Water input per mole CH₄O = 3/n moles
          • Water by‐product per mole CH₄O = (n-3)/n moles
        Thus, the fraction of water input that becomes by‐product is:
          ideal_water_fraction = (n-3)/3.
        Hence,
          • TC_H2O_water = (n-3)/3 × 100%
          • TC_H2O_meoh = 100% - TC_H2O_water

    Parameters
    ----------
    CH4O_tonnes : float
        Tonnes of methanol (CH₄O) to be produced.
    n : float
        Number of hydrogen atoms in the feedstock hydrocarbon (CH_n). For natural gas, n = 4.
        Must be >= 3.
    sg_efficiency : float, optional
        Synthesis gas preparation efficiency (%, default 81).
    ms_efficiency : float, optional
        Methanol synthesis efficiency (%, default 93).

    Returns
    -------
    CHn_tonnes_required : float
        Tonnes of hydrocarbon (CH_n) required.
    H2O_tonnes_input_required : float
        Tonnes of water (H₂O) required as input.
    H2O_tonnes_output : float
        Tonnes of water (H₂O) produced as by‐product.
    CO2_tonnes_consumed : float
        Tonnes of carbon dioxide (CO₂) consumed.
    limiting_reagent_name : str
        The reagent that becomes limiting (smallest in moles).
    excess_tonnes : float
        Tonnes of excess reagent remaining after the reaction.
    transfer_coeffs : dict
        A dictionary with six keys:
          "CHn_meoh": % of CH_n feed (by mass) transferred to methanol.
          "CHn_water": % of CH_n feed not transferred to methanol.
          "H2O_meoh": % of H₂O feed contributing to methanol.
          "H2O_water": % of H₂O feed appearing as by‐product water.
          "CO2_meoh": % of CO₂ feed transferred to methanol.
          "CO2_water": % of CO₂ feed not transferred to methanol.
    """
    if n < 3:
        raise ValueError("The value of n must be at least 3 for this process.")

    # --- Molecular weights (g/mol) ---
    MW_CHn = MW_C + (n * 1.008)
    # --- Convert target methanol production (tonnes) to moles ---
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # --- Ideal stoichiometric ratios (per 1 mole CH4O) ---
    ratio_CHn = 3.0 / n  # CH_n: 3/n moles
    ratio_H2O_input = 3.0 / n  # H₂O (input): 3/n moles
    ratio_CO2 = (n - 3.0) / n  # CO₂: (n-3)/n moles
    ratio_H2O_output = (n - 3.0) / n  # H₂O (by-product): (n-3)/n moles

    # --- Calculate ideal (100% efficient) moles required/produced ---
    ideal_moles_CHn = moles_CH4O * ratio_CHn
    ideal_moles_H2O = moles_CH4O * ratio_H2O_input
    ideal_moles_CO2 = moles_CH4O * ratio_CO2
    ideal_moles_H2O_out = moles_CH4O * ratio_H2O_output

    # --- Apply inefficiencies ---
    overall_efficiency = (sg_efficiency / 100) * (
        ms_efficiency / 100
    )  # e.g. 0.81*0.93 = (appr.) 0.753
    usage_multiplier = 1.0 / overall_efficiency  # e.g. = (appr.) 1.33
    moles_CHn_required = ideal_moles_CHn * usage_multiplier
    moles_H2O_input_required = ideal_moles_H2O * usage_multiplier
    moles_CO2_required = ideal_moles_CO2 * usage_multiplier
    # The water output is determined solely by the methanol produced (assumed 100% conversion of the ideal output).
    moles_H2O_output = ideal_moles_H2O_out

    # --- Convert moles back to tonnes ---
    CHn_tonnes_required = (moles_CHn_required * MW_CHn) / 1e6
    H2O_tonnes_input_required = (moles_H2O_input_required * MW_H2O) / 1e6
    CO2_tonnes_consumed = (moles_CO2_required * MW_CO2) / 1e6
    H2O_tonnes_output = (moles_H2O_output * MW_H2O) / 1e6

    # --- Determine limiting reagent ---
    limiting_moles = min(
        moles_CHn_required, moles_H2O_input_required, moles_CO2_required
    )
    if limiting_moles == moles_CHn_required:
        limiting_reagent_name = "CH_n"
        excess_moles_H2O = moles_H2O_input_required - moles_CHn_required
        excess_moles_CO2 = moles_CO2_required - moles_CHn_required
        excess_tonnes = (excess_moles_H2O * MW_H2O + excess_moles_CO2 * MW_CO2) / 1e6
    elif limiting_moles == moles_H2O_input_required:
        limiting_reagent_name = "H₂O"
        excess_moles_CHn = moles_CHn_required - moles_H2O_input_required
        excess_moles_CO2 = moles_CO2_required - moles_H2O_input_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_CO2 * MW_CO2) / 1e6
    else:
        limiting_reagent_name = "CO₂"
        excess_moles_CHn = moles_CHn_required - moles_CO2_required
        excess_moles_H2O = moles_H2O_input_required - moles_CO2_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_H2O * MW_H2O) / 1e6

    # --- Calculate transfer coefficients, ensuring no cross-transfer of elements ---
    # For CH_n and CO₂, all of the carbon that reacts is incorporated into methanol.
    TC_CHn_meoh = 100.0  # 100% of the reacted CH_n (carbon) ends up in methanol.
    TC_CHn_water = 0.0  # None of the CH_n ends up as water.
    TC_CO2_meoh = 100.0  # 100% of the reacted CO₂ (carbon) is used in methanol.
    TC_CO2_water = 0.0  # None of the CO₂ goes to water.

    # For H₂O, the partitioning is defined by the stoichiometry:
    #   H₂O input per mole CH₄O = 3/n moles and H₂O (by-product) = (n-3)/n moles.
    ideal_water_fraction = (
        ratio_H2O_output / ratio_H2O_input
    )  # For n=4, 0.25/0.75 = 0.3333 (33.33%)
    TC_H2O_water = ideal_water_fraction * 100  # ~33.33% of water appears as by-product.
    TC_H2O_meoh = (
        100.0 - TC_H2O_water
    )  # ~66.67% of water input is effectively used in methanol formation.

    transfer_coeffs = {
        "CHn_meoh": TC_CHn_meoh,
        "CHn_water": TC_CHn_water,
        "H2O_meoh": TC_H2O_meoh,
        "H2O_water": TC_H2O_water,
        "CO2_meoh": TC_CO2_meoh,
        "CO2_water": TC_CO2_water,
    }

    return (
        CHn_tonnes_required,
        H2O_tonnes_input_required,
        H2O_tonnes_output,
        CO2_tonnes_consumed,
        limiting_reagent_name,
        excess_tonnes,
        transfer_coeffs,
    )


def reverse_pox_combined(
    CH4O_tonnes: float, n: float
) -> (float, float, float, float, str, float, dict):
    """
    Reverse process of partial oxidation for methanol production, calculating
    the required reactants in tonnes, plus transfer coefficients for each input
    (CH_n, O₂, and H₂O) to methanol (CH₄O) vs CO₂.

    The reaction is:
      2 CH_n + O₂ + (4 - n)/3 H₂O -> (n + 2)/3 CH₄O + (4 - n)/3 CO₂

    For n < 4 (e.g. n = 2 for a 'CH2' style hydrocarbon), after dividing by (n+2)/3
    we get:
      CH_n: 6/(n+2)
      O₂:  3/(n+2)
      H₂O: (4-n)/(n+2)
      CO₂: (4-n)/(n+2)  (product)

    Parameters
    ----------
    CH4O_tonnes : float
        Tonnes of methanol (CH₄O) to be produced.
    n : float
        Number of hydrogen atoms in the original hydrocarbon (CH_n),
        must be < 4 for this reverse POX process.

    Returns
    -------
    CHn_tonnes_required : float
        Tonnes of hydrocarbon (CH_n) required to produce the given amount of methanol.
    O2_tonnes_required : float
        Tonnes of oxygen (O₂) required to produce the given amount of methanol.
    H2O_tonnes_required : float
        Tonnes of water (H₂O) required for the reverse reaction.
    CO2_tonnes_produced : float
        Tonnes of carbon dioxide (CO₂) produced in the reaction.
    limiting_reagent : str
        The limiting reagent based on stoichiometry.
    excess_tonnes : float
        Tonnes of any excess reagent after the reaction.
    transfer_coeffs : dict
        Dictionary with 6 keys, e.g.:
          "CHn_meoh": fraction (in %) of CH_n feed that appears in methanol,
          "CHn_co2": fraction (in %) of CH_n feed that appears in CO₂,
          "O2_meoh": fraction (in %) of O₂ feed used in methanol,
          "O2_co2": fraction (in %) of O₂ feed used in CO₂,
          "H2O_meoh": fraction (in %) of water feed that ends up in methanol,
          "H2O_co2": fraction (in %) of water feed that ends up in CO₂.
    """
    if n >= 4:
        raise ValueError(
            "The value of n must be less than 4 for this partial oxidation process."
        )

    # --- Molecular weights (g/mol) ---
    MW_CHn = MW_C + (n * 1.008)

    # --- Convert methanol production to moles ---
    moles_CH4O = (CH4O_tonnes * 1_000_000) / MW_CH4O

    # --- Stoichiometric ratios (per 1 mole of CH4O) from dividing the reaction by (n+2)/3 ---
    ratio_CHn = 6.0 / (n + 2)  # moles CH_n per mole CH4O
    ratio_O2 = 3.0 / (n + 2)  # moles O₂ per mole CH4O
    ratio_H2O = (4.0 - n) / (n + 2)  # moles H₂O input per mole CH4O
    ratio_CO2 = (4.0 - n) / (n + 2)  # moles CO2 output per mole CH4O

    # --- Calculate stoichiometric moles required/produced ---
    moles_CHn_required = ratio_CHn * moles_CH4O
    moles_O2_required = ratio_O2 * moles_CH4O
    moles_H2O_required = ratio_H2O * moles_CH4O
    moles_CO2_produced = ratio_CO2 * moles_CH4O

    # --- Convert moles back to tonnes ---
    CHn_tonnes_required = (moles_CHn_required * MW_CHn) / 1e6
    O2_tonnes_required = (moles_O2_required * MW_O2) / 1e6
    H2O_tonnes_required = (moles_H2O_required * MW_H2O) / 1e6
    CO2_tonnes_produced = (moles_CO2_produced * MW_CO2) / 1e6

    # --- Determine limiting reagent (assuming exactly these stoichiometric amounts are fed) ---
    limiting_moles = min(moles_CHn_required, moles_O2_required, moles_H2O_required)
    if limiting_moles == moles_CHn_required:
        limiting_reagent = "CHn"
        excess_moles_O2 = moles_O2_required - moles_CHn_required
        excess_moles_H2O = moles_H2O_required - moles_CHn_required
        excess_tonnes = (excess_moles_O2 * MW_O2 + excess_moles_H2O * MW_H2O) / 1e6
    elif limiting_moles == moles_O2_required:
        limiting_reagent = "O2"
        excess_moles_CHn = moles_CHn_required - moles_O2_required
        excess_moles_H2O = moles_H2O_required - moles_O2_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_H2O * MW_H2O) / 1e6
    else:
        limiting_reagent = "H2O"
        excess_moles_CHn = moles_CHn_required - moles_H2O_required
        excess_moles_O2 = moles_O2_required - moles_H2O_required
        excess_tonnes = (excess_moles_CHn * MW_CHn + excess_moles_O2 * MW_O2) / 1e6

    # --- Calculate transfer coefficients (TCs) ---
    # 1) Carbon from CH_n is split between CH₄O and CO₂ in proportion to how many carbons end up in each:
    #    2 CH_n => 2n carbons total.  The final eq produces (n+2)/3 moles CH4O => (n+2)/3 carbons,
    #    and (4-n)/3 moles CO₂ => (4-n)/3 carbons.  So:
    frac_CHn_meoh = ((n + 2) / 3) / 2.0  # i.e.  (n+2)/6
    frac_CHn_co2 = ((4.0 - n) / 3) / 2.0  # i.e. (4-n)/6
    # Multiply by 100 to get percentages:
    TC_CHn_meoh = frac_CHn_meoh * 100
    TC_CHn_co2 = frac_CHn_co2 * 100

    # 2) Oxygen from O₂ and from H₂O is split between CH₄O and CO₂:
    #    - Each CH₄O contains 1 oxygen,
    #    - Each CO₂ contains 2 oxygens.
    #    In total, per 1 mole CH₄O we produce (4-n)/3 moles of CO₂ => 2*(4-n)/3 oxygens.
    #    So total oxygens in meoh: 1*(1) = 1; total oxygens in CO2: 2*(4-n)/3.
    #    The ratio => meoh : co2 = 1 : [2*(4-n)/3] = 3 : 2(4-n)
    #    Next we figure how many total oxygens come from O₂ vs H₂O. We do a partition:

    #    (A) O₂ => ratio_O2 moles => each mole has 2 oxygen atoms => total O from O2:
    #        total_O2_atoms = 2 * ratio_O2
    #    (B) H₂O => ratio_H2O moles => each has 1 oxygen => total O from H2O:
    #        total_H2O_atoms = 1 * ratio_H2O
    #    total O input => total_O2_atoms + total_H2O_atoms
    #    Then we define the fraction of O from O₂ that ends up in meoh vs co2, and similarly for H₂O.

    # Number of oxygen atoms in final meoh and co2 for 1 mole CH4O:
    oxy_in_meoh = 1.0
    oxy_in_co2 = 2.0 * ratio_CO2  # ratio_CO2 = (4-n)/(n+2)

    # total oxy in products:
    total_oxy_products = oxy_in_meoh + oxy_in_co2

    # total O from O₂: ratio_O2 moles => each O₂ has 2 oxygen atoms => total_O2_atoms:
    total_O2_atoms = 2.0 * ratio_O2
    # total O from H2O: ratio_H2O moles => each H2O has 1 oxygen => total_H2O_atoms:
    total_H2O_atoms = 1.0 * ratio_H2O
    total_oxy_input = total_O2_atoms + total_H2O_atoms

    # fraction of oxygen from O₂ that goes to methanol:
    # we assume the same fraction of O₂ is used for meoh as the ratio of meoh oxy to total oxy, i.e:
    # O2 fraction that goes to meoh = oxy_in_meoh / total_oxy_products
    # and similarly for CO2.

    if total_oxy_input <= 1e-12:
        # Edge case: if n=4 => partial oxidation eq not valid. or if ratio is 0 => no O2 or H2O
        # but user said n<4 => so let's do a safe check
        O2_meoh = 0.0
        O2_co2 = 0.0
        H2O_meoh = 0.0
        H2O_co2 = 0.0
    else:
        # fraction of total oxy that goes to meoh:
        frac_oxy_meoh = oxy_in_meoh / total_oxy_products
        frac_oxy_co2 = oxy_in_co2 / total_oxy_products
        # fraction of O₂'s oxygen that is in meoh vs co2:
        O2_meoh = frac_oxy_meoh * 100.0
        O2_co2 = frac_oxy_co2 * 100.0
        # fraction of H₂O's oxygen that is in meoh vs co2:
        H2O_meoh = frac_oxy_meoh * 100.0
        H2O_co2 = frac_oxy_co2 * 100.0

    # hydrogen from H₂O presumably goes to methanol (since co2 has no hydrogen).
    # If we wanted to track hydrogen TCs, we could define them. But typically we do for O fraction.

    # Build dictionary
    transfer_coeffs = {
        "CHn_meoh": TC_CHn_meoh,
        "CHn_co2": TC_CHn_co2,
        "O2_meoh": O2_meoh,
        "O2_co2": O2_co2,
        "H2O_meoh": H2O_meoh,
        "H2O_co2": H2O_co2,
    }

    return (
        CHn_tonnes_required,
        O2_tonnes_required,
        H2O_tonnes_required,
        CO2_tonnes_produced,
        limiting_reagent,
        excess_tonnes,
        transfer_coeffs,
    )


def adjusted_reverse_pox_with_TCs(
    CH4O_tonnes: float,
    n: float,
    sg_efficiency: float = 81,
    ms_efficiency: float = 93,
) -> (float, float, float, float, str, float, dict):
    """
    Adjusted partial oxidation (POX) function for methanol production.
    Computes stoichiometric amounts, applies inefficiency scaling,
    identifies limiting reagent, and calculates Transfer Coefficients (TCs)
    for CH_n, O₂, and H₂O among methanol (CH₄O), CO₂, and unreacted feed.

    Reaction (for n < 4, e.g. n=2):
      2 CH_n + O₂ + (4 - n)/3 H₂O → (n + 2)/3 CH₄O + (4 - n)/3 CO₂

    We define usage_multiplier = 1/((sg_efficiency × 0.01) (ms_efficiency× 0.01))
    The fraction 1/usage_multiplier is the “reacted fraction.” The remainder
    is unreacted.

    Each input's Transfer Coefficients (TC) are given as the percentage
    that ends up in methanol, in CO₂, or is unreacted. Summation = 100 %.

    Returns
    -------
    CHn_tonnes_required : float
        Actual feed of hydrocarbon (CH_n).
    O2_tonnes_required : float
        Actual feed of oxygen (O₂).
    H2O_tonnes_required : float
        Actual feed of water (H₂O).
    CO2_tonnes_produced : float
        Tonnes of CO₂ formed stoichiometrically (i.e., for the reacted portion).
    limiting_reagent : str
        Which feed is limiting after the inefficiency scaling.
    excess_tonnes : float
        Tonnage of leftover feed from the other reagents.
    transfer_coeffs : dict
        9 keys: For each input (CHn, O2, H2O):
          • "<input>_meoh"      – fraction (in %) going to methanol
          • "<input>_co2"       – fraction (in %) going to CO₂
          • "<input>_unreacted" – leftover fraction (in %)
        Summation = 100 % per input.
    """
    import math

    if n >= 4:
        raise ValueError("For partial oxidation, n must be < 4 (e.g. n=2).")

    # === Molecular weights (g/mol) ===
    MW_C = 12.010
    MW_CHn = MW_C + (n * 1.008)
    MW_O2 = 32.000
    MW_H2O = 18.015
    MW_CO2 = 44.010
    MW_CH4O = 32.042

    # === Convert target methanol to moles ===
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # === Stoichiometric ratios per 1 mol CH4O ===
    # 2 CH_n + O₂ + (4-n)/3 H₂O => (n+2)/3 CH₄O + (4-n)/3 CO₂
    # Dividing each reactant by (n+2)/3 gives ratios per 1 CH4O:
    ratio_CHn = 6.0 / (n + 2)  # moles CH_n per 1 CH4O
    ratio_O2 = 3.0 / (n + 2)
    ratio_H2O = (4.0 - n) / (n + 2)
    ratio_CO2 = (4.0 - n) / (n + 2)

    # === Ideal stoichiometric moles ===
    ideal_moles_CHn = ratio_CHn * moles_CH4O
    ideal_moles_O2 = ratio_O2 * moles_CH4O
    ideal_moles_H2O = ratio_H2O * moles_CH4O
    ideal_moles_CO2 = ratio_CO2 * moles_CH4O  # produced if all stoich feed reacts

    # === Apply inefficiencies ===
    overall_eff = (sg_efficiency * 0.01) * (ms_efficiency * 0.01)
    usage_multiplier = 1.0 / overall_eff

    moles_CHn_req = ideal_moles_CHn * usage_multiplier
    moles_O2_req = ideal_moles_O2 * usage_multiplier
    moles_H2O_req = ideal_moles_H2O * usage_multiplier
    # We assume only the stoich fraction actually reacts, so CO₂ is from ideal stoich:
    moles_CO2_prod = ideal_moles_CO2

    # === Convert to tonnes ===
    CHn_tonnes_required = (moles_CHn_req * MW_CHn) / 1e6
    O2_tonnes_required = (moles_O2_req * MW_O2) / 1e6
    H2O_tonnes_required = (moles_H2O_req * MW_H2O) / 1e6
    CO2_tonnes_produced = (moles_CO2_prod * MW_CO2) / 1e6

    # === Identify limiting reagent ===
    limiting_moles = min(moles_CHn_req, moles_O2_req, moles_H2O_req)
    if math.isclose(limiting_moles, moles_CHn_req, abs_tol=1e-9):
        limiting_reagent = "CHn"
        # leftover from O2, H2O
        exc_O2 = moles_O2_req - moles_CHn_req
        exc_H2O = moles_H2O_req - moles_CHn_req
        excess_tonnes = (exc_O2 * MW_O2 + exc_H2O * MW_H2O) / 1e6
    elif math.isclose(limiting_moles, moles_O2_req, abs_tol=1e-9):
        limiting_reagent = "O2"
        # leftover from CHn, H2O
        exc_CHn = moles_CHn_req - moles_O2_req
        exc_H2O = moles_H2O_req - moles_O2_req
        excess_tonnes = (exc_CHn * MW_CHn + exc_H2O * MW_H2O) / 1e6
    else:
        limiting_reagent = "H2O"
        # leftover from CHn, O2
        exc_CHn = moles_CHn_req - moles_H2O_req
        exc_O2 = moles_O2_req - moles_H2O_req
        excess_tonnes = (exc_CHn * MW_CHn + exc_O2 * MW_O2) / 1e6

    # === Transfer Coefficients ===
    # The fraction that reacts is (1/usage_multiplier).
    # For CHn: stoichiometry indicates 2 CH_n => 1.0 fraction of carbon to {CH4O + CO2}.
    # The portion that forms CH4O vs CO2 is ~ (n+2)/(4n + ???).
    # We'll keep the simplified approach from your existing code:

    used_fraction = 1.0 / usage_multiplier  # fraction that actually reacts

    # 1) CH_n
    #   partial-oxidation stoichiometry => fraction to meoh = (n+2)/6
    #                                     fraction to co2  = (4-n)/6
    frac_CHn_meoh_stoich = (n + 2) / 6.0
    frac_CHn_co2_stoich = (4.0 - n) / 6.0
    CHn_meoh = used_fraction * frac_CHn_meoh_stoich
    CHn_co2 = used_fraction * frac_CHn_co2_stoich
    CHn_unreacted = 1.0 - (CHn_meoh + CHn_co2)

    # 2) O₂
    #   We distribute the reacted portion between meoh vs co2 as in your code:
    #   meoh needs 1 oxygen, co2 has 2*(4-n)/3, etc.
    #   Then we scale by used_fraction.
    oxy_in_meoh = 1.0
    oxy_in_co2 = 2.0 * ratio_CO2  # ratio_CO2 = (4-n)/(n+2)
    total_oxy = oxy_in_meoh + oxy_in_co2
    frac_oxy_meoh = oxy_in_meoh / total_oxy
    frac_oxy_co2 = oxy_in_co2 / total_oxy

    O2_meoh = used_fraction * frac_oxy_meoh
    O2_co2 = used_fraction * frac_oxy_co2
    O2_unreacted = 1.0 - (O2_meoh + O2_co2)

    # 3) H₂O
    #   same approach as O2 for the fraction that reacts
    H2O_meoh = used_fraction * frac_oxy_meoh
    H2O_co2 = used_fraction * frac_oxy_co2
    H2O_unreacted = 1.0 - (H2O_meoh + H2O_co2)

    # convert to percentage
    CHn_meoh_pct = CHn_meoh * 100
    CHn_co2_pct = CHn_co2 * 100
    CHn_unr_pct = CHn_unreacted * 100

    O2_meoh_pct = O2_meoh * 100
    O2_co2_pct = O2_co2 * 100
    O2_unr_pct = O2_unreacted * 100

    H2O_meoh_pct = H2O_meoh * 100
    H2O_co2_pct = H2O_co2 * 100
    H2O_unr_pct = H2O_unreacted * 100

    # small checks
    assert abs((CHn_meoh + CHn_co2 + CHn_unreacted) - 1.0) < 1e-5
    assert abs((O2_meoh + O2_co2 + O2_unreacted) - 1.0) < 1e-5
    assert abs((H2O_meoh + H2O_co2 + H2O_unreacted) - 1.0) < 1e-5

    transfer_coeffs = {
        "CHn_meoh": CHn_meoh_pct,
        "CHn_co2": CHn_co2_pct,
        "CHn_unreacted": CHn_unr_pct,
        "O2_meoh": O2_meoh_pct,
        "O2_co2": O2_co2_pct,
        "O2_unreacted": O2_unr_pct,
        "H2O_meoh": H2O_meoh_pct,
        "H2O_co2": H2O_co2_pct,
        "H2O_unreacted": H2O_unr_pct,
    }

    return (
        CHn_tonnes_required,
        O2_tonnes_required,
        H2O_tonnes_required,
        CO2_tonnes_produced,
        limiting_reagent,
        excess_tonnes,
        transfer_coeffs,
    )


#####################################################################################################################################
# The following equations are sourced from [3]
#####################################################################################################################################


# Steam reforming reactions
def steam_reforming_general(
    CmHn: float, H2O: float, m: int, n: int
) -> (float, float, str, str, float):
    """
    General steam reforming reaction for hydrocarbons,
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows:
    CmHn + mH2O -> mCO + (m + n/2)H2    DELTA_H = +203/+206 kJ/mol

    Parameters:
    - CmHn: float, tonnes of hydrocarbon.
    - H2O: float, tonnes of water.
    - m: int, number of carbon atoms in the hydrocarbon.
    - n: int, number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Calculate the molecular weight of the hydrocarbon
    MW_CmHn = (12.01 * m) + (1.008 * n)

    # Convert tonnes to moles (1 tonne = 1e6 grams)
    moles_CmHn = (CmHn * 1e6) / MW_CmHn
    moles_H2O = (H2O * 1e6) / MW_H2O

    # Determine the limiting reagent
    limiting_reagent = "CmHn" if moles_CmHn < moles_H2O / m else "H2O"
    moles_reacted = min(moles_CmHn, moles_H2O / m)

    # Calculate products
    CO_tonnes = (m * moles_reacted * MW_CO) / 1e6
    H2_tonnes = ((m + n / 2) * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CmHn":
        excess_reagent = "H2O"
        excess_moles = moles_H2O - (m * moles_reacted)
    else:
        excess_reagent = "CmHn"
        excess_moles = moles_CmHn - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_H2O if excess_reagent == "H2O" else MW_CmHn)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def steam_reforming_methane(
    CH4_tonnes: float, H2O_tonnes: float
) -> (float, float, str, str, float):
    """
    Steam reforming of methane,
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows:
    CH4 + H2O -> CO + 3H2  DELTA_H = +203/+206 kJ/mol

    Parameters:
    - CH4_tonnes: float, tonnes of methane.
    - H2O_tonnes: float, tonnes of water.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4 = (CH4_tonnes * 1e6) / MW_CH4
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Determine the limiting reagent
    limiting_reagent = "CH4" if moles_CH4 < moles_H2O / 1 else "H2O"
    moles_reacted_CH4 = min(moles_CH4, moles_H2O / 1)
    moles_reacted_H2O = (
        1 * moles_reacted_CH4
    )  # Because 1 moles of H2O are needed per mole of CH4

    # Calculate products
    CO_tonnes = (moles_reacted_CH4 * MW_CO) / 1e6
    H2_tonnes = (3 * moles_reacted_CH4 * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CH4":
        excess_reagent = "H2O"
        excess_moles = moles_H2O - moles_reacted_H2O
    else:
        excess_reagent = "CH4"
        excess_moles = moles_CH4 - moles_reacted_CH4

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CH4 if excess_reagent == "CH4" else MW_H2O)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def csr_input_requirements(
    CO_tonnes: float, H2_tonnes: float
) -> (float, float, str, float):
    """
    Calculate the input requirements for steam methane reforming based on the desired syngas output.

    The reaction is as follows (for the reverse process):
    CO + 3H2 -> CH4 + H2O  DELTA_H = -203/-206 kJ/mol

    Parameters:
    - CO_tonnes: float, tonnes of carbon monoxide.
    - H2_tonnes: float, tonnes of hydrogen.

    Returns:
    - float, tonnes of methane required.
    - float, tonnes of water required.
    - str, the reagent that is in excess.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles for CO and H2
    moles_CO = CO_tonnes * 1e6 / MW_CO
    moles_H2 = H2_tonnes * 1e6 / MW_H2

    # Determine the limiting reagent
    limiting_reagent = "CO" if moles_CO < moles_H2 / 3 else "H2"
    moles_reacted = min(moles_CO, moles_H2 / 3)

    # Calculate products
    CH4_tonnes_req = (moles_reacted * MW_CH4) / 1e6
    H2O_tonnes_req = (moles_reacted * MW_H2O) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CO":
        excess_reagent = "H2"
        excess_moles = moles_H2 - (3 * moles_reacted)
    else:
        excess_reagent = "CO"
        excess_moles = moles_CO - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_H2 if excess_reagent == "H2" else MW_CO)) / 1e6

    return CH4_tonnes_req, H2O_tonnes_req, excess_reagent, excess_tonnes


# Partial oxidation reactions
def partial_oxidation_general(
    CmHn_tonnes: float, O2_tonnes: float, m: int, n: int
) -> (float, float, str, str, float):
    """
    General partial oxidation reaction for hydrocarbons to carbon monoxide and hydrogen,
    also identifies the limiting and excess reagents and the excess amount.

    The reaction is as follows:
    CmHn + (m/2)O2 -> mCO + (n/2)H2     DELTA_H = -41 kJ/mol

    Parameters:
    - CmHn_tonnes: float, tonnes of hydrocarbon (CmHn).
    - O2_tonnes: float, tonnes of oxygen.
    - m: int, number of carbon atoms in the hydrocarbon.
    - n: int, number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    MW_CmHn = (12.01 * m) + (1.008 * n)

    # Convert tonnes to moles
    moles_CmHn = (CmHn_tonnes * 1e6) / MW_CmHn
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "CmHn" if moles_CmHn < (moles_O2 * 2 / m) else "O2"
    moles_reacted = min(moles_CmHn, moles_O2 * 2 / m)

    # Calculate products
    CO_tonnes = (m * moles_reacted * MW_CO) / 1e6
    H2_tonnes = ((n / 2) * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CmHn":
        excess_reagent = "O2"
        excess_moles = moles_O2 - (moles_reacted * m / 2)
    else:
        excess_reagent = "CmHn"
        excess_moles = moles_CmHn - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CmHn if excess_reagent == "CmHn" else MW_O2)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def partial_oxidation_of_methane(
    CH4_tonnes: float, O2_tonnes: float
) -> (float, float, str, str, float):
    """
    Partial oxidation of methane to carbon monoxide and hydrogen,
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows (Equation 4.4 in [1]):
    CH4 + 1/2O2 -> CO + 2H2    DELTA_H = -41 kJ/mol

    Parameters:
    - CH4_tonnes: float, tonnes of methane.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4 = (CH4_tonnes * 1e6) / MW_CH4
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "CH4" if moles_CH4 < (moles_O2 * 2) else "O2"
    moles_reacted = min(moles_CH4, moles_O2 * 2)

    # Calculate products
    CO_tonnes = (moles_reacted * MW_CO) / 1e6
    H2_tonnes = (2 * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CH4":
        excess_reagent = "O2"
        excess_moles = moles_O2 - (moles_reacted / 2)
    else:
        excess_reagent = "CH4"
        excess_moles = moles_CH4 - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CH4 if excess_reagent == "CH4" else MW_O2)
    ) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def partial_oxidation_of_methanol(
    CH4O_tonnes: float, O2_tonnes: float
) -> (float, float, str, str, float):
    """
    Partial oxidation of methanol to carbon dioxide and hydrogen (Equation 4.6 in [1]),
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon dioxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.

    Notes:
    The reaction is as follows, with all quantities in moles:
    CH4O + 1/2O2 -> CO2 + 2H2
    """
    # Convert tonnes to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "CH4O" if moles_CH4O < (moles_O2 * 2) else "O2"
    moles_reacted = min(moles_CH4O, moles_O2 * 2)

    # Calculate products
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6
    H2_tonnes = (2 * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CH4O":
        excess_reagent = "O2"
        excess_moles = moles_O2 - (moles_reacted / 2)
    else:
        excess_reagent = "CH4O"
        excess_moles = moles_CH4O - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CH4O if excess_reagent == "CH4O" else MW_O2)
    ) / 1e6

    return CO2_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def direct_partial_oxidation_of_methanol(
    CH4O_tonnes: float,
) -> (float, float, str, float):
    """
    Direct partial oxidation of methanol to carbon monoxide and hydrogen, with inputs in tonnes and outputs in tonnes (Equation 4.7 in [1]).

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, indicating the reactant 'CH4O' as it's directly converted.
    - float, the amount of reactant used (tonnes), equal to the input as all is converted.

    Notes:
    The reaction is as follows, with all quantities in tonnes:
    CH4O -> CO + 2H2    DELTA_H = -44 kJ/mol
    """
    # Convert tonnes to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # Calculate products
    CO_tonnes = (moles_CH4O * MW_CO) / 1e6
    H2_tonnes = (2 * moles_CH4O * MW_H2) / 1e6

    # Since the reaction converts all methanol, there's no excess reactant
    reactant_used_tonnes = CH4O_tonnes

    return CO_tonnes, H2_tonnes, "CH4O", reactant_used_tonnes


# Autothermal reforming reactions


def autothermal_reforming_general(
    CmHn_tonnes: float, H2O_tonnes: float, O2_tonnes: float, m: int, n: int
) -> (float, float, str, str, float):
    """
    General autothermal reforming reaction for hydrocarbons to carbon monoxide and hydrogen, with inputs in tonnes and outputs in tonnes (Equation 4.9 in [1]).
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows, with all quantities in tonnes:
    CmHn + m/2H2O + m/4O2 -> mCO + (m/2 + n/2)H2

    Parameters:
    - CmHn_tonnes: float, tonnes of hydrocarbon (CmHn).
    - H2O_tonnes: float, tonnes of water.
    - O2_tonnes: float, tonnes of oxygen.
    - m: int, number of carbon atoms in the hydrocarbon.
    - n: int, number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    MW_CmHn = (12.01 * m) + (
        1.008 * n
    )  # Calculate the molecular weight of the hydrocarbon

    # Convert tonnes to moles
    moles_CmHn = (CmHn_tonnes * 1e6) / MW_CmHn
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent_ratios = {
        "CmHn": moles_CmHn,
        "H2O": moles_H2O / (m / 2),
        "O2": moles_O2 / (m / 4),
    }
    limiting_reagent = min(limiting_reagent_ratios, key=limiting_reagent_ratios.get)
    moles_reacted = limiting_reagent_ratios[limiting_reagent]

    # Calculate products
    CO_tonnes = (m * moles_reacted * MW_CO) / 1e6
    H2_tonnes = ((m / 2 + n / 2) * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    excess_amounts = {
        "CmHn": moles_CmHn - moles_reacted,
        "H2O": moles_H2O - (moles_reacted * (m / 2)),
        "O2": moles_O2 - (moles_reacted * (m / 4)),
    }
    excess_reagent, excess_moles = max(excess_amounts.items(), key=lambda x: x[1])

    # Lookup the molecular weight for the excess reagent
    MW_excess_reagent = (
        MW_CmHn
        if excess_reagent == "CmHn"
        else MW_H2O
        if excess_reagent == "H2O"
        else MW_O2
    )

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * MW_excess_reagent) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def autothermal_reforming_of_methane(
    CH4_tonnes: float, H2O_tonnes: float, O2_tonnes: float
) -> (float, float, str, str, float):
    """
    Autothermal reforming of methane to carbon monoxide and hydrogen,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.8 in [1])..

    The reaction is as follows, with all quantities in tonnes:
    CH4 + 1/2H2O + 1/4O2 -> CO + 2.5H2
    Parameters
    - CH4_tonnes: float, tonnes of methane.
    - H2O_tonnes: float, tonnes of water.
    - O2_tonnes: float, tonnes of oxygen.

    Returns
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4 = (CH4_tonnes * 1e6) / MW_CH4
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent based on stoichiometry
    limiting_ratio_CH4 = moles_CH4
    limiting_ratio_H2O = moles_H2O * 2  # For 1/2 H2O per CH4
    limiting_ratio_O2 = moles_O2 * 4  # For 1/4 O2 per CH4

    limiting_reagent = min(
        ("CH4", limiting_ratio_CH4),
        ("H2O", limiting_ratio_H2O),
        ("O2", limiting_ratio_O2),
        key=lambda x: x[1],
    )[0]

    moles_reacted = min(limiting_ratio_CH4, limiting_ratio_H2O, limiting_ratio_O2)

    # Calculate products based on the moles of the limiting reactant
    CO_tonnes = (moles_reacted * MW_CO) / 1e6
    H2_tonnes = (2.5 * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    excess_amounts = {
        "CH4": moles_CH4 - moles_reacted,
        "H2O": moles_H2O - (moles_reacted / 2),
        "O2": moles_O2 - (moles_reacted / 4),
    }
    excess_reagent, excess_moles = max(excess_amounts.items(), key=lambda x: x[1])

    # Convert excess moles back to tonnes
    MW_excess = (
        MW_CH4
        if excess_reagent == "CH4"
        else MW_H2O
        if excess_reagent == "H2O"
        else MW_O2
    )
    excess_tonnes = (excess_moles * MW_excess) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def syngas_production_from_atr(
    CO_tonnes: float, H2_tonnes: float
) -> (float, float, float):
    """
    Autothermal reforming (ATR) for syngas production is represented by the reaction:

        CH₄ + ½ H₂O + ½ O₂ → CO + 5⁄2 H₂

    This function performs a backward calculation: given the produced syngas amounts of CO and H₂
    (in tonnes), it calculates the required inputs in tonnes:
      - Methane (CH₄),
      - Water (H₂O), and
      - Oxygen (O₂).

    Parameters
    ----------
    CO_tonnes : float
        Tonnes of carbon monoxide (CO) produced.
    H2_tonnes : float
        Tonnes of hydrogen (H₂) produced.

    Returns
    -------
    CH4_tonnes_req : float
        Tonnes of methane (CH₄) required.
    H2O_tonnes_req : float
        Tonnes of water (H₂O) required.
    O2_tonnes_req  : float
        Tonnes of oxygen (O₂) required.
    """
    # Convert final CO and H2 from tonnes to moles
    moles_CO = (CO_tonnes * 1e6) / MW_CO
    moles_H2 = (H2_tonnes * 1e6) / MW_H2

    # Stoichiometric ratio: 2.5 moles H2 per 1 mole CO
    # If actual H2 is at least 2.5 times CO, CO is limiting; otherwise H2 is limiting.
    ratio_needed = 2.5
    ratio_actual = moles_H2 / moles_CO if moles_CO > 0 else 0.0

    if ratio_actual >= ratio_needed:
        # CO is limiting
        moles_reacted_CO = moles_CO
    else:
        # H2 is limiting
        moles_reacted_CO = moles_H2 / ratio_needed

    # From the stoichiometry:
    # For each 1 mole CO produced => 1 mole CH4, 0.5 mole H2O, 0.5 mole O2
    # So if we produce "moles_reacted_CO" moles of CO, we need the same for CH4, half for H2O, half for O2.
    moles_CH4_req = moles_reacted_CO
    moles_H2O_req = 0.5 * moles_reacted_CO
    moles_O2_req = 0.5 * moles_reacted_CO

    # Convert back to tonnes
    CH4_tonnes_req = (moles_CH4_req * MW_CH4) / 1e6
    H2O_tonnes_req = (moles_H2O_req * MW_H2O) / 1e6
    O2_tonnes_req = (moles_O2_req * MW_O2) / 1e6

    return CH4_tonnes_req, H2O_tonnes_req, O2_tonnes_req


def autothermal_reforming_of_methanol(
    CH4O_tonnes: float, H2O_tonnes: float, O2_tonnes: float
) -> (float, float, str, str, float):
    """
    Autothermal reforming of methanol to carbon dioxide and hydrogen,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.10 in [1]).

    The reaction is as follows, with all quantities in tonnes:
    CH4O + 1/2H2O + 1/4O2 -> CO2 + 2.5H2      DELTA_H = -44 kJ/mol

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol.
    - H2O_tonnes: float, tonnes of water.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon dioxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent based on stoichiometry
    limiting_ratio = {
        "CH4O": moles_CH4O,
        "H2O": moles_H2O * 2,  # Adjust for 1/2 H2O
        "O2": moles_O2 * 4,  # Adjust for 1/4 O2
    }
    limiting_reagent = min(limiting_ratio, key=limiting_ratio.get)
    moles_reacted = limiting_ratio[limiting_reagent]

    if limiting_reagent == "CH4O":
        moles_reacted_CH4O = moles_reacted
    elif limiting_reagent == "H2O":
        moles_reacted_CH4O = moles_reacted / 2
    else:  # O2 is the limiting reagent
        moles_reacted_CH4O = moles_reacted / 4

    # Calculate products
    CO2_tonnes = (moles_reacted_CH4O * MW_CO2) / 1e6
    H2_tonnes = (2.5 * moles_reacted_CH4O * MW_H2) / 1e6

    # Calculate excess of each reactant
    excess_moles_CH4O = moles_CH4O - moles_reacted_CH4O
    excess_moles_H2O = moles_H2O - (moles_reacted_CH4O / 2)
    excess_moles_O2 = moles_O2 - (moles_reacted_CH4O / 4)

    # Identify and calculate the excess reagent and its amount
    excess_reagent, excess_moles = max(
        [
            ("CH4O", excess_moles_CH4O),
            ("H2O", excess_moles_H2O),
            ("O2", excess_moles_O2),
        ],
        key=lambda x: x[1],
    )

    # Convert excess moles back to tonnes
    MW_excess = {
        "CH4O": MW_CH4O,
        "H2O": MW_H2O,
        "O2": MW_O2,
    }[excess_reagent]
    excess_tonnes = (excess_moles * MW_excess) / 1e6

    return CO2_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


# Combined reforming reactions
def combined_reforming(
    CH4_tonnes: float, O2_tonnes: float
) -> (float, float, float, str, float):
    """
    Implements the combined reforming process for methanol synthesis from methane.

    Based on the stoichiometry of the reactions:
    CH4 + 1/2 O2 -> CO + 2 H2
    Followed by: CO + 2 H2 -> CH4O    DELTA_H = -98 kJ mol-1

    Parameters:
    - CH4_tonnes: tonnes of methane.
    - O2_tonnes: tonnes of oxygen.

    Returns:
    - tonnes of methanol produced.
    - tonnes of carbon monoxide produced.
    - tonnes of hydrogen produced.
    - The limiting reactant.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4 = CH4_tonnes * 1e6 / MW_CH4
    moles_O2 = O2_tonnes * 1e6 / MW_O2

    # Determine the limiting reactant
    limiting_reagent = "CH4" if moles_CH4 < moles_O2 * 2 else "O2"
    moles_reacted_CH4 = min(moles_CH4, moles_O2 * 2)
    moles_reacted_O2 = moles_reacted_CH4 / 2

    # Assuming that all reacted methane converts to methanol
    # moles_CH4O_produced = moles_reacted_CH4
    moles_CO_produced = moles_reacted_CH4
    moles_H2_produced = moles_CO_produced * 2  # From the first reaction

    # Excess reactant calculations
    excess_amount = 0
    if limiting_reagent == "CH4":
        excess_O2 = moles_O2 - moles_reacted_O2
        excess_amount = excess_O2 * MW_O2 / 1e6
        excess_reagent = "O2"
    else:
        excess_CH4 = moles_CH4 - moles_reacted_CH4
        excess_amount = excess_CH4 * MW_CH4 / 1e6
        excess_reagent = "CH4"

    # Convert moles of produced methanol back to tonnes
    # CH4O_tonnes_produced = moles_CH4O_produced * MW_CH4O / 1e6
    CO_tonnes_produced = moles_CO_produced * MW_CO / 1e6
    H2_tonnes_produced = moles_H2_produced * MW_H2 / 1e6

    return (
        CO_tonnes_produced,
        H2_tonnes_produced,
        limiting_reagent,
        excess_reagent,
        excess_amount,
    )


def reverse_combined_reforming(CH4O_tonnes: float) -> (float, float, float, float):
    """
    Estimates the required methane (CH4) and oxygen (O2) to produce a given amount of methanol (CH4O)
    and calculates the amounts of carbon monoxide (CO) and hydrogen (H2) produced
    for the Combined Reforming Process.

    Based on the stoichiometry of the reactions:
    Methanol Steam Reforming Reaction: CO + 2 H2 -> CH4O
    Followed by: CH4 + 1/2 O2 -> CO + 2 H2

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol (CH4O) to be produced.

    Returns:
    - float, tonnes of methane (CH4) required.
    - float, tonnes of oxygen (O2) required.
    - float, tonnes of carbon monoxide (CO) produced.
    - float, tonnes of hydrogen (H2) produced.
    """
    # Convert tonnes of methanol to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # Stoichiometry for methanol steam reforming (reversed):
    # Producing 1 mole of CH4O consumes 1 mole of CO and 2 moles of H2
    moles_CO_produced = moles_CH4O
    moles_H2_produced = 2 * moles_CH4O

    # Stoichiometry for subsequent methane and oxygen reaction:
    # Producing 1 mole of CO and 2 moles of H2 requires 1 mole of CH4 and 1/2 mole of O2
    moles_CH4_required = moles_CO_produced
    moles_O2_required = moles_CO_produced / 2

    # Convert moles back to tonnes
    CH4_required_tonnes = (moles_CH4_required * MW_CH4) / 1e6
    O2_required_tonnes = (moles_O2_required * MW_O2) / 1e6
    CO_produced_tonnes = (moles_CO_produced * MW_CO) / 1e6
    H2_produced_tonnes = (moles_H2_produced * MW_H2) / 1e6

    return (
        CH4_required_tonnes,
        O2_required_tonnes,
        CO_produced_tonnes,
        H2_produced_tonnes,
    )


def water_gas_shift_from_CO_H2(
    CO_tonnes: float, H2_tonnes: float
) -> (float, float, str, str, float):
    """
    Calculates the missing water input and the amount of CO₂ produced for the water-gas shift reaction:

        CO + H₂O -> CO₂ + H₂

    The known inputs are the masses of CO and H₂ (in tonnes). Using the stoichiometric ratios,
    the function calculates:
      - The tonnes of water (H₂O) required (since the reaction is 1:1 between CO and H₂O),
      - The tonnes of CO₂ produced (1:1 with CO),
      - The limiting reagent (based on a 1:1 ratio between CO and H₂O),
      - The excess reagent, and
      - The tonnes of the excess reagent remaining.

    All units are in tonnes. (Remember: 1 tonne = 1,000,000 g.)

    Parameters
    ----------
    CO_tonnes : float
        Tonnes of carbon monoxide (CO) available.
    H2_tonnes : float
        Tonnes of hydrogen (H₂) produced (or available).

    Returns
    -------
    H2O_tonnes_required : float
        Tonnes of water (H₂O) required for the reaction.
    CO2_tonnes_produced : float
        Tonnes of carbon dioxide (CO₂) produced.
    limiting_reagent : str
        The reagent that is limiting ("CO" or "H₂").
    excess_reagent : str
        The reagent that is in excess.
    excess_tonnes : float
        Tonnes of the excess reagent remaining.
    """
    # --- Convert input masses from tonnes to moles ---
    moles_CO = (CO_tonnes * 1e6) / MW_CO
    moles_H2 = (H2_tonnes * 1e6) / MW_H2

    # --- For the reaction CO + H₂O -> CO₂ + H₂, the ideal stoichiometry is 1:1:1:1.
    # Since H₂ is a product, if we assume perfect conversion, the moles of H₂ produced should equal the moles of CO reacted.
    # To determine the limiting reagent among the inputs (CO and the water that must be supplied),
    # we compare moles_CO with the moles of H₂ (since, ideally, moles_CO should equal moles_H2).
    #
    # Here, we use the known CO and H₂ values (which are measured from the process).
    # If moles_CO is less than moles_H2, then CO is the limiting reagent and the required water (and hence CO₂ produced)
    # will equal moles_CO; water must be supplied in an amount equal to moles_CO.
    # Otherwise, H₂ is limiting, and water required equals moles_H2.

    if moles_CO < moles_H2:
        limiting_reagent = "CO"
        excess_reagent = "H₂"
        moles_reacted = moles_CO
        excess_moles = moles_H2 - moles_CO
    else:
        limiting_reagent = "H₂"
        excess_reagent = "CO"
        moles_reacted = moles_H2
        excess_moles = moles_CO - moles_H2

    # --- Calculate water required and CO₂ produced based on the limiting reagent ---
    # In the reaction, 1 mole of CO reacts with 1 mole of H₂O to produce 1 mole of CO₂ and 1 mole of H₂.
    moles_H2O_required = moles_reacted  # since the ratio is 1:1 for CO and H₂O.
    moles_CO2_produced = moles_reacted  # since 1 mole CO yields 1 mole CO₂.

    # --- Convert these moles back to tonnes ---
    H2O_tonnes_required = (moles_H2O_required * MW_H2O) / 1e6
    CO2_tonnes_produced = (moles_CO2_produced * MW_CO2) / 1e6

    # --- Convert excess moles of the non-limiting reagent back to tonnes ---
    if limiting_reagent == "CO":
        excess_tonnes = (excess_moles * MW_H2) / 1e6
    else:
        excess_tonnes = (excess_moles * MW_CO) / 1e6

    return (
        H2O_tonnes_required,
        CO2_tonnes_produced,
        limiting_reagent,
        excess_reagent,
        excess_tonnes,
    )


def water_gas_shift(
    CO_tonnes: float, H2O_tonnes: float
) -> (float, float, str, str, float):
    """
    Water-gas shift reaction to produce carbon dioxide and hydrogen,
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows, with all quantities in tonnes:
    CO + H2O -> CO2 + H2         DELTA_H = -41.2 kJ/mol

    Parameters
    - CO_tonnes: float, tonnes of carbon monoxide.
    - H2O_tonnes: float, tonnes of water.

    Returns
    - float, tonnes of carbon dioxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """

    # Convert tonnes to moles
    moles_CO = (CO_tonnes * 1e6) / MW_CO
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Determine the limiting reagent
    if moles_CO < moles_H2O:
        limiting_reagent = "CO"
        moles_reacted = moles_CO
        excess_reagent = "H2O"
        excess_moles = moles_H2O - moles_reacted
        excess_tonnes = (excess_moles * MW_H2O) / 1e6
    else:
        limiting_reagent = "H2O"
        moles_reacted = moles_H2O
        excess_reagent = "CO"
        excess_moles = moles_CO - moles_reacted
        excess_tonnes = (excess_moles * MW_CO) / 1e6

    # Calculate products
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6
    H2_tonnes = (moles_reacted * MW_H2) / 1e6

    return CO2_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def reverse_water_gas_shift(
    CO2_tonnes: float, H2_tonnes: float
) -> (float, float, str, str, float):
    """
    Reverse water-gas shift reaction to produce carbon monoxide and water,
    Also identifies the limiting reagent, excess reagent, and the excess amount(Equation 4.20 in [1]).

    The reaction is as follows, with all quantities in tonnes:
    CO2 + H2 -> CO + H2O        DELTA_H = +41.2 kJ/mol

    Parameters
    - CO2_tonnes: float, tonnes of carbon dioxide.
    - H2_tonnes: float, tonnes of hydrogen.

    Returns
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of water produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CO2 = (CO2_tonnes * 1e6) / MW_CO2
    moles_H2 = (H2_tonnes * 1e6) / MW_H2

    # Determine the limiting reagent
    limiting_reagent = "CO2" if moles_CO2 < moles_H2 else "H2"
    moles_reacted = min(moles_CO2, moles_H2)

    # Calculate products
    CO_tonnes = (moles_reacted * MW_CO) / 1e6
    H2O_tonnes = (moles_reacted * MW_H2O) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CO2":
        excess_reagent = "H2"
        excess_moles = moles_H2 - moles_reacted
    else:
        excess_reagent = "CO2"
        excess_moles = moles_CO2 - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_H2 if excess_reagent == "H2" else MW_CO2)) / 1e6

    return CO_tonnes, H2O_tonnes, limiting_reagent, excess_reagent, excess_tonnes


# Methanol (Methyl alcohol) synthesis reactions
def reverse_co2_hydrogenation_alt_a(
    CH4O_tonnes: float, H2O_tonnes: float
) -> (float, float, str, str, float):
    """
    Reverse carbon dioxide hydrogenation reaction to produce carbon dioxide and hydrogen,
    with inputs in tonnes and outputs in tonnes.
    Also identifies the limiting reagent, excess reagent, and the excess amount.

    The reaction is as follows (Equation 4.3 in [1]):
    CH4O + H2O -> CO2 + 3H2 DELTA_H = +49.5 kJ/mol

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol.
    - H2O_tonnes: float, tonnes of water.

    Returns:
    - float, tonnes of carbon dioxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Determine the limiting reagent
    limiting_reagent = "CH4O" if moles_CH4O < moles_H2O else "H2O"
    moles_reacted = min(moles_CH4O, moles_H2O)

    # Calculate products
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6
    H2_tonnes = (3 * moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CH4O":
        excess_reagent = "H2O"
        excess_moles = moles_H2O - moles_reacted
    else:
        excess_reagent = "CH4O"
        excess_moles = moles_CH4O - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (
        excess_moles * (MW_CH4O if excess_reagent == "CH4O" else MW_H2O)
    ) / 1e6

    return CO2_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def co_hydrogenation(CO_tonnes: float, H2_tonnes: float) -> (float, str, str, float):
    """
    Carbon monoxide hydrogenation reaction to produce methanol (CH4O),
    with inputs in tonnes and outputs in tonnes.
    The molecular weights for CO, H2, and CH4O are constants defined outside the function.

    The reaction is as follows:
    CO + 2H2 <-> CH4O   DELTA_H = -90.7 kJ/mol  (Equation 12 in [2])

    Parameters:
    - CO_tonnes: float, tonnes of carbon monoxide.
    - H2_tonnes: float, tonnes of hydrogen.

    Returns:
    - float, tonnes of methanol produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # 1) Convert feed (in tonnes) to moles
    moles_CO = (CO_tonnes * 1e6) / MW_CO
    moles_H2 = (H2_tonnes * 1e6) / MW_H2

    # 2) Determine the limiting reagent (stoichiometry: 1 mole CO : 2 moles H2)
    #    If CO is limiting, then moles_CO < (moles_H2 / 2). Otherwise, H2 is limiting.
    if moles_CO < (moles_H2 / 2.0):
        limiting_reagent = "CO"
        moles_reacted_CO = moles_CO
        moles_reacted_H2 = 2.0 * moles_CO
        excess_reagent = "H2"
        leftover_moles = moles_H2 - moles_reacted_H2
        excess_mw = MW_H2
    else:
        limiting_reagent = "H2"
        moles_reacted_H2 = moles_H2
        moles_reacted_CO = moles_H2 / 2.0
        excess_reagent = "CO"
        leftover_moles = moles_CO - moles_reacted_CO
        excess_mw = MW_CO

    # 3) Calculate methanol production
    #    Reaction: 1 mole CO -> 1 mole CH4O
    #    so the moles of methanol = moles_reacted_CO
    moles_CH4O = moles_reacted_CO

    # 4) Convert stoichiometric amounts back to tonnes
    CH4O_tonnes = (moles_CH4O * MW_CH4O) / 1e6
    CO_tonnes_consumed = (moles_reacted_CO * MW_CO) / 1e6
    H2_tonnes_consumed = (moles_reacted_H2 * MW_H2) / 1e6
    excess_tonnes = (leftover_moles * excess_mw) / 1e6

    return (
        CH4O_tonnes,
        CO_tonnes_consumed,
        H2_tonnes_consumed,
        limiting_reagent,
        excess_reagent,
        excess_tonnes,
    )


def reverse_co_hydrogenation(CH4O_tonnes: float) -> (float, float):
    """
    Estimates the tonnes of carbon monoxide (CO) and hydrogen (H2) needed to produce a given amount of methanol (CH4O).
    The reaction is as follows:
    CO + 2H2 <-> CH4O   DELTA_H = +90.7 kJ/mol  (Equation 12 in [2])

    Parameters:
    - CH4O_tonnes: float, tonnes of methanol to be produced.

    Returns:
    - float, tonnes of carbon monoxide (CO) required.
    - float, tonnes of hydrogen (H2) required.
    """
    # Convert tonnes to moles
    moles_CH4O = CH4O_tonnes * 1e6 / MW_CH4O

    # From the stoichiometry of the reaction, we know that:
    # 1 mole of CO produces 1 mole of CH4O
    # 2 moles of H2 are needed to produce 1 mole of CH4O

    # Calculate moles of CO and H2 needed
    moles_CO_needed = moles_CH4O  # Because 1 CO -> 1 CH4O
    moles_H2_needed = moles_CH4O * 2  # Because 2 H2 -> 1 CH4O

    # Convert moles back to tonnes
    CO_tonnes_req = moles_CO_needed * MW_CO / 1e6
    H2_tonnes_req = moles_H2_needed * MW_H2 / 1e6

    return CO_tonnes_req, H2_tonnes_req


def reverse_co2_hydrogenation(CH4O_tonnes: float) -> (float, float):
    """
    Calculates the tonnes of carbon dioxide (CO₂) and hydrogen (H₂) required to produce a given amount of methanol (CH₄O) via the reverse CO₂ hydrogenation reaction.

    The reaction is:
        CO₂ + 3H₂ → CH₄O + H₂O

    Parameters
    ----------
    CH4O_tonnes : float
        Tonnes of methanol (CH₄O) to be produced.

    Returns
    -------
    CO2_tonnes : float
        Tonnes of carbon dioxide (CO₂) required.
    H2_tonnes : float
        Tonnes of hydrogen (H₂) required.
    H2O_tonnes_required : float
        Tonnes of water (H₂O) produced as by-product.
    """
    # 1) Convert the given methanol from tonnes to moles
    moles_CH4O = (CH4O_tonnes * 1e6) / MW_CH4O

    # 2) Stoichiometric ratios:
    #    - 1 mole CH4O requires 1 mole H2O
    #    - 1 mole CH4O produces 1 mole CO2 and 3 moles H2
    moles_H2O_required = moles_CH4O
    moles_CO2_produced = moles_CH4O
    moles_H2_produced = 3.0 * moles_CH4O

    # 3) Convert back to tonnes
    H2O_tonnes_required = (moles_H2O_required * MW_H2O) / 1e6
    CO2_tonnes = (moles_CO2_produced * MW_CO2) / 1e6
    H2_tonnes = (moles_H2_produced * MW_H2) / 1e6

    return CO2_tonnes, H2_tonnes, H2O_tonnes_required


def methanol_synthesis_w_co2(
    CO2_tonnes: float, H2_tonnes: float
) -> (float, float, str, float):
    """
    Methanol and water production from carbon dioxide and hydrogen, with outputs in tonnes.

    The reaction is as follows:
    CO2 + 3H2 -> CH4O + H2O   DELTA_H = +90.7 kJ/mol / DELTA_H = -58 kJ mol-1  (Equation 13 in [2])

    Parameters:
    - CO2_tonnes: float, tonnes of carbon dioxide.
    - H2_tonnes: float, tonnes of hydrogen.

    Returns:
    - float, tonnes of methanol produced.
    - float, tonnes of water produced.
    - str, the limiting reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # 1) Convert feed (tonnes) to moles
    moles_CO2 = (CO2_tonnes * 1e6) / MW_CO2
    moles_H2 = (H2_tonnes * 1e6) / MW_H2

    # 2) Determine the limiting reagent
    #    Stoichiometry: 1 mole CO₂ reacts with 3 moles H₂
    #    => If moles_CO2 < moles_H2 / 3, CO₂ is limiting; else H₂ is limiting.
    if moles_CO2 < (moles_H2 / 3.0):
        limiting_reagent = "CO₂"
        moles_reacted_CO2 = moles_CO2
        moles_reacted_H2 = moles_CO2 * 3.0
    else:
        limiting_reagent = "H₂"
        moles_reacted_H2 = moles_H2
        moles_reacted_CO2 = moles_H2 / 3.0

    # 3) Calculate methanol and water production
    #    1 mole CO₂ => 1 mole CH₄O => 1 mole H₂O
    #    The "reacted CO₂" dictates how many moles of CH₄O & H₂O form
    moles_CH4O_produced = moles_reacted_CO2  # 1:1 with CO₂
    moles_H2O_produced = moles_reacted_CO2  # 1:1 with CO₂

    # 4) Convert consumed and produced moles back to tonnes
    CO2_tonnes_consumed = (moles_reacted_CO2 * MW_CO2) / 1e6
    H2_tonnes_consumed = (moles_reacted_H2 * MW_H2) / 1e6
    CH4O_tonnes_produced = (moles_CH4O_produced * MW_CH4O) / 1e6
    H2O_tonnes_produced = (moles_H2O_produced * MW_H2O) / 1e6

    # 5) Calculate excess (the non-limiting reagent leftover)
    if limiting_reagent == "CO₂":
        # We used all CO₂ => leftover is H₂
        leftover_moles = moles_H2 - moles_reacted_H2
        excess_tonnes = leftover_moles * MW_H2 / 1e6
    else:
        # We used all H₂ => leftover is CO₂
        leftover_moles = moles_CO2 - moles_reacted_CO2
        excess_tonnes = leftover_moles * MW_CO2 / 1e6

    return (
        CH4O_tonnes_produced,
        H2O_tonnes_produced,
        CO2_tonnes_consumed,
        H2_tonnes_consumed,
        limiting_reagent,
        excess_tonnes,
    )


# Gasification of carbon (coal, coke) reactions
def gasification_of_carbon_with_steam(
    C_tonnes: float, H2O_tonnes: float
) -> (float, float, str, str, float):
    """
    Gasification of carbon with water to produce carbon monoxide and hydrogen,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.11 in [1]).

    Parameters:
    - C_tonnes: float, tonnes of carbon.
    - H2O_tonnes: float, tonnes of water.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.

    Notes:
    The reaction is as follows, with all quantities in tonnes:
    C + H2O -> CO + H2
    """
    # Convert tonnes to moles
    moles_C = (C_tonnes * 1e6) / MW_C
    moles_H2O = (H2O_tonnes * 1e6) / MW_H2O

    # Determine the limiting reagent
    limiting_reagent = "C" if moles_C < moles_H2O else "H2O"
    moles_reacted = min(moles_C, moles_H2O)

    # Calculate products
    CO_tonnes = (moles_reacted * MW_CO) / 1e6
    H2_tonnes = (moles_reacted * MW_H2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "C":
        excess_reagent = "H2O"
        excess_moles = moles_H2O - moles_reacted
    else:
        excess_reagent = "C"
        excess_moles = moles_C - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_C if excess_reagent == "C" else MW_H2O)) / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def combustion_carbon_to_co2(
    C_tonnes: float, O2_tonnes: float
) -> (float, str, str, float):
    """
    Combustion of carbon to produce carbon dioxide,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.12 in [1]).

    Parameters:
    - C_tonnes: float, tonnes of carbon.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon dioxide produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.

    Notes:
    The reaction is as follows, with all quantities in tonnes:
    C + O2 -> CO2
    """
    # Convert tonnes to moles
    moles_C = (C_tonnes * 1e6) / MW_C
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "C" if moles_C < moles_O2 else "O2"
    moles_reacted = min(moles_C, moles_O2)

    # Calculate product
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "C":
        excess_reagent = "O2"
        excess_moles = moles_O2 - moles_reacted
    else:
        excess_reagent = "C"
        excess_moles = moles_C - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_C if excess_reagent == "C" else MW_O2)) / 1e6

    return CO2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


# Gasification of coal and biomass reactions
def gasification(
    C_tonnes: float, O2_tonnes: float, H2O_tonnes: float
) -> (float, float, str, float):
    """
    Implements the coal and biomass gasification process.

    Stoichiometry:
    3C + O2 + H2O -> 3CO + H2   (DELTA_H = -142.22 kJ/mol)

    Parameters:
    - C_tonnes: Tonnes of carbon.
    - O2_tonnes: Tonnes of oxygen.
    - H2O_tonnes: Tonnes of water.

    Returns:
    - Tonnes of carbon monoxide produced.
    - Tonnes of hydrogen produced.
    - The limiting reactant.
    - Tonnes of the excess reactant remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_C = C_tonnes * 1e6 / MW_C
    moles_O2 = O2_tonnes * 1e6 / MW_O2
    moles_H2O = H2O_tonnes * 1e6 / MW_H2O

    # Stoichiometric ratios for the reactants based on the balanced equation
    ratio_C = moles_C / 3
    ratio_O2 = moles_O2 / 1
    ratio_H2O = moles_H2O / 1

    # Determine the limiting reagent
    limiting_ratio = min(ratio_C, ratio_O2, ratio_H2O)
    limiting_reagent = ""
    excess_amount = 0
    if limiting_ratio == ratio_C:
        limiting_reagent = "C"
        # Calculate moles of excess reactants
        excess_moles_O2 = moles_O2 - limiting_ratio
        excess_moles_H2O = moles_H2O - limiting_ratio
    elif limiting_ratio == ratio_O2:
        limiting_reagent = "O2"
        # Calculate moles of excess reactants
        excess_moles_C = moles_C - (limiting_ratio * 3)
        excess_moles_H2O = moles_H2O - limiting_ratio
    else:
        limiting_reagent = "H2O"
        # Calculate moles of excess reactants
        excess_moles_C = moles_C - (limiting_ratio * 3)
        excess_moles_O2 = moles_O2 - limiting_ratio

    # Identify the excess reagent and calculate its amount in tonnes
    if limiting_reagent == "C":
        excess_reagent = "O2" if excess_moles_O2 > excess_moles_H2O else "H2O"
        excess_amount = (
            (excess_moles_O2 if excess_reagent == "O2" else excess_moles_H2O)
            * (MW_O2 if excess_reagent == "O2" else MW_H2O)
            / 1e6
        )
    elif limiting_reagent == "O2":
        excess_reagent = "C" if excess_moles_C > excess_moles_H2O else "H2O"
        excess_amount = (
            (excess_moles_C if excess_reagent == "C" else excess_moles_H2O)
            * (MW_C if excess_reagent == "C" else MW_H2O)
            / 1e6
        )
    else:  # limiting_reagent == 'H2O'
        excess_reagent = "C" if excess_moles_C > excess_moles_O2 else "O2"
        excess_amount = (
            (excess_moles_C if excess_reagent == "C" else excess_moles_O2)
            * (MW_C if excess_reagent == "C" else MW_O2)
            / 1e6
        )

    # Calculate the amount of products based on the limiting reagent
    CO_tonnes = limiting_ratio * 3 * MW_CO / 1e6
    H2_tonnes = limiting_ratio * MW_H2 / 1e6

    return CO_tonnes, H2_tonnes, limiting_reagent, excess_amount


def required_inputs_for_gasification(
    CO_tonnes: float, H2_tonnes: float
) -> (float, float, float):
    """
    Calculates the required inputs of carbon, oxygen, and water to produce a given amount of carbon monoxide and hydrogen
    via biomass/coal gasification.

    Stoichiometry:
    3C + O2 + H2O -> 3CO + H2

    Parameters:
    - CO_tonnes: Tonnes of carbon monoxide desired.
    - H2_tonnes: Tonnes of hydrogen desired.

    Returns:
    - Tonnes of carbon required.
    - Tonnes of oxygen required.
    - Tonnes of water required.
    """
    # Convert tonnes to moles
    moles_CO = CO_tonnes * 1e6 / MW_CO
    moles_H2 = H2_tonnes * 1e6 / MW_H2

    # Calculate moles of C, O2, and H2O needed based on desired CO and H2 production
    moles_C_needed = moles_CO  # 3C -> 3CO, directly proportional
    moles_O2_needed = moles_CO / 3  # O2 is used in a 1:3 ratio with CO
    moles_H2O_needed = moles_H2  # 1 H2O -> 1 H2, directly proportional

    # Convert moles back to tonnes
    C_tonnes = moles_C_needed * MW_C / 1e6
    O2_tonnes = moles_O2_needed * MW_O2 / 1e6
    H2O_tonnes = moles_H2O_needed * MW_H2O / 1e6

    return C_tonnes, O2_tonnes, H2O_tonnes


# Partial oxidation reactions
def partial_oxidation_carbon_to_CO(
    C_tonnes: float, O2_tonnes: float
) -> (float, str, str, float):
    """
    Partial oxidation of carbon to produce carbon monoxide,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.13 in [1]).
    Stoichiometry:
    C + 0.5O2 -> CO

    Parameters:
    - C_tonnes: float, tonnes of carbon.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon monoxide produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_C = (C_tonnes * 1e6) / MW_C
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "C" if moles_C < moles_O2 * 2 else "O2"
    moles_reacted = min(moles_C, moles_O2 * 2)

    # Calculate product
    CO_tonnes = (moles_reacted * MW_CO) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "C":
        excess_reagent = "O2"
        excess_moles = moles_O2 - (moles_reacted / 2)
    else:
        excess_reagent = "C"
        excess_moles = moles_C - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_C if excess_reagent == "C" else MW_O2)) / 1e6

    return CO_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def boudouard_reaction(C_tonnes: float, CO2_tonnes: float) -> (float, str, str, float):
    """
    Boudouard reaction of carbon with carbon dioxide to produce carbon monoxide,
    Also identifies the limiting reagent, excess reagent, and the excess amount (Equation 4.14 in [1]).

    Stoichiometry:
    C + CO2 -> 2CO (DELTA_H = +172 kJ/mol)

    Parameters
    - C_tonnes: float, tonnes of carbon.
    - CO2_tonnes: float, tonnes of carbon dioxide.

    Returns
    - float, tonnes of carbon monoxide produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_C = (C_tonnes * 1e6) / MW_C
    moles_CO2 = (CO2_tonnes * 1e6) / MW_CO2

    # Determine the limiting reagent
    limiting_reagent = "C" if moles_C < moles_CO2 else "CO2"
    moles_reacted = min(moles_C, moles_CO2)

    # Calculate product
    CO_tonnes = (2 * moles_reacted * MW_CO) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "C":
        excess_reagent = "CO2"
        excess_moles = moles_CO2 - moles_reacted
    else:
        excess_reagent = "C"
        excess_moles = moles_C - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_C if excess_reagent == "C" else MW_CO2)) / 1e6

    return CO_tonnes, limiting_reagent, excess_reagent, excess_tonnes


# Carbon formation reactions
def carbon_formation_from_methane(CH4_tonnes: float) -> (float, float, str, float):
    """
    Carbon formation from methane, with inputs in tonnes and outputs in tonnes(Equation 4.15 in [1]).
    Stoichiometry:
    CH4 -> C + 2H2

    Parameters:
    - CH4_tonnes: float, tonnes of methane.

    Returns:
    - float, tonnes of carbon produced.
    - float, tonnes of hydrogen produced.
    - str, indicating the reactant 'CH4' as it's directly converted.
    - float, the amount of reactant used (tonnes), equal to the input as all is converted.
    """
    # Convert tonnes to moles
    moles_CH4 = (CH4_tonnes * 1e6) / MW_CH4

    # Calculate products based on the moles of methane
    C_tonnes = (moles_CH4 * MW_C) / 1e6
    H2_tonnes = (2 * moles_CH4 * MW_H2) / 1e6

    # Since the reaction converts all methane, there's no excess reactant
    reactant_used_tonnes = CH4_tonnes

    return C_tonnes, H2_tonnes, "CH4", reactant_used_tonnes


def carbon_formation_from_hydrocarbons(
    CmHn_tonnes: float, x: float, m: int, n: int
) -> (float, float, str, str, float):
    """
    Carbon formation from general hydrocarbons, with inputs in tonnes and outputs in tonnes(Equation 4.16 in [1]).
    Stoichiometry:
    CmHn -> xC + Cm-xHn-2x + xH2

    Parameters:
    - CmHn_tonnes: float, tonnes of hydrocarbon (CmHn).
    - x: float, moles of carbon that reacts to form carbon monoxide and remaining hydrocarbon.
    - m: int, number of carbon atoms in the hydrocarbon.
    - n: int, number of hydrogen atoms in the hydrocarbon.

    Returns:
    - float, tonnes of carbon produced.
    - float, tonnes of hydrogen produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent.


    """

    # molecular weight for CmHn
    MW_CmHn = (12.01 * m) + (1.008 * n)

    # Convert tonnes of hydrocarbon to moles
    moles_CmHn = (CmHn_tonnes * 1e6) / MW_CmHn

    # Calculate moles of carbon and hydrogen produced based on x
    moles_C_produced = x * moles_CmHn
    moles_H2_produced = x * moles_CmHn

    # Convert moles back to tonnes
    C_tonnes = (moles_C_produced * MW_C) / 1e6
    H2_tonnes = (moles_H2_produced * MW_H2) / 1e6

    # Assuming x is the total moles of C that can react based on the provided CmHn
    if moles_CmHn >= x:
        limiting_reagent = "CmHn"
        excess_reagent = "None"
        excess_amount = (moles_CmHn - x) * MW_CmHn / 1e6
    else:
        limiting_reagent = "None"  # All CmHn is consumed
        excess_reagent = "None"
        excess_amount = 0

    return C_tonnes, H2_tonnes, limiting_reagent, excess_reagent, excess_amount


def reverse_boudouard_reaction(CO_tonnes: float) -> (float, float, str, float):
    """
    Reverse Boudouard reaction of carbon monoxide to produce carbon and carbon dioxide, with inputs in tonnes and outputs in tonnes (Equation 4.17 in [1]).
    Stoichiometry:
    2CO -> C + CO2 (DELTA_H = -172 kJ/mol)

    Parameters:
    - CO_tonnes: float, tonnes of carbon monoxide.

    Returns:
    - float, tonnes of carbon produced.
    - float, tonnes of carbon dioxide produced.
    - str, indicating the reactant 'CO' as it's directly converted.
    - float, the amount of reactant used (tonnes), equal to half the input as CO reacts in a 2:1 ratio.

    """
    # Convert tonnes to moles
    moles_CO = (CO_tonnes * 1e6) / MW_CO

    # CO reacts in a 2:1 ratio to produce C and CO2
    moles_reacted = moles_CO / 2

    # Calculate moles of carbon and carbon dioxide produced
    C_tonnes = (moles_reacted * MW_C) / 1e6
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6

    # Since 2 moles of CO produce 1 mole of C and 1 mole of CO2, the amount of CO reacted is half the initial amount
    reactant_used_tonnes = CO_tonnes / 2

    return C_tonnes, CO2_tonnes, "CO", reactant_used_tonnes


# Selective CO oxidation reactions
def co_oxidation(CO_tonnes: float, O2_tonnes: float) -> (float, str, str, float):
    """
    Selective CO oxidation to produce carbon dioxide (Equation 4.21 in [1]).
    Stoichiometry:
    CO + O2 -> CO2

    Parameters:
    - CO_tonnes: float, tonnes of carbon monoxide.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of carbon dioxide produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.

    """
    # Convert tonnes to moles
    moles_CO = (CO_tonnes * 1e6) / MW_CO
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "CO" if moles_CO < moles_O2 else "O2"
    moles_reacted = min(moles_CO, moles_O2)

    # Calculate product
    CO2_tonnes = (moles_reacted * MW_CO2) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "CO":
        excess_reagent = "O2"
        excess_moles = moles_O2 - moles_reacted
    else:
        excess_reagent = "CO"
        excess_moles = moles_CO - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_CO if excess_reagent == "CO" else MW_O2)) / 1e6

    return CO2_tonnes, limiting_reagent, excess_reagent, excess_tonnes


def h2_oxidation(H2_tonnes: float, O2_tonnes: float) -> (float, str, str, float):
    """
    Oxidation of hydrogen to produce water (Equation 4.22 in [1]),
    Stoichiometry:
    H2 + 0.5O2 -> H2O

    Parameters:
    - H2_tonnes: float, tonnes of hydrogen.
    - O2_tonnes: float, tonnes of oxygen.

    Returns:
    - float, tonnes of water produced.
    - str, the limiting reagent.
    - str, the excess reagent.
    - float, tonnes of the excess reagent remaining after the reaction.
    """
    # Convert tonnes to moles
    moles_H2 = (H2_tonnes * 1e6) / MW_H2
    moles_O2 = (O2_tonnes * 1e6) / MW_O2

    # Determine the limiting reagent
    limiting_reagent = "H2" if moles_H2 < moles_O2 / 2 else "O2"
    moles_reacted = min(moles_H2, moles_O2 / 2)

    # Calculate product
    H2O_tonnes = (moles_reacted * MW_H2O) / 1e6

    # Calculate excess reagent and its amount
    if limiting_reagent == "H2":
        excess_reagent = "O2"
        excess_moles = moles_O2 - (2 * moles_reacted)
    else:
        excess_reagent = "H2"
        excess_moles = moles_H2 - moles_reacted

    # Convert excess moles back to tonnes
    excess_tonnes = (excess_moles * (MW_H2 if excess_reagent == "H2" else MW_O2)) / 1e6

    return H2O_tonnes, limiting_reagent, excess_reagent, excess_tonnes


########################################
_BIOMASS: dict[
    Literal[
        "dry_biomass",
        "wet_biomass",
        "rice_straw",
        "lipid_rich_biomass",
        "agric_waste",
        "isw",
        "carbonaceous_biomass",
    ],
    dict[str, float],
] = {
    # formula ──── MW (g/mol)────ν_CH4────ν_CO2────ν_H2O
    "dry": {"MW": 145.12, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 0},
    "wet_biomass": {"MW": 177.14, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 2},
    "rice_straw": {"MW": 162.14, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 0.5},
    "lipid_rich_biomass": {"MW": 884.54, "ν_CH4": 26, "ν_CO2": 31, "ν_H2O": 0},
    "agric_waste": {"MW": 180.16, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 1.5},
    "isw": {"MW": 162.14, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 0.5},
    "carbonaceous_biomass": {"MW": 162.14, "ν_CH4": 3, "ν_CO2": 3, "ν_H2O": 0.5},
}


def methane_extraction_from_biomass(
    biomass_type: Literal[
        "dry_biomass",
        "wet_biomass",
        "rice_straw",
        "lipid_rich_biomass",
        "agric_waste",
        "isw",
        "carbonaceous_biomass",
    ],
    biomass_tonnes: float,
) -> Tuple[float, float, float]:
    """
    Compute the methane-pathway products (t CH₄, t CO₂, t H₂O) for a given
    mass of biomass.

    ── Stoichiometric equations used ───────────────────────────────────────
      Dry biomass (C₆H₉O₄)               :   C₆H₉O₄             → 3 CH₄ + 3 CO₂
      Wet biomass (C₆H₉O₄·2H₂O)          :   C₆H₉O₄·2H₂O        → 3 CH₄ + 3 CO₂ + 2 H₂O
      Straw (C₆H₁₀O₅)                    :   C₆H₁₀O₅            → 3 CH₄ + 3 CO₂ + 0.5 H₂O
      Lipid-rich biomass (C₅₇H₁₀₄O₆)      :   C₅₇H₁₀₄O₆          → 26 CH₄ + 31 CO₂
      Agricultural waste, high-H (C₆H₁₂O₆):   C₆H₁₂O₆            → 3 CH₄ + 3 CO₂ + 1.5 H₂O
      Food-processing residues (= (appr.)C₆H₁₀O₅)  :   C₆H₁₀O₅            → 3 CH₄ + 3 CO₂ + 0.5 H₂O
      Carbohydrate-rich biomass (C₆H₁₀O₅)  :   C₆H₁₀O₅            → 3 CH₄ + 3 CO₂ + 0.5 H₂O

    Parameters
    ----------
    biomass_type : str
        Key for the feedstock class listed above.
    biomass_tonnes : float
        Mass of *dry* biomass fed, in tonnes.

    Returns
    -------
    Tuple[float, float, float]
        (CH4_tonnes, CO2_tonnes, H2O_tonnes)
        H₂O_tonnes is 0.0 when no water is generated by the equation.

    Raises
    ------
    ValueError
        If `biomass_type` is not recognised.
    """
    if biomass_type not in _BIOMASS:
        raise ValueError(
            f"Unknown biomass_type '{biomass_type}'. "
            f"Choose from: {', '.join(_BIOMASS)}"
        )

    data = _BIOMASS[biomass_type]

    # biomass_tonnes (t) → biomass_kg (kg) → moles of biomass
    n_biomass = biomass_tonnes * 1_000_000 / data["MW"]

    # Convert to tonnes of products
    CH4_t = n_biomass * data["ν_CH4"] * MW_CH4 / 1_000_000
    CO2_t = n_biomass * data["ν_CO2"] * MW_CO2 / 1_000_000
    H2O_t = n_biomass * data["ν_H2O"] * MW_H2O / 1_000_000

    # Drop negligible water values
    H2O_t = 0.0 if abs(H2O_t) < 1e-9 else H2O_t

    return CH4_t, CO2_t, H2O_t


# ────────────────────────────────────────────────────────────────────────────
# Combustion stoichiometry  (biomass  +  ν_O2 O₂ → ν_CO2 CO₂  +  ν_H2O H₂O)
# ────────────────────────────────────────────────────────────────────────────
_COMBUSTION: dict[
    Literal[
        "dry",
        "wet_biomass",
        "rice_straw",
        "lipid_rich_biomass",
        "agric_waste",
        "isw",
        "carbonaceous_biomass",
    ],
    dict[str, float],
] = {
    #          formula                MW (g/mol)   ν_O2  ν_CO2  ν_H2O
    "dry": {"MW": 145.12, "ν_O2": 6.25, "ν_CO2": 6, "ν_H2O": 4.5},
    "wet_biomass": {"MW": 177.14, "ν_O2": 6.25, "ν_CO2": 6, "ν_H2O": 6.5},
    "rice_straw": {"MW": 162.14, "ν_O2": 6.00, "ν_CO2": 6, "ν_H2O": 5},
    "lipid_rich_biomass": {"MW": 884.54, "ν_O2": 78.0, "ν_CO2": 57, "ν_H2O": 52},
    "agric_waste": {"MW": 180.16, "ν_O2": 6.00, "ν_CO2": 6, "ν_H2O": 6},
    "isw": {"MW": 162.14, "ν_O2": 6.00, "ν_CO2": 6, "ν_H2O": 5},
    "carbonaceous_biomass": {"MW": 162.14, "ν_O2": 6.00, "ν_CO2": 6, "ν_H2O": 5},
}


def bio_combustion(
    biomass_type: Literal[
        "dry",
        "wet_biomass",
        "rice_straw",
        "lipid_rich_biomass",
        "agric_waste",
        "isw",
        "carbonaceous_biomass",
    ],
    biomass_tonnes: float,
) -> Tuple[float, float, float]:
    """
    Return the *tonnes* of products and oxidant consumed during complete
    combustion of a given biomass type.

    ── Stoichiometric equations used ───────────────────────────────────────
      Dry biomass               :  C₆H₉O₄            + 6.25 O₂ → 6 CO₂ + 4.5 H₂O
      Wet biomass               :  C₆H₉O₄·2H₂O       + 6.25 O₂ → 6 CO₂ + 6.5 H₂O
      Straw / Food / Carb.-rich :  C₆H₁₀O₅           + 6    O₂ → 6 CO₂ + 5   H₂O
      Lipid-rich biomass        :  C₅₇H₁₀₄O₆        + 78   O₂ → 57 CO₂ + 52  H₂O
      Agric. waste (high-H)     :  C₆H₁₂O₆           + 6    O₂ → 6 CO₂ + 6   H₂O

    Parameters
    ----------
    biomass_type : str
        Key identifying the feedstock category.
    biomass_tonnes : float
        Mass of dry biomass to combust (t).

    Returns
    -------
    Tuple[float, float, float]
        (CO2_tonnes, H2O_tonnes, O2_tonnes_consumed)

    Raises
    ------
    ValueError
        If an unknown `biomass_type` is supplied.
    """
    if biomass_type not in _COMBUSTION:
        raise ValueError(
            f"Unknown biomass_type '{biomass_type}'. "
            f"Valid options: {', '.join(_COMBUSTION)}"
        )

    st = _COMBUSTION[biomass_type]

    # Convert biomass mass (t) → moles of biomass
    n_biomass = biomass_tonnes * 1_000_000 / st["MW"]

    # Tonnes of each participant
    CO2_t = n_biomass * st["ν_CO2"] * MW_CO2 / 1_000_000
    H2O_t = n_biomass * st["ν_H2O"] * MW_H2O / 1_000_000
    O2_t = n_biomass * st["ν_O2"] * MW_O2 / 1_000_000

    return CO2_t, H2O_t, O2_t
