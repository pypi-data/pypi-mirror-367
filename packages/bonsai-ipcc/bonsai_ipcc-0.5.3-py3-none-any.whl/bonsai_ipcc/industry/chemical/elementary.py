"""Greenhouse Gas Emission Calculations for Chemical Production

This script calculates CO2 and CH4 emissions from chemical production using IPCC Tier 1-3 methods. It includes functions for:

Tier 1: CO2 emissions using emission factors
Tier 2: CO2 emissions via mass balance
Tier 3: Direct measurement of CO2 emissions
Detailed analysis of combustion, process vent, and flaring emissions
Fugitive and process vent methane emissions
These reusable functions leverage annual production data, emissions factors, and mass balances. Ensure all input data units are consistent when using these functions.

Author: @Albertkwame
Affiliation: Aalborg University, Copenhagen
Email: ako@plan.aau.dk
"""


def pp_i_j_k(pp_i: float, pp_share_i_j: float, pp_share_i_j_k: float) -> tuple:
    """
    Calculate the quantity of petrochemical i produced through a specific production process configuration/activity and from a specific feedstock (t/yr).

    Parameters
    ----------
    pp_i : float
        Total annual production of petrochemical i in the country, in tons.
    pp_share_i_j : float
        Share of total methanol production attributed to process configuration/activity j, as a percentage.
    pp_share_i_j_k : float
        Share of the specific feedstock 'k' required to produce methanol in process configuration/activity j, as a percentage.

    Returns
    -------
    tuple
        Quantity of methanol produced via process configuration/activity j (in tons) and quantity of methanol produced from the specific feedstock for process configuration/activity j (in tons).
    """
    pp_i_j = pp_i * (pp_share_i_j / 100)
    pp_i_j_k = pp_i_j * (pp_share_i_j_k / 100)
    return pp_i_j_k


def eco2_tier1(pp_i: float, ef: float, gaf: float) -> float:
    """
    Implements Equation 3.15 to calculate the CO2 emissions for chemical production using Tier 1 emission factors.

    This method computes the CO2 emissions by considering the annual production of the chemical,
    its specific CO2 emission factor, and a geographic adjustment factor, as per Equation 3.15.

    Parameters
    ----------
    pp_i : float
        Annual production of chemical i, in tonnes.
    ef : float
        CO2 emission factor for chemical i, in tonnes CO2/tonne product produced.
    gaf : float
        Geographic Adjustment Factor (GAF) as a percentage for Tier 1 CO2 emission factors
        for ethylene production.

    Returns
    -------
    float
        The calculated CO2 emissions from the production of chemical i, in tonnes.

    Examples
    --------
    >>> eco2_tier1(1000, 0.5, 100)
    500.0

    Notes
    -----
    The GAF should be provided as a percentage value where 100 represents no adjustment,
    less than 100 indicates a reduction, and more than 100 indicates an increase in the
    CO2 emissions due to geographic efficiency differences.
    """
    eco2_tier1 = pp_i * ef * gaf / 100
    return eco2_tier1


def pp_i(fa, spp) -> float:
    """
    Implements Equation 3.16 to estimate the annual production of a chemical using feedstock consumption and specific production factors.

    Parameters
    ----------
    fa : float
        annual consumption for the production of chemical (i), in tonnes.
    spp : float
        primary product production factor for chemical (i), in tonnes of primary product per tonne of feedstock consumed.

    Returns
    -------
    float
        The estimated annual production of the chemical (PP_i), in tonnes.

    """
    pp_i = fa * spp
    return pp_i


def eco2_tier2(
    fa_fc,
    pp_pc,
    sp_sc,
) -> float:
    """
    Implements Equation 3.17 to calculate CO2 emissions from the production of chemical `i` using the Tier 2 mass balance method.
    Equation has been subdivided.

    Parameters
    ----------
    fa_fc : float
        Annual carbon content of feedstock, in tonnes.
    pp_pc : float
        Annual carbon content of primary petrochemical, in tonnes.
    sp_sc : float
        Annual carbon content of secondary product, in tonnes.

    Returns
    -------
    float
        CO2 emissions from the production of chemical `i`, in t/yr.
    """
    eco2_tier2 = (fa_fc - (pp_pc + sp_sc)) * 44 / 12
    return eco2_tier2


def fa_fc(
    fa,
    fc,
) -> float:
    """
    Implements Equation 3.17 to calculate the carbon input of the production of chemical `i` using the Tier 2 mass balance method.

    Parameters
    ----------
    fa : float
        Annual consumption of feedstock `k` for production of chemical `i`, in tonnes.
    fc : float
        Carbon content of feedstock `k`, in tonnes C/tonne feedstock.

    Returns
    -------
    float
        annual carbon content of feedstock, in t/yr.
    """
    fa_fc = fa * fc
    return fa_fc


def pp_pc(
    pp_i,
    pc,
) -> float:
    """
    Implements Equation 3.17 to calculate carbon output of the production of chemical `i` using the Tier 2 mass balance method.

    Parameters
    ----------
    pp_i : float
        Annual production of primary chemical product `i`, in tonnes.
    pc : float
        Carbon content of primary chemical product `i`, in tonnes C/tonne product.

    Returns
    -------
    float
        annual carbon content of primary petrochemical, in t/yr.
    """
    pp_pc = pp_i * pc
    return pp_pc


def sp_sc(
    sp,
    sc,
) -> float:
    """
    Implements Equation 3.17 to calculate CO2 emissions from the production of chemical `i` using the Tier 2 mass balance method.

    Parameters
    ----------
    sp : float
        Annual amount of secondary product `j` produced from the production process for chemical `i`, in tonnes.
    sc : float
        Carbon content of secondary product `j`, in tonnes C/tonne product.

    Returns
    -------
    float
        annual carbon content of secondary product, in t/yr.
    """
    sp_sc = sp * sc
    return sp_sc


def sp_ethylene_j(fa_ethylene, ssp) -> float:
    """
    Implements Equation 3.18 to estimate the annual production of a secondary product `j` from ethylene production.

    Parameters
    ----------
    fa_ethylene_k : float
        annual consumption of feedstock k for ethylene production, t/yr
    ssp : float
        specific secondary product production factor for secondary product `j` and feedstock k, (i.e, t/t - tonnes of secondary product per tonne of feedstock consumed)

    Returns
    -------
    float
        Total annual production of the secondary product `j` from ethylene production, t/yr

    """
    sp_ethylene_j = fa_ethylene * ssp
    return sp_ethylene_j


def sp_acrylonitrile_j(fp_acrylonitrile, ssp) -> float:
    """
    Implements Equation 3.19 to estimate the annual production of a secondary product `j` from acrylonitrile production.

    Parameters
    ----------
    fp_acrylonitrile : float
        annual acrylonitrile production from feedstock `k`, t/yr
    ssp : float
        specific secondary product production factor for secondary product `j` and feedstock `k`, (t/t - secondary product/tonne acrylonitrile produced)

    Returns
    -------
    float
        Total annual production of the secondary product from acrylonitrile production, t/yr.
    """
    sp_acrylonitrile_j = fp_acrylonitrile * ssp
    return sp_acrylonitrile_j


# Methane emissions


# Tier 1 CH4 emissions
def ech4_tier1(ech4_fugitive: float, ech4_process_vent: float) -> float:
    """
    Calculate total CH4 emissions from the production of chemical i using Equation 3.25.

    Parameters
    ----------
    ech4_fugitive : float
        CH4 fugitive emission factor for chemical i, in kg CH4/tonne product.
    ech4_process_vent : float
        CH4 process vent emission factor for chemical i, in kg CH4/tonne product.

    Returns
    -------
    float
        Total CH4 emissions from production of chemical i, in kg.
    """

    return ech4_fugitive + ech4_process_vent


def ech4_fugitive(pp_i: float, ef: float) -> float:
    """
    Calculate fugitive CH4 emissions from the production of chemical i using Equation 3.23.

    Parameters
    ----------
    pp_i : float
        Annual production of chemical i, in tonnes.
    ef : float
        CH4 fugitive emission factor for chemical i, in kg CH4/tonne product.

    Returns
    -------
    float
        Fugitive emissions of CH4 from production of chemical i, in kg.
    """
    ech4_fugitive_i = pp_i * ef
    return ech4_fugitive_i


def ech4_process_vent(pp_i: float, ef: float) -> float:
    """
    Calculate process vent CH4 emissions from the production of chemical i using Equation 3.24.

    Parameters
    ----------
    pp_i : float
        Annual production of chemical i, in tonnes.
    ef : float
        CH4 process vent emission factor for chemical i, in kg CH4/tonne product.

    Returns
    -------
    float
        Process vent emissions of CH4 from production of chemical i, in kg.
    """
    ech4_process_vent = pp_i * ef
    return ech4_process_vent


# Tier 3 CH4 emissions
def ech4_tier3a(
    c_total_vocs: float,
    ch4_fraction: float,
    ch4_background_level: float,
    WS: float,
    PA: float,
) -> float:
    """
    Calculate total plant CH4 emissions from atmospheric measurement data using Equation 3.26.

    Parameters
    ----------
    c_total_vocs : float
        VOC concentration at the plant, in micrograms/m^3.
    ch4_fraction : float
        Fraction of total VOC concentration that is CH4.
    ch4_background_level : float
        Ambient CH4 concentration at background location, in micrograms/m^3.
    WS : float
        Wind speed at the plant, in metres/second.
    PA : float
        Plume area, in square metres.

    Returns
    -------
    float
        Total CH4 emissions from the plant, in micrograms/second.
    """
    return (c_total_vocs * ch4_fraction - ch4_background_level) * WS * PA


def ech4_tier3b(e_combustion: float, ech4_process_vent: float, e_flare: float) -> float:
    """
    Calculate the total emissions of CH4 from production of chemical i using Equation 3.27.

    Parameters
    ----------
    e_combustion : float
        Emissions of CH4 from fuel combustion, in kg.
    ech4_process_vent : float
        Emissions of CH4 from process vents, in kg.
    e_flare : float
        Emissions of CH4 from flared waste gases, in kg.

    Returns
    -------
    float
        The total emissions of CH4 from production of chemical i, in kg.
    """
    return e_combustion + ech4_process_vent + e_flare


def e_combustion(fa_i_k: float, ncv_k: float, ef_k: float) -> float:
    """
    Calculate the CH4 emissions from the combustion of a specific fuel k for petrochemical product i.

    This is a part of Equation 3.28 from the IPCC guidelines.
    The function calculates the emissions for one type of fuel and should be used inside a loop
    to sum the emissions for all types of fuel.

    Parameters:
    - fa_ij_k: The amount of fuel k consumed for production of petrochemical i, in tonnes.
    - ncv_k: The net calorific value of fuel k, in TJ/tonne.
    - ef_k: The CH4 emission factor of fuel k, in kg/TJ.

    Returns:
    - CH4 emissions from the combustion of fuel k for product i.
    """
    e_combustion = fa_i_k * ncv_k * ef_k
    return e_combustion


def e_flare(fg_i_k: float, ncv_k: float, ef_k: float) -> float:
    """
    Calculate the CH4 emissions from the flaring of a specific gas k for petrochemical product i.

    This is a part of Equation 3.29 from the IPCC guidelines.
    The function calculates the emissions for one type of flared gas and should be used inside a loop
    to sum the emissions for all types of flared gas.

    Parameters:
    - fg_ij_k: The amount of gas k flared during production of petrochemical i, in tonnes.
    - ncv_k: The net calorific value of flared gas k, in TJ/tonne.
    - ef_k: The CH4 emission factor of flared gas k, in kg/TJ.

    Returns:
    - CH4 emissions from the flaring of gas k for product i.
    """
    e_flare = fg_i_k * ncv_k * ef_k
    return e_flare


def tier1_e_hfc_23(ef_default: float, p_hcfc_22: float) -> float:
    """
    Estimate HFC-23 emissions from HCFC-22 production using the Tier 1 default factor.
    This is a part of Equation 3.30 from the IPCC guidelines.

    Parameters
    ----------
    ef_default : float
        HFC-23 default emission factor, kg HFC-23/kg HCFC-22.
    p_hcfc_22 : float
        Total HCFC-22 production, kg.

    Returns
    -------
    float
        Estimated HFC-23 emissions, kg.
    """
    return ef_default * p_hcfc_22


def tier2_e_hfc_23(ef_calculated: float, p_hcfc_22: float, f_released: float) -> float:
    """
    Estimate HFC-23 emissions from HCFC-22 production using calculated factors from process efficiencies (Tier 2).
    This is a part of Equation 3.31 from the IPCC guidelines.

    Parameters
    ----------
    ef_calculated : float
        HFC-23 calculated emission factor, kg HFC-23/kg HCFC-22.
    p_hcfc_22 : float
        Total HCFC-22 production, kg.
    f_released : float
        Fraction of the year that this stream was released to atmosphere untreated.

    Returns
    -------
    float
        Estimated HFC-23 emissions, kg.
    """
    return ef_calculated * p_hcfc_22 * f_released


def ef_carbon_balance(cbe: float, f_efficiency_loss: float, fcc: float = 0.81) -> float:
    """
    Calculate the HFC-23 emission factor from carbon balance efficiency (Equation 3.32).

    Parameters
    ----------
    cbe : float
        Carbon balance efficiency, percent.
    f_efficiency_loss : float
        Factor to assign efficiency loss to HFC-23, fraction.
    fcc : float
        Factor for the carbon content of this component (default is 0.81 kg HFC-23/kg HCFC-22).

    Returns
    -------
    float
        The HFC-23 emission factor calculated from carbon balance efficiency.
    """
    return ((100 - cbe) / 100) * f_efficiency_loss * fcc


def ef_fluorine_balance(
    fbe: float, f_efficiency_loss: float, ffc: float = 0.54
) -> float:
    """
    Calculate the HFC-23 emission factor from fluorine balance efficiency (Equation 3.33).

    Parameters
    ----------
    fbe : float
        Fluorine balance efficiency, percent.
    f_efficiency_loss : float
        Factor to assign efficiency loss to HFC-23, fraction.
    ffc : float
        Factor for the fluorine content of this component (default is 0.54 kg HFC-23/kg HCFC-22).

    Returns
    -------
    float
        The HFC-23 emission factor calculated from fluorine balance efficiency.
    """
    return ((100 - fbe) / 100) * f_efficiency_loss * ffc


def e_hfc_23_direct_method(c_ij: float, f_ij: float) -> float:
    """
    Calculate total HFC-23 emissions from individual process streams using the direct method (Equation 3.34).

    Parameters
    ----------
    c_ij : float
        Concentration of HFC-23 in the stream (kg HFC-23).
    f_ij : float
        Mass flow of the stream (kg).

    Returns
    -------
    float
        Total HFC-23 emissions for the given stream.
    """
    return c_ij * f_ij


def e_hfc_23_proxy_method(e_ij: float) -> float:
    """
    Calculate total HFC-23 emissions from individual process streams using proxy methods (Equation 3.35).

    Parameters
    ----------
    e_ij : float
        Emissions from each plant and stream determined by the proxy methods (kg).

    Returns
    -------
    float
        Total HFC-23 emissions for the given stream.
    """
    return e_ij


def e_hfc_23_by_monitoring(c_i: float, p_i: float) -> float:
    """
    Calculate total HFC-23 emissions from individual process streams by monitoring reactor product (Equation 3.36).

    Parameters
    ----------
    c_i : float
        Concentration of HFC-23 relative to the HCFC-22 product (kg HFC-23/kg HCFC-22).
    p_i : float
        Mass flow of HCFC-22 from the plant reactor (kg).

    Returns
    -------
    float
        Total HFC-23 emissions for the given plant.
    """
    return c_i * p_i


def e_ij_instantaneous_hfc_23_direct_method(
    c_ij: float, f_ij: float, t: float
) -> float:
    """
    Calculate 'instantaneous' HFC-23 emissions from an individual process stream (Equation 3.37).

    Parameters
    ----------
    c_ij : float
        Concentration of HFC-23 in the gas stream from the process stream (kg HFC-23/kg gas).
    f_ij : float
        Mass flow of the gas stream from the process stream (kg gas/hour).
    t : float
        The length of time over which these parameters are measured and remain constant (hours).

    Returns
    -------
    float
        The 'instantaneous' HFC-23 emissions for the given process stream (kg).
    """
    return c_ij * f_ij * t


def e_ij_hfc_23_proxy_method(
    s_ij: float, f_ij: float, por_ij: float, t: float, r_ij: float
) -> float:
    """
    Calculate HFC-23 emissions from an individual process stream using the proxy method (Equation 3.38).

    Parameters
    ----------
    s_ij : float
        The standard mass emission of HFC-23 in vent stream j at plant i (kg).
    f_ij : float
        A dimensionless factor relating the measured standard mass emission rate to the emission rate at the actual plant operating rate.
    por_ij : float
        The proxy operating rate (such as process operating rate) at plant i during the trial (unit/hour).
    t : float
        The total duration of venting for the year, or the period if the process is not operated continuously (hours).
    r_ij : float
        The quantity of HFC-23 recovered for vent stream j at plant i for use as chemical feedstock, or hence destroyed (kg).

    Returns
    -------
    float
        The mass emission of HFC-23 from the process stream j at plant i (kg).
    """
    return (s_ij * f_ij * por_ij * t) - r_ij


def st_ij(ct_ij: float, ft_ij: float, por_t_ij: float) -> float:
    """
    Calculate the standard emission for the proxy method (Equation 3.39).

    Parameters
    ----------
    ct_ij : float
        The average mass fractional concentration of HFC-23 in vent stream j at plant i during the trial (kg HFC-23/kg gas).
    ft_ij : float
        The average mass flow rate of vent stream j at plant i during the trial (kg/hour).
    por_t_ij : float
        The proxy quantity (such as process operating rate) at plant i during the trial (unit/hour).

    Returns
    -------
    float
        The standard mass emission of HFC-23 in vent stream j at plant i ('unit' in units compatible with the factors in Equation 3.38).
    """
    return ct_ij * ft_ij / por_t_ij


def e_i(c_i: float, p_i: float, tf: float, r_i: float) -> float:
    """
    Calculate the emissions of HFC-23 from an individual facility based on in-process measurements (Equation 3.40).

    Parameters
    ----------
    c_i : float
        The concentration of HFC-23 in the reactor product at facility i (kg HFC-23/kg HCFC-22).
    p_i : float
        The mass of HCFC-22 produced at facility i while this concentration applied (kg).
    tf : float
        The fractional duration during which this HFC-23 is actually vented to the atmosphere (dimensionless).
    r_i : float
        The quantity of HFC-23 recovered from facility i for use as chemical feedstock, and hence destroyed (kg).

    Returns
    -------
    float
        The HFC-23 emissions from an individual facility (kg).
    """
    return c_i * p_i * tf - r_i


def tier1_e_k(ef_default_k: float, p_k: float) -> float:
    """
    Calculate the production-related emissions of fluorinated greenhouse gases (Equation 3.41).

    Parameters
    ----------
    ef_default_k : float
        Default emission factor for the greenhouse gas (kg/kg).
    p_k : float
        Total production of the fluorinated greenhouse gas (kg).

    Returns
    -------
    float
        Production-related emissions of the greenhouse gas (kg).
    """
    return ef_default_k * p_k


def tier3_e_k_direct(c_ij: float, f_ij: float, t: float) -> float:
    """
    Calculate the total production-related emissions of fluorinated greenhouse gases using Tier 3 direct method (Equation 3.42).

    Parameters
    ----------
    c_ij : float
        The concentration of the fluorinated greenhouse gas in the stream j at plant i (kg/kg).
    f_ij : float
        The mass flow of the gas stream j at plant i (kg/hour).

    Returns
    -------
    float
        The total production-related emissions for the given plant and stream (kg).
    """
    return c_ij * f_ij


def tier3_e_k_proxy(e_ij: float) -> float:
    """
    Calculate the total production-related emissions of fluorinated greenhouse gases using Tier 3 proxy method (Equation 3.43).

    Parameters
    ----------
    e_ij : float
        The emissions of fluorinated greenhouse gas from each plant and stream determined by the proxy methods (kg).

    Returns
    -------
    float
        The total production-related emissions for the given plant and stream using proxy methods (kg).
    """
    return e_ij


def ef_hfc23_average(carbon, flurine):
    """
    Calculate average of carbon and flurine emission factor (as described on page 3.13)

    Parameters
    ----------
    carbon : float
        hfc23 emission factor for carbon balance (kg/kg)
    flurine : float
        hfc23 emission factor flurine balance (kg/kg)

    Returns
    -------
    float
        hfc23 average emission factor of (kg/kg)
    """
    return (carbon + flurine) / 2
