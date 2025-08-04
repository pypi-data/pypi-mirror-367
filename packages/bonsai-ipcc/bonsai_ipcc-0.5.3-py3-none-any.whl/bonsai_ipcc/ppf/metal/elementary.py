from ...industry.metal.elementary import (
    ch4_coke,
    ch4_dri,
    ch4_pigiron,
    ch4_sinter,
    ch4_steel_total,
    co2_coke_tier1a_,
    co2_dri_tier1_,
    co2_flaring,
    co2_pellet,
    co2_pigiron,
    co2_sinter_tier1_,
    co2_steel_total_tier1_,
    co2_steelmaking_tier1_,
    n2o_flaring,
)


def ck_calculated(coke, coke_activity_per_reg):
    """Coke production per activity (t/yr)

    Parameters
    ----------
    coke: float
        amount of produced coke (t/yr)
    coke_activity_per_reg: float
        ratio factor (t/t)

    Returns
    -------
    float
        amoount of coke produced by activity (t/yr)
    """
    return coke * coke_activity_per_reg


def by_product_supply(coke, ratio):
    """By-products produced in coke production (t/yr)

    Parameters
    ----------
    coke: float
        amount of produced coke (t/yr)
    ratio: float
        ratio factor (t/t)

    Returns
    -------
    float
        amoount of by-product produced by activity (t/yr)
    """
    return coke * ratio


def coal_use(coke_output, coal_coke_ratio):
    """Coal input for coke production (t/yr)

    Parameters
    ----------
    coke_output: float
        amount of produced coke (t/yr)
    coal_coke_ratio: float
        conversion factor (t/t)

    Returns
    -------
    float
        amoount of coal for coke production (t/yr)
    """
    return coke_output * coal_coke_ratio


def energy_use(product_output, energy_product_ratio):
    """Energy input for coke production (GJ/yr)

    Parameters
    ----------
    coke_output: float
        amount of produced coke (t/yr)
    energy_coke_ratio: float
        conversion factor (GJ/t)

    Returns
    -------
    float
        amoount of energy for coke production (GJ/yr)
    """
    return product_output * energy_product_ratio


def emission(product_output, emission_product_ratio):
    """Emission output for coke production (t/yr)

    Parameters
    ----------
    coke_output: float
        amount of produced coke (t/yr)
    emisssion_coke_ratio: float
        conversion factor (t/t)

    Returns
    -------
    float
        amoount of emission for coke production (t/yr)
    """
    return product_output * emission_product_ratio


def transf_coeff(reference_supply, use):
    """Transfer coefficient (t/t)

    The transfer coeeficient is defined as reference output devided by used input.

    Parameters
    ----------
    reference_supply : float
        amount of reference product supplied (t/yr)
    use : float
        amount of used input (t/yr)
    Returns
    -------
    float
        Transfer coefficient
    """
    return reference_supply / use


def steel_calculated(steel, steel_activity_per_reg):
    """Steel production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    steel_activity_per_reg: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of steel produced by activity (t/yr)
    """
    return steel * steel_activity_per_reg


def q_dri_calculated(steel, dri_per_steel):
    """Direct reduced iron intermediate production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    dri_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of DRI produced by activity as intermediate product (t/yr)

    """
    return steel * dri_per_steel


def q_pellet_calculated(steel, pellet_per_steel):
    """Pellet intermediate production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    pellet_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of pellet produced by activity as intermediate product (t/yr)

    """
    return steel * pellet_per_steel


def q_pigiron_calculated(steel, pigiron_per_steel):
    """pig iron intermediate production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    pigiron_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of pig iron produced by activity as intermediate product (t/yr)

    """
    return steel * pigiron_per_steel


def q_sinter_calculated(steel, sinter_per_steel):
    """sinter intermediate production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    sinter_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of sinter produced by activity as intermediate product (t/yr)

    """
    return steel * sinter_per_steel


def q_bfg_calculated(steel, bfg_per_steel):
    """blast furnace gas production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    bfg_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of bfg produced by activity as intermediate product (t/yr)

    """
    return steel * bfg_per_steel


def q_ldg_calculated(steel, ldg_per_steel):
    """converter gas production per activity (t/yr)

    Parameters
    ----------
    steel: float
        amount of produced steel (t/yr)
    ldg_per_steel: float
        ratio factor (t/t)

    Returns
    -------
    float
        amount of ldg produced by activity as intermediate product (t/yr)

    """
    return steel * ldg_per_steel


def feedstock_use(product_output, feedstock_product_ratio):
    """Feedstock input for coke production (t/yr)

    Parameters
    ----------
    product_output: float
        amount of produced coke (t/yr)
    energy_product_ratio: float
        conversion factor (t/t)

    Returns
    -------
    float
        amount of feedstock for product production (t/yr)
    """
    return product_output * feedstock_product_ratio


def iron_ore_use_dri(dri, factor):
    """Iron ore input (t/yr)

    Parameters
    ----------
    dri: float
        amount of direct reduced iron (t/yr)
    factor: float
        iron ore per dri (t/t)

    Returns
    -------
    float
        amount of iron ore (t/yr)
    """

    return dri * factor


def iron_ore_use_pigiron(pig_iron, factor):
    """Iron ore input (t/yr)

    Parameters
    ----------
    pig_iron: float
        amount of pig_iron (t/yr)
    factor: float
        iron ore per dri (t/t)

    Returns
    -------
    float
        amount of iron ore (t/yr)
    """

    return pig_iron * factor
