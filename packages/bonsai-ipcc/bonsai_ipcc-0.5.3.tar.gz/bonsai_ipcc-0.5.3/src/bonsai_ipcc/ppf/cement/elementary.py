# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 09:39:57 2023

This file is intended to contain all elementary equations that will be used in the
cement PPF model that are not part of the IPCC. Beware, some functions will be have to
be moved at the "Collect" or "Clean" stage at a later point in time.

@author: Mathieu Delpierre (2.-0 LCA Consultants)
"""

# If you need to import some IPCC equations for cement


from ...industry.mineral.elementary import (
    co2_emissions_tier1_,
    co2_emissions_tier2_,
    ef_clc,
)

####################################################################################
# ---------------------- Equations for cement production ------------------------- #
####################################################################################


def mass_clinker(mass_cement, clink_on_cem):
    """
    This function calculates the mass of clinker, derived from the mass of cement.

    Parameters
    ----------
    mass_cement : float
        The mass of cement that is considered (in tonnes).
    clink_on_cem : float
        The fraction of clinker needed to produce cement (in kg of clinker/kg of cement).

    Returns
    -------
    mass_clinker : float
        The mass of clinker that is needed to produce the cement considered (in tonnes).

    """
    mass_clinker = mass_cement * clink_on_cem
    return mass_clinker


def energy_need_cement(mass_cement, energy_cement):
    """
    This function calculates the energy need (heat) for the production of cement.

    Parameters
    ----------
    mass_cement : float
        Mass of cement that is considered in tonnes.
    energy_cement : float
        the energy needed to produce cement (in GJ/tonne).

    Returns
    -------
    energy_need_cement : float
        The amount of energy that is needed to produce cement (in TJ).

    """
    energy_need_cement = mass_cement * energy_cement
    # To shift from GJ to TJ, one needs to divide by 1000
    energy_need_cement = energy_need_cement / 1000
    return energy_need_cement


def elec_use_cement(mass_cement, elec_intensity):
    """
    This function calculates the amount of electricity needed for the calcination and
    cement mill. It corresponds to Equation 3.5 from the technical documentation.

    Parameters
    ----------
    mass_cement : float
        mass of cement produced in tonnes.
    elec_intensity : float
        Electricity needed per tonne of cement in the calcination and mill cement
        processes (in kWh/tonne).

    Returns
    -------
    elec_use_cement : float
        Total electricity consumption in the calcination and cement mill processes
        (in TJ).

    """
    elec_use_cement = mass_cement * elec_intensity
    # To shift from kWh to TJ,one needs to multiply by 0.0000036 (1 kWh <=> 0.0000036 TJ)
    elec_use_cement = elec_use_cement * 0.0000036
    return elec_use_cement


def gypsum_use_cement_mill(mass_cement, gyp_intensity):
    """
    This function calculates the amount of gypsum needed for the cement mill and
    corresponds to Equation 3.7 from the technical documentation.

    Parameters
    ----------
    mass_cement : float
        mass of cement produced in tonnes.
    gyp_intensity : float
        Gypsum needed per tonne of cement in the cement mill process (in
        tonne gypsum/tonne cement).

    Returns
    -------
    gyp_use_cement_mill : float
        Total gypsum consumption in the cement mill process (in tonnes).

    """
    gyp_use_cement_mill = mass_cement * gyp_intensity
    return gyp_use_cement_mill


def ckd_landfill(mass_clinker, ckd_on_clinker, coeff_ckd_landfill):
    """
    This function calculates the amount of CKD (Cement Kiln Dust) that is sent to a
    landfill.

    Parameters
    ----------
    mass_clinker : float
        Mass of clinker that is considered (in tonnes).
    ckd_on_clinker : float
        Fraction of CKD that is derived from clinker (fraction).
    coeff_ckd_landfill : float
        Fraction of CKD tha issent into landfill (frcation).

    Returns
    -------
    ckd_landfill : float
        The mass of CKD sent to landfill (in tonnes).

    """
    ckd_landfill = mass_clinker * ckd_on_clinker * coeff_ckd_landfill
    return ckd_landfill


def waste_cement_construction(mass_cement, loss_coeff):
    """
    This function calculates the amount of cement waste generated during contruction
    processes (of buildings, walls, etc...).

    Parameters
    ----------
    mass_cement : float
        The mass of cement that is used for the construction (in tonnes).
    loss_coeff : float
        Coefficient of the material losses occuring from cement use in the construction
        phase (frcction).

    Returns
    -------
    waste_cement_construction : float
        The mass of cement waste generated during the construction process (in tonnes).

    """
    waste_cement_construction = mass_cement * loss_coeff
    return waste_cement_construction


def mass_concrete(
    mass_cement, cement_to_concrete_coeff, cement_use_concrete, volumic_mass_concrete
):
    """
    This fucntion calculates the amount of concrete produced, derived from the global
    cement production (from which a share only is used for concrete, the rest is for
    mortar).

    Parameters
    ----------
    mass_cement : float
        Mass of cement produced (in tonnes).
    cement_to_concrete_coeff : float
        Share of the produced cement that will be allocated to concrete production.
    cement_use_concrete : float
        Amount of cement needed to produce concrete (in kg of cement/m3 of concrete).
    volumic_mass_concrete : float
        Volumic mass concrete in kg/m3.

    Returns
    -------
    mass_concrete : float
        Mass of concrete produced (in tonnes).

    """
    volume_concrete = mass_cement * cement_to_concrete_coeff / cement_use_concrete
    # division by 1000 to switch from kg to tonnes
    mass_concrete = volume_concrete * volumic_mass_concrete / 1000
    return mass_concrete


def water_use_concrete(mass_concrete, volumic_mass_concrete, water_use_concrete):
    """
    This function calculates the water consumption for the concrete production.

    Parameters
    ----------
    mass_concrete : float
        Amount of concrete produced.
    volumic_mass_concrete : float
        Volumic mass of concrete in kg/m3.
    water_use_concrete : float
        Coefficient of water consumed during concrete production in kg/m3.

    Returns
    -------
    volume_water : float
        Amount of water consumed for concrete production (in tonnes).

    """
    # As the water consumption is provided in kg water/m3 of concrete, wee need first to
    # convert the mass of concrete (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_concrete = mass_concrete / (volumic_mass_concrete / 1000)
    water_use_concrete = volume_concrete * water_use_concrete / 1000
    return water_use_concrete


def aggregate_use_concrete(
    mass_concrete, volumic_mass_concrete, aggregate_use_concrete
):
    """
    This function calculates the water consumption for the concrete production.

    Parameters
    ----------
    mass_concrete : float
        Amount of concrete produced.
    volumic_mass_concrete : float
        Volumic mass of concrete in kg/m3.
    aggregate_use_concrete : float
        Coefficient of aggregate consumed during concrete production in kg/m3.

    Returns
    -------
    aggregate_use_concrete : float
        Amount of aggregate consumed for concrete production (in tonnes).

    """
    # As the aggregate consumption is provided in kg water/m3 of concrete, wee need first to
    # convert the mass of concrete (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_concrete = mass_concrete / (volumic_mass_concrete / 1000)
    # The division by 1000 is to switch from kg to tonnes.
    aggregate_use_concrete = volume_concrete * aggregate_use_concrete / 1000
    return aggregate_use_concrete


def elec_use_concrete(mass_concrete, volumic_mass_concrete, elec_use_concrete):
    """
    This function calculates the electricity consumption for the concrete production.

    Parameters
    ----------
    mass_concrete : float
        Amount of concrete produced.
    volumic_mass_concrete : float
        Volumic mass of concrete in kg/m3.
    elec_use_concrete : float
        Coefficient of electricity consumed during concrete production in kWh/m3.

    Returns
    -------
    elec_use_concrete : float
        Amount of electricity consumed for concrete production (in TJ).

    """
    # As the electricity consumption is provided in kg kWh/m3 of concrete, wee need first to
    # convert the mass of concrete (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_concrete = mass_concrete / (volumic_mass_concrete / 1000)
    elec_use_concrete = volume_concrete * elec_use_concrete
    # To shift from kWh to TJ,one needs to multiply by 0.0000036 (1 kWh <=> 0.0000036 TJ)
    elec_use_concrete = elec_use_concrete * 0.0000036
    return elec_use_concrete


def mass_mortar(
    mass_cement, cement_to_mortar_coeff, cement_use_mortar, volumic_mass_mortar
):
    """
    This function calculates the amount of mortar produced, derived from the global
    cement production (from which a share only is used for mortar, the rest is for
    concrete).

    Parameters
    ----------
    mass_cement : float
        Mass of cement produced (in tonnes).
    cement_to_mortar_coeff : float
        Share of the produced cement that will be allocated to mortar production.
    cement_use_mortar : float
        Amount of cement needed to produce mortar (in kg of cement/m3 of mortar).
    volumic_mass_mortar : float
        Volumic mass mortar in kg/m3.

    Returns
    -------
    mass_mortar : float
        Mass of mortar produced (in tonnes).

    """
    volume_mortar = mass_cement * cement_to_mortar_coeff / cement_use_mortar
    # division by 1000 to switch from kg to tonnes
    mass_mortar = volume_mortar * volumic_mass_mortar / 1000
    return mass_mortar


def water_use_mortar(mass_mortar, volumic_mass_mortar, water_use_mortar):
    """
    This function calculates the water consumption for the mortar production.

    Parameters
    ----------
    mass_mortar : float
        Amount of mortar produced.
    volumic_mass_mortar : float
        Volumic mass of mortar in kg/m3.
    water_use_mortar : float
        Coefficient of water consumed during mortar production in kg/m3.

    Returns
    -------
    volume_water : float
        Amount of water consumed for mortar production (in tonnes).

    """
    # As the water consumption is provided in kg water/m3 of mortar, wee need first to
    # convert the mass of mortar (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_mortar = mass_mortar / (volumic_mass_mortar / 1000)
    water_use_mortar = volume_mortar * water_use_mortar / 1000
    return water_use_mortar


def sand_use_mortar(mass_mortar, volumic_mass_mortar, sand_use_mortar):
    """
    This function calculates the sand consumption for the mortar production.

    Parameters
    ----------
    mass_mortar : float
        Amount of mortar produced.
    volumic_mass_mortar : float
        Volumic mass of mortar in kg/m3.
    sand_use_mortar : float
        Coefficient of sand consumed during mortar production in kg/m3.

    Returns
    -------
    sand_use_mortar : float
        Amount of sand consumed for mortar production (in tonnes).

    """
    # As the sand consumption is provided in kg water/m3 of mortar, wee need first to
    # convert the mass of mortar (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_mortar = mass_mortar / (volumic_mass_mortar / 1000)
    sand_use_mortar = volume_mortar * sand_use_mortar / 1000
    return sand_use_mortar


def lime_use_mortar(mass_mortar, volumic_mass_mortar, lime_use_mortar):
    """
    This function calculates the lime consumption for the mortar production.

    Parameters
    ----------
    mass_mortar : float
        Amount of mortar produced.
    volumic_mass_mortar : float
        Volumic mass of mortar in kg/m3.
    lime_use_mortar : float
        Coefficient of lime consumed during mortar production in kg/m3.

    Returns
    -------
    lime_use_mortar : float
        Amount of lime consumed for mortar production (in tonnes).

    """
    # As the lime consumption is provided in kg water/m3 of mortar, wee need first to
    # convert the mass of mortar (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_mortar = mass_mortar / (volumic_mass_mortar / 1000)
    lime_use_mortar = volume_mortar * lime_use_mortar / 1000
    return lime_use_mortar


def elec_use_mortar(mass_mortar, volumic_mass_mortar, elec_use_mortar):
    """
    This function calculates the electricity consumption for the mortar production.

    Parameters
    ----------
    mass_concrete : float
        Amount of concrete produced.
    volumic_mass_mortar : float
        Volumic mass of mortar in kg/m3.
    elec_use_mortar : float
        Coefficient of electricity consumed during mortar production in kWh/m3.

    Returns
    -------
    elec_use_mortar : float
        Amount of electricity consumed for mortar production (in TJ).

    """
    # As the electricity consumption is provided in kg kWh/m3 of mortar, wee need first to
    # convert the mass of mortar (in tonnes) to m3. The division by 1000 to switch from kg to tonnes
    volume_mortar = mass_mortar / (volumic_mass_mortar / 1000)
    elec_use_mortar = volume_mortar * elec_use_mortar
    # To shift from kWh to TJ,one needs to multiply by 0.0000036 (1 kWh <=> 0.0000036 TJ)
    elec_use_mortar = elec_use_mortar * 0.0000036
    return elec_use_mortar


def water_emission_cement(water_use, fraction_water_emission):
    """
    This function calculates the amount of water lost as by-product (vapor)

    Parameters
    ----------
    water_use : float
        Amount of wtaer consumed for a process (can be concrete production, mortar
        production...), in tonnes.
    fraction_water_emission : float
        Fraction of water that is lost (in %).

    Returns
    -------
    water_emission_cement : float
        Amount of water lost/emitted (in tonnes).

    """
    water_emission_cement = water_use * fraction_water_emission
    return water_emission_cement


####################################################################################
# -------------------- Equations for mass & carbon balances ---------------------- #
####################################################################################


def mass_carbon_balance(mass_clinker, f_cao_on_clinker):
    """
    Calculate the supply of CaCO3, mass difference and carbon difference in tonne (to varify the mass and carbon balances for the production of clinker).


    Parameters
    ----------
    mass_clinker : float
        mass of clinker produced in tonnes.
    f_cao_on_clinker : float
        Fraction of CaO on clinker (fraction).

    Returns
    -------
    tuple of float
        Supply of CaCO3 (in tonnes) and Mass Difference and Carbon Difference between input and output (in tonnes).

    """
    # As the mass of clinker is provided in tonnes, we need to multiply it by 1E6 to get
    # the value in g.
    # The denominator is the division of the molecular weight of calcium oxide
    # (56.0774 g/mol) by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    m_caco3_supply = f_cao_on_clinker * mass_clinker * 1e6 / (56.0774 / 100.0869)
    # Division by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    n_caco3_in = m_caco3_supply / 100.0869
    # Multiplication by the molar weigth of carbon: 12.0096 g/mol
    mass_carbon_in = n_caco3_in * 12.0096
    # Multiplication by the molecular weigth of CaO (56.0774 g/mol).
    mass_cao_out = n_caco3_in * 56.0774
    # Multiplication by the molecular weigth of CO2 (44.009 g/mol).
    mass_co2_out = n_caco3_in * 44.009
    # Multiplication by the fraction of molar weigth of Carbon (12.0096 g/mol) on
    # molecular weigth of CO2 (44.009 g/mol).
    mass_carbon_out = mass_co2_out * 12.0096 / 44.009
    # The final results are divided by 1E6 to convert from g to tonnes.
    delta_mass = (m_caco3_supply - mass_cao_out - mass_co2_out) / 1e6
    delta_c = (mass_carbon_in - mass_carbon_out) / 1e6
    return m_caco3_supply, delta_mass, delta_c


def m_caco3_supply(mass_clinker, f_cao_on_clinker):
    """
    This function verifies the mass and carbon balances for the production of clinker.

    Parameters
    ----------
    mass_clinker : float
        mass of clinker produced in tonnes.
    f_cao_on_clinker : float
        Fraction of CaO on clinker (fraction).

    Returns
    -------
    delta_mass : float
        Mass difference between input and output, in tonnes.
    delta_c : float
        Mass difference between input and output, in tonnes.

    """
    # As the mass of clinker is provided in tonnes, we need to multiply it by 1E6 to get
    # the value in g.
    # The denominator is the division of the molecular weight of calcium oxide
    # (56.0774 g/mol) by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    m_caco3_supply = f_cao_on_clinker * mass_clinker * 1e6 / (56.0774 / 100.0869)
    return m_caco3_supply


def delta_mass(mass_clinker, f_cao_on_clinker):
    """
    This function verifies the mass and carbon balances for the production of clinker.

    Parameters
    ----------
    mass_clinker : float
        mass of clinker produced in tonnes.
    f_cao_on_clinker : float
        Fraction of CaO on clinker (fraction).

    Returns
    -------
    delta_mass : float
        Mass difference between input and output, in tonnes.
    delta_c : float
        Mass difference between input and output, in tonnes.

    """
    # As the mass of clinker is provided in tonnes, we need to multiply it by 1E6 to get
    # the value in g.
    # The denominator is the division of the molecular weight of calcium oxide
    # (56.0774 g/mol) by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    m_caco3_supply = f_cao_on_clinker * mass_clinker * 1e6 / (56.0774 / 100.0869)
    # Division by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    n_caco3_in = m_caco3_supply / 100.0869
    # Multiplication by the molar weigth of carbon: 12.0096 g/mol
    # Multiplication by the molecular weigth of CaO (56.0774 g/mol).
    mass_cao_out = n_caco3_in * 56.0774
    # Multiplication by the molecular weigth of CO2 (44.009 g/mol).
    mass_co2_out = n_caco3_in * 44.009
    # The final results are divided by 1E6 to convert from g to tonnes.
    delta_mass = (m_caco3_supply - mass_cao_out - mass_co2_out) / 1e6
    return delta_mass


def delta_c(mass_clinker, f_cao_on_clinker):
    """
    This function verifies the mass and carbon balances for the production of clinker.

    Parameters
    ----------
    mass_clinker : float
        mass of clinker produced in tonnes.
    f_cao_on_clinker : float
        Fraction of CaO on clinker (fraction).

    Returns
    -------
    delta_mass : float
        Mass difference between input and output, in tonnes.
    delta_c : float
        Mass difference between input and output, in tonnes.

    """
    # As the mass of clinker is provided in tonnes, we need to multiply it by 1E6 to get
    # the value in g.
    # The denominator is the division of the molecular weight of calcium oxide
    # (56.0774 g/mol) by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    m_caco3_supply = f_cao_on_clinker * mass_clinker * 1e6 / (56.0774 / 100.0869)
    # Division by the molecular weigth of Calcium carbonate (100.0869 g/mol).
    n_caco3_in = m_caco3_supply / 100.0869
    # Multiplication by the molar weigth of carbon: 12.0096 g/mol
    mass_carbon_in = n_caco3_in * 12.0096
    # Multiplication by the molecular weigth of CO2 (44.009 g/mol).
    mass_co2_out = n_caco3_in * 44.009
    # Multiplication by the fraction of molar weigth of Carbon (12.0096 g/mol) on
    # molecular weigth of CO2 (44.009 g/mol).
    mass_carbon_out = mass_co2_out * 12.0096 / 44.009
    # The final results are divided by 1E6 to convert from g to tonnes.
    delta_c = (mass_carbon_in - mass_carbon_out) / 1e6
    return delta_c


####################################################################################
# -------------- Equations for carbonation (concrete and mortar) ----------------- #
####################################################################################


def carbonation_rate(carb_coeff_env, carb_coeff_add, carb_coeff_co2, carb_coeff_cc):
    """
    This function calculates the carbonation rate of concrete. It is based on Equation
    (1) from the supplement of Zi Huang et al. (2023) and corresponds to Equation 3.1
    from the technical documentation.

    Parameters
    ----------
    carb_coeff_env : float
        Carbonated coefficient under different environments.
    carb_coeff_add : float
        Carbonated coefficients of cement additives.
    carb_coeff_co2 : float
        Carbonated coefficients from the CO2 concentration.
    carb_coeff_cc : float
        Carbonated coefficient from the coating and cover.

    Returns
    -------
    carbonation_rate : float
        Carbonation rate coefficient of a particular strength class of concrete
        (in mm/(year)^(1/2)).

    """
    carbonation_rate = carb_coeff_env * carb_coeff_add * carb_coeff_co2 * carb_coeff_cc
    return carbonation_rate


def carbonation_depth(carbonation_rate, react_time):
    """
    This function calculates the concrete carbonation depth, based on equation (2) from
    the supplement of Zi Huang et al. (2023)  and corresponds to Equation 3.2 from the
    technical documentation.

    Parameters
    ----------
    carbonation_rate : float
        Carbonation rate coefficient of a particular strength class of concrete.
    react_time : float
        Reaction time where the carbonation is taking place (most usually in years).

    Returns
    -------
    carbonation_depth : float
        Concrete carbonation depth in mm.

    """
    carbonation_depth = carbonation_rate * (react_time) ** (1 / 2)
    return carbonation_depth


def concrete_carbonated(carbonation_depth, cement_on_concrete, thick):
    """
    This function calculates the amount of carbonated concrete over a certain period of
    time. It is based on equation (3) from the supplement of Zi Huang et al. (2023)  and
    corresponds to Equation 3.3 from the technical documentation.

    Parameters
    ----------
    carbonation_depth : float
        Concrete carbonation depth in mm.
    cement_on_concrete : float
        Cement content in concrete (fraction).
    thick : float
        Thickness of the concrete structure in mm.

    Returns
    -------
    concrete_carbonated : float
        Amount coefficient of carbonated concrete (fraction).

    """
    concrete_carbonated = cement_on_concrete * carbonation_depth / thick
    return concrete_carbonated


def co2_carbonated_concrete(
    cement_on_concrete,
    carbonation_rate,
    clink_on_cem,
    cao_in_clinker,
    cao_to_caco3,
    thick,
    react_time,
    mass_cement,
    cement_distrib,
):
    """
    This function calculates the amount of CO2 that has been absorbed after a certain
    reaction time of use (lifetime) of concrete, based on the carbonation effect.
    Derived from equation (6) from the supplement of Zi Huang et al. (2023) and
    corresponds to Equation 3.4 from the technical documentation. The final results is
    given per year.


    Parameters
    ----------
    cement_on_concrete : float
        Fraction content of cement in concrete (in kg/m3).
    carbonation_rate : float
        Carbonation rate coefficient of a particular strength class of concrete )
        (in mm/(year)^(0.5)).
    clink_on_cem : float
        Fraction of clinker on cement (fraction).
    cao_in_clinker : float
        Fraction of CaO in clinker (fraction).
    cao_to_caco3 : float
        Percentage of CaO converted to CaCO3 (fraction).
    thick : float
        Average thickness of the cement-product under consideration (in mm).
    react_time : integer
        Lifetime of the cement-product's use (in years).
    mass_cement : float
        Mass of cement produced (in tonnes).
    cement_distrib : float
        Fraction of cement used in the respective product type (concrete, mortar...)
        (fraction).

    Returns
    -------
    co2_carbonated : float
        Amount of CO2 that has been carbonated from the concrete structure
        (in tonnes).

    """
    # Based on literature data, the volumic mass of cement is on average 0.002162
    # tonnes/m3. This value is needed to convert the cement_on_concrete into tonnes.
    co2_carbonated = (
        (
            cement_on_concrete
            * carbonation_rate
            * clink_on_cem
            * cao_in_clinker
            * cao_to_caco3
            * mass_cement
            * cement_distrib
            / (0.002162)
            * ((react_time) ** (1 / 2))
        )
        / thick
        * 44.0095
        / 56.0774
    )
    return co2_carbonated


def co2_carbonated_concrete_per_year(
    df,
):
    """
    This function is kind of a test to comply with the "to_frames()" function but it
    is not useful so far since dataframes/lists cannnot be stored in the"to_frames()".
    Maik would need to check on this.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    co2_carbonated_concrete_per_year : TYPE
        DESCRIPTION.

    """
    co2_carbonated_concrete_per_year = df
    return co2_carbonated_concrete_per_year


def co2_carbonated_mortar(
    mass_cement,
    coeff_mortar_on_cement,
    ratio_mortar_type,
    carb_coeff_mortar,
    react_time,
    thick,
    clink_on_cem,
    cao_in_clinker,
    cao_to_caco3,
):
    """
    This function calculates the amount of CO2 that has been absorbed after a certain
    reaction time of use (lifetime) of rendering mortar, based on the carbonation effect.
    Derived from equation (XXX) from the supplement of Zi Huang et al. (2023) and
    corresponds to Equation XXX from the technical documentation. The final results is
    given as a total value (not per year).

    ----------
    mass_cement : float
        Amount of cement produced (in tonnes).
    coeff_mortar_on_cement : float
        Fraction of cement used as a mortar (fraction).
    ratio_mortar_type : float
        Fraction of rendering mortar on total mortar cement (fraction).
    carb_coeff_mortar : float
        Carbonation diffusion rate of mortar (in mm/((year)^0.5)).
    react_time : float
        Lifetime of mortar use (in years).
    thick : float
        Average thickness of the cement-product under consideration (in mm).
    clink_on_cem : float
        Fraction of clinker on cement (fraction).
    cao_in_clinker : float
        Fraction of CaO in clinker (fraction).
    cao_to_caco3 : float
        Percentage of CaO converted to CaCO3 (fraction).


    Returns
    -------
    co2_carbonated : float
        Amount of CO2 that has been carbonated from the concrete structure
        (in tonnes).

    """

    # The last factor of the multiplication is a division of the molecular weigt of CO2
    # (44.0095 g/mol) by the molecular weigth of CaO (56.0774 g/mol) both constants.
    # Based on literature data, the volumic mass of cement is on average 2.162 kg/m3
    co2_carbonated_mortar = (
        mass_cement
        * coeff_mortar_on_cement
        * ratio_mortar_type
        * carb_coeff_mortar
        * (react_time) ** (1 / 2)
        / (thick)
        * clink_on_cem
        * cao_in_clinker
        * cao_to_caco3
        * 44.0095
        / 56.0774
    )

    return co2_carbonated_mortar


def co2_carbonated_mortar_per_year(
    df,
):
    """
    This function is kind of a test to comply with the "to_frames()" function but it
    is not useful so far since dataframes/lists cannnot be stored in the"to_frames()".
    Maik would need to check on this.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    co2_carbonated_concrete_per_year : TYPE
        DESCRIPTION.

    """
    co2_carbonated_mortar_per_year = df
    return co2_carbonated_mortar_per_year
