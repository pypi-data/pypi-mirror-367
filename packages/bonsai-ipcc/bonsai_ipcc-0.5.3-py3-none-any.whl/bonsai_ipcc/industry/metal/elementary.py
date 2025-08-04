def co2_coke_tier1a_(ck, ef_co2):
    """
    Equation 4.1 (tier 1a).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_coke_tier1a_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier1a_ = ck * ef_co2
    return co2_coke_tier1a_


def ch4_coke(ck, ef_ch4):
    """
    Equation 4.1a (tier 1a).

    This function calculates the CH4 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    ef_ch4 (t/t): float
        Emission factor CO2.

    Returns
    -------
    ch4_coke_tier1a_ (t/year): float
        Total CH4 emissions generated from coke production (in tonnes CH4).

    """
    ch4_coke = ck * ef_ch4
    return ch4_coke


def co2_coke_tier1b_(cc, ck, c_cc, c_ck):
    """
    Equation 4.1b (tier 1b).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    ck (t/year): float
        Quantity of coke produced.
    cc (t/year): float
        Quantity of coking coal produced.
    c_ck (t/t): float
        default carbon content of metallurgical coke.
    c_cc (t/t): float
        default carbon content of coking coal.

    Returns
    -------
    co2_coke_tier1b_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier1b_ = (cc * c_cc - ck * c_ck) * 44 / 12
    return co2_coke_tier1b_


def c_pm(pm_a, c_a):
    """
    Part of Equation 4.2 (tier 2).

    This function calculates the carbon content of process materials a used in coke production.

    Argument
    --------
    pm_a (t/yr): float
        quantity of process materials consumed for metallurgical coke production
    c_a (t/t): float
        country-specific carbon content of material input

    Returns
    -------
    c_pm (t/year): float
        Carbon quantity of process material a in coke production.

    """
    c_pm = pm_a * c_a
    return c_pm


def c_cob(cob_b, c_b):
    """
    Part of Equation 4.2 (tier 2).

    This function calculates the carbon content of process materials a used in coke production.

    Argument
    --------
    cob_b (t/yr): float
        quantity of by-product b produced in metallurgical coke production
    c_b (t/t): float
        country-specific carbon content of by-product b

    Returns
    -------
    c_pm (t/year): float
        Carbon quantity of by-product b from coke production.

    """
    c_cob = cob_b * c_b
    return c_cob


def co2_coke_tier2_(cc, c_cc, c_pm, bg, c_bg, co, c_co, cog, c_cog, c_cob, e_flaring):
    """
    Equation 4.2 (tier 2).

    This function calculates the CO2 emissions from coke production.

    Argument
    --------
    cc (t/year): float
        Quantity of coking coal produced.
    c_cc (t/t): float
        country-specific carbon content of coking coal.
    c_pm (t/yr): float
        quantity of carbon from all other process materials consumed for metallurgical coke production
    bg (t/yr): float
        quantity of blast furnace gas consumed in coke oven
    c_bg (t/t): float
        country-specific carbon content of blast furnace gas
    co (t/yr): float
        quantity of metallurgical coke produced
    c_co (t/t): float
        country-specific carbon content of metallurgical coke
    cog (t/yr): float
        quantity of coke oven gas produced but not recirculated and therefore not consumed for metallurgical coke production
    c_cog (t/t): float
        country-specific carbon content of coke oven gas
    c_cob_b (t/yr): float
        quantity of carbon in all coke oven by-products
    e_flaring (t/yr): float
        co2 emissions from flaring, deducted from the carbon mass balance, as the corresponding emissions are estimated as fugitive emissions using the methodology described in Section 4.3.2.2 Chapter 4 Volume 2 of the 2019 Refinement


    Returns
    -------
    co2_coke_tier2_ (t/year): float
        Total CO2 emissions generated from coke production (in tonnes CO2).

    """
    co2_coke_tier2_ = (
        (cc * c_cc + c_pm + bg * c_bg - co * c_co - cog * c_cog - c_cob - e_flaring)
        * 44
        / 12
    )
    return co2_coke_tier2_


def co2_steelmaking_tier1_(q, ef_co2):
    """
    Equation 4.4 (tier 1). Revised to simplify.

    This function calculates the CO2 emissions from iron and steel production.

    Argument
    --------
    q (t/year): float
        Quantity of steel produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_steelmaking_tier1_ (t/year): float
        Total CO2 emissions generated from iron and steel production (in tonnes CO2).

    """
    co2_steelmaking_tier1_ = q * ef_co2
    return co2_steelmaking_tier1_


def co2_pigiron(q, ef_co2):
    """
    Equation 4.5 (tier 1).

    This function calculates the CO2 emissions from pig iron production.

    Argument
    --------
    q (t/year): float
        Quantity of pig iron produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_pigiron (t/year): float
        Total CO2 emissions generated from pig iron production (in tonnes CO2).

    """
    co2_pigiron = q * ef_co2
    return co2_pigiron


def co2_dri_tier1_(q, ef_co2):
    """
    Equation 4.6 (tier 1).

    This function calculates the CO2 emissions from direct reduced iron production.

    Argument
    --------
    q (t/year): float
        Quantity of direct reduced iron produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_dri_tier1_ (t/year): float
        Total CO2 emissions generated from direct reduced iron production (in tonnes CO2).

    """
    co2_dri_tier1_ = q * ef_co2
    return co2_dri_tier1_


def co2_sinter_tier1_(q, ef_co2):
    """
    Equation 4.7 (tier 1).

    This function calculates the CO2 emissions from sinter production.

    Argument
    --------
    q (t/year): float
        Quantity of sinter produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_dri_tier1_ (t/year): float
        Total CO2 emissions generated from sinter production (in tonnes CO2).

    """
    co2_sinter_tier1_ = q * ef_co2
    return co2_sinter_tier1_


def co2_pellet(q, ef_co2):
    """
    Equation 4.8 (tier 1).

    This function calculates the CO2 emissions from pellet production.

    Argument
    --------
    q (t/year): float
        Quantity of pellet produced.
    ef_co2 (t/t): float
        Emission factor CO2.

    Returns
    -------
    co2_dri_tier1_ (t/year): float
        Total CO2 emissions generated from pellet production (in tonnes CO2).

    """
    co2_pellet = q * ef_co2
    return co2_pellet


def co2_flaring(q_bfg, q_ldg, r_bfg, cc_bfg, r_ldg, cc_ldg):
    """
    Equation 4.8a (tier 1).

    This function calculates the CO2 emissions from gas flaring.

    Argument
    --------
    q_bfg (t/year): float
        Quantity of blast furnace gas produced.
    q_ldg (t/year): float
        Quantity of converter gas produced.
    r_bfg (t/t): float
        rate of BFG removed from the production steam and then flared.
    cc_bfg (t/t): float
        carbon content of BFG
    r_ldg (t/t): float
        rate of LDG removed from the production steam and then flared.
    cc_ldg (t/t): float
        carbon content of LDG

    Returns
    -------
    co2_flaring (t/year): float
        Total CO2 emissions generated from gas flaring (in tonnes CO2).

    """
    co2_flaring = (q_bfg * r_bfg * cc_bfg * 44 / 12) + (
        q_ldg * r_ldg * cc_ldg * 44 / 12
    )
    return co2_flaring


def co2_steel_total_tier1_(steel, dri, pigiron, sinter, pellet, flaring):
    """
    Equation 4.x (tier 1).

    Required to sum up all subprocess of steel prodcution.

    Argument
    --------
    steel (t/year): float
        CO2 from steelmaking
    dri (t/year): float
        CO2 from direct reduced iron
    pigiron (t/year): float
        CO2 from pigiron production
    sinter (t/year): float
        CO2 from sinter ore production
    pellet (t/year): float
        CO2 from iron pellet production
    flaring (t/year): float
        CO2 flaring

    Returns
    -------
    co2_steel_total (t/yr):  float
        total co2 of steel production
    """
    co2_steel_total = steel + dri + pigiron + sinter + pellet + flaring
    return co2_steel_total


def co2_steel_total_tier2_(steel, sinter, dri):
    """
    Equation 4.x (tier 1).

    Required to sum up all subprocess of steel prodcution.

    Argument
    --------
    steel (t/year): float
        CO2 from steelmaking
    dri (t/year): float
        CO2 from direct reduced iron
    sinter (t/year): float
        CO2 from sinter ore production

    Returns
    -------
    co2_steel_total (t/yr):  float
        total co2 of steel production
    """
    co2_steel_total = steel + dri + sinter
    return co2_steel_total


def ch4_steel_total(sinter, dri, pigiron):
    """
    Equation 4.x (tier 1).

    Required to sum up all subprocess of steel prodcution.

    Argument
    --------
    pigiron (t/year): float
        CH4 from pig iron production
    dri (t/year): float
        CH4 from direct reduced iron
    sinter (t/year): float
        CH4 from sinter ore production

    Returns
    -------
    ch4_steel_total (t/yr):  float
        total ch4 of steel production
    """
    ch4_steel_total = pigiron + dri + sinter
    return ch4_steel_total


def c_cob_a(cob_a, c_a):
    """
    Part of Equation 4.9 (tier 2).

    This function calculates the quantity of carbon in onside coke oven by-product a used iron and steel production.

    Argument
    --------
    cob_a (t/year): float
        quantity of onsite coke oven by-product a, consumed in blast furnace
    c_a (t/t): float
        carbon content of onsite coke oven by-product a, consumed in blast furnace

    Returns
    -------
    c_cob_a (t/yr):  float
        quantity of carbon in onside coke oven by-product a
    """
    c_cob_a = cob_a * c_a
    return c_cob_a


def c_o_b(o_b, c_b):
    """
    Part of Equation 4.9 (tier 2).

    This function calculates the quantity of carbon in other carbonaceous and process material b used iron and steel production.

    Argument
    --------
    o_b (t/year): float
        quantity of other carbonaceous and process material b, consumed in iron and steel prodcution
    c_b (t/t): float
        carbon content of carbonaceous and process material b

    Returns
    -------
    c_o_b (t/yr):  float
        quantity of carbon in other carbonaceous and process material b
    """
    c_o_b = o_b * c_b
    return c_o_b


def co2_steelmaking_tier2_(
    pc,
    c_pc,
    c_cob_a,
    ci,
    c_ci,
    l,
    c_l,
    d,
    c_d,
    ce,
    c_ce,
    c_o_b,
    cog,
    c_cog,
    s,
    c_s,
    ip,
    c_ip,
    bfg,
    c_bfg,
):
    """
    Equation 4.9 (tier 2).

    This function calculates the total CO2 emissions of iron and steel production.

    Argument
    --------
    pc (t/year): float
        quantity of coke consumed in iron and steel production
    c_pc (t/t): float
        carbon factor for coke
    c_cob_a (t/year): float
        quantity of onsite coke oven by-product a, consumed in blast furnace
    ci (t/year): float
        quantity of coal directly injected into blast furnace
    c_ci (t/t): float
        carbon factor for coal injected
    l (t/year): float
        quantity of limestone consumed in iron and steel production
    c_l (t/t): float
        carbon factor for limestone
    d (t/year): float
        quantity of dolomite consumed in iron and steel production
    c_d (t/t): float
        carbon factor for dolomite
    ce (t/year): float
        quantity of carbon electrodes consumed in EAFs
    c_ce (t/t): float
        carbon factor for carbon electrodes
    c_o_b (t/year): float
        quantity of carbon in all other carbonaceous and process material b
    cog (t/year): float
        quantity of coke oven gas consumed in stationary combustion equipment
    c_cog (t/t): float
        carbon factor for coke oven gas
    s (t/year): float
        quantity of steel produced
    c_s (t/t): float
        carbon factor for steel
    ip (t/year): float
        quantity of coke consumed in iron and steel production
    c_ip (t/t): float
        carbon factor for coke
    bfg (t/year): float
        quantity of blast furnace gas transferred off site or to other facilities in an integrated plant
    c_bfg (t/t): float
        carbon factor for blast furnace gas
    Returns
    -------
    co2_steelmaking_tier2_ (t/year): float
        Total CO2 emissions of iron and steel production (in tonnes CO2).

    """
    co2_steelmaking_tier2_ = (
        (
            pc * c_pc
            + c_cob_a
            + ci * c_ci
            + l * c_l
            + d * c_d
            + ce * c_ce
            + c_o_b
            + cog * c_cog
            - s * c_s
            - ip * c_ip
            - bfg * c_bfg
        )
        * 44
        / 12
    )
    return co2_steelmaking_tier2_


def c_pm_a(pm_a, c_a):
    """
    Part of Equation 4.10 (tier 2).

    This function calculates the carbon quantity of process material a sinter production.

    Argument
    --------
    pm_a (t/year): float
        quantity of process material a, other than those listed as separate terms
    c_a (t/t): float
        carbon factor for material a
    Returns
    -------
    c_pm_a (t/year): float
        carbon quantity of process material a.

    """
    c_pm_a = pm_a * c_a
    return c_pm_a


def co2_sinter_tier2_(cbr, c_cbr, cog, c_cog, bfg, c_bfg, c_pm_a):
    """
    Equation 4.10 (tier 2).

    This function calculates the CO2 emissions from sinter production.

    Argument
    --------
    cbr (t/year): float
        quantity of purchased and on-site produced coke breeze used for sinter production
    c_cbr (t/t): float
        carbon factor for coke
    cog (t/year): float
        quantity of coke oven gas consumed in stationary combustion equipment in iron and steel production
    c_cog (t/t): float
        carbon factor for coke oven gas
    bfg (t/year): float
        quantity of blast furnace gas transferred off site or to other facilities in an integrated plant
    c_bfg (t/t): float
        carbon factor for blast furnace gas
    c_pm_a (t/year): float
        quantity of carbon in all process materials, other than those listed as separate terms
    Returns
    -------
    co2_sinter_tier2_ (t/year): float
        CO2 emissions generated from sinter production (in tonnes CO2).

    """
    co2_sinter_tier2_ = (
        ((cbr * c_cbr) + (cog * c_cog) + (bfg * c_bfg) + c_pm_a) * 44 / 12
    )
    return co2_sinter_tier2_


def co2_dri_tier2_(dri_ng, c_ng, dri_bz, c_bz, dri_ck, c_ck):
    """
    Equation 4.11 (tier 2).

    This function calculates the CO2 emissions from direct induced iron production.

    Argument
    --------
    dri_ng (GJ/year): float
        amount of natural gas used in direct reduced iron production
    c_ng (t/GJ): float
        carbon factor for natural gas
    dri_bz (GJ/year): float
        amount of coke breeze used in direct reduced iron production
    c_bz (t/GJ): float
        carbon factor for coke breeze
    dri_ck (GJ/year): float
        amount of metallurgical coke used in direct reduced iron production
    c_ck (t/GJ): float
        carbon factor for metallurgical coke
    Returns
    -------
    co2_dri_tier2_ (t/year): float
        CO2 emissions generated from direct induced iron production (in tonnes CO2).

    """
    co2_dri_tier2_ = ((dri_ng * c_ng) + (dri_bz * c_bz) + (dri_ck * c_ck)) * 44 / 12
    return co2_dri_tier2_


def ch4_sinter(si, ef_si):
    """
    Equation 4.12 (tier 1).

    This function calculates the CH4 emissions from sinter production.

    Argument
    --------
    si (t/year): float
        amount of sinter produced
    ef_si (t/GJ): float
        ch4 emission factor for sinter
    Returns
    -------
    ch4_sinter (t/year): float
        CH4 emissions generated from sinter production.

    """
    ch4_sinter = si * ef_si
    return ch4_sinter


def ch4_pigiron(pi, ef_pi):
    """
    Equation 4.13 (tier 1).

    This function calculates the CH4 emissions from blast furnace production of pig iron.

    Argument
    --------
    pi (t/year): float
        amount of pig iron produced
    ef_pi (t/GJ): float
        ch4 emission factor for pig iron
    Returns
    -------
    ch4_pigiron (t/year): float
        CH4 emissions generated from sinter production.

    """
    ch4_pigiron = pi * ef_pi
    return ch4_pigiron


def ch4_dri(dri, ef_dri):
    """
    Equation 4.14 (tier 1).

    This function calculates the CH4 emissions from direct reduced iron production.

    Argument
    --------
    dri (t/year): float
        amount of steel by direct reduced iron production
    ef_dri (t/GJ): float
        ch4 emission factor for pig iron
    Returns
    -------
    ch4_dri (t/year): float
        CH4 emissions generated from direct reduced iron production.

    """
    ch4_dri = dri * ef_dri
    return ch4_dri


def n2o_flaring(q_bfg, q_ldg, r_bfg, ef_bfg, r_ldg, ef_ldg):
    """
    Equation 4.14a (tier 1).

    This function calculates the N2O emissions from gas flaring.

    Argument
    --------
    q_bfg (t/year): float
        Quantity of blast furnace gas produced.
    q_ldg (t/year): float
        Quantity of converter gas produced.
    r_bfg (t/t): float
        rate of BFG removed from the production steam and then flared.
    ef_bfg (t/t): float
        n2o emission factor for BFG flared
    r_ldg (t/t): float
        rate of LDG removed from the production steam and then flared.
    ef_ldg (t/t): float
        n2o emission factor for LDG flared

    Returns
    -------
    n2o_flaring (t/year): float
        Total N2O emissions generated from gas flaring (in tonnes).

    """
    n2o_flaring = (q_bfg * r_bfg * ef_bfg) + (q_ldg * r_ldg * ef_ldg)
    return n2o_flaring


def co2_ferroalloy_tier1_(mp, ef):
    """
    Equation 4.15 (tier 1).

    This function calculates the CO2 emissions from ferroalloy production.

    Argument
    --------
    mp (t/year): float
        Quantity of ferroalloy type produced.
    ef (t/t): float
        CO2 emission factor per ferroalloy type.

    Returns
    -------
    co2_ferroalloy (t/year): float
        CO2 emissions generated from ferroallay production.

    """
    co2_ferroalloy = mp * ef
    return co2_ferroalloy


def co2_ferroalloy_tier2_3_(
    co2_in_agent, co2_in_ore, co2_in_slag, co2_out_product, co2_out_non_product
):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production.

    Argument
    --------
    in_agent (t/year): float
        CO2 emissions for agent input.
    in_ore (t/year): float
        CO2 emissions for ore input.
    in_slag (t/year): float
        CO2 emissions for slag input.
    out_product (t/year): float
        CO2 emissions for prodcut output.
    out_non_product (t/year): float
        CO2 emissions for non-product output.

    Returns
    -------
    co2_ferroalloy (t/year): float
        CO2 emissions generated from ferroallay production.

    """
    co2_ferroalloy = (
        co2_in_agent + co2_in_ore + co2_in_slag - co2_out_product - co2_out_non_product
    )
    return co2_ferroalloy


def co2_in_agent_tier2_(m, ef):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production in reducing agents.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ef (t/t): float
        CO2 emissions factor for reducing agent.

    Returns
    -------
    co2_in_agent (t/year): float
        CO2 emissions for agent.

    """
    co2_in_agent = m * ef
    return co2_in_agent


def co2_in_ore(m, ccontent):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production in ores.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ccontent (t/t): float
        carbon content for ore.

    Returns
    -------
    co2_in_ore (t/year): float
        CO2 emissions for ore.

    """
    co2_in_ore = m * ccontent * 44 / 12
    return co2_in_ore


def co2_in_slag(m, ccontent):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production in slags.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ccontent (t/t): float
        carbon content for slag.

    Returns
    -------
    co2_in_slag (t/year): float
        CO2 emissions for slag.

    """
    co2_in_slag = m * ccontent * 44 / 12
    return co2_in_slag


def co2_out_product(m, ccontent):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production in product.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ccontent (t/t): float
        carbon content for slag.

    Returns
    -------
    co2_out_product (t/year): float
        CO2 emissions for product.

    """
    co2_out_product = m * ccontent * 44 / 12
    return co2_out_product


def co2_out_non_product(m, ccontent):
    """
    Equation 4.16 (tier 2).

    This function calculates the CO2 emissions from ferroalloy production in non-product outgoing stream.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ccontent (t/t): float
        carbon content for slag.

    Returns
    -------
    co2_out_non_product (t/year): float
        CO2 emissions for non-product outgoing stream.

    """
    co2_out_non_product = m * ccontent * 44 / 12
    return co2_out_non_product


def co2_in_agent_tier3_(m, ccontent):
    """
    Equation 4.17 (tier 3).

    This function calculates the CO2 emissions from ferroalloy production in reducing agents.

    Argument
    --------
    m (t/year): float
        mass of  reducing agent.
    ccontent (t/t): float
        C content factor for reducing agent.

    Returns
    -------
    co2_in_agent (t/year): float
        CO2 emissions for agent.

    """
    co2_in_agent = m * ccontent * 44 / 12
    return co2_in_agent


def ch4_ferroalloy_tier1_(mp, ef):
    """
    Equation 4.18 (tier 1).

    This function calculates the CH4 emissions from ferroalloy production.

    Argument
    --------
    mp (t/year): float
        mass of produced ferroalloy.
    ef (t/t): float
        CH4 emission factor.

    Returns
    -------
    ch4_ferroalloy (t/year): float
        CH4 emissions for ferroalloy production.

    """
    ch4_ferroalloy = mp * ef
    return ch4_ferroalloy


def ch4_ferroalloy_tier2_(mp, ef, furnace_operation_frac):
    """
    Equation 4.18 (tier2). Adopted since depended on furnace operation.

    This function calculates the CH4 emissions from ferroalloy production per furnace operation type.

    Argument
    --------
    mp (t/year): float
        mass of produced ferroalloy.
    ef (t/t): float
        CH4 emission factor.
    furnace_operation_frac (t/t):
        fraction of a specific furnace operation type

    Returns
    -------
    ch4_ferroalloy (t/year): float
        CH4 emissions for ferroalloy production.

    """
    ch4_ferroalloy = mp * ef * furnace_operation_frac
    return ch4_ferroalloy


def ccontent(f_fix_c, f_volatiles, c_v):
    """
    Equation 4.19 (tier3).

    This function calculates the carbon content of ferroalloy agent.

    Argument
    --------
    f_fix (t/t): float
        mass fraction of fix c in reducing agent.
    f_volatile (t/t): float
        mass fraction of volatiles in reducing agent.
    c_v (t/t):
        carbon content in volatiles.

    Returns
    -------
    ccontent (t/yr): float
        carbon content of ferroalloy.

    """
    ccontent = f_fix_c + (f_volatiles * c_v)
    return ccontent


def e_co2_tier1_(mp, ef):
    """
    Equation 4.20 (tier1).

    This function calculates the co2 emission of aluminium production.

    Argument
    --------
    mp (t/yr): float
        aluminium production.
    ef (t/t): float
        co2 emission factor.

    Returns
    -------
    e_co2 (t/t): float
        co2 of aluminium production.

    """
    e_co2 = mp * ef
    return e_co2


def e_co2_prebake(e_co2_anode, e_co2_pitch, e_co2_packing):
    """
    Equation 4.x (tier 2 and 3).

    This function calculates the co2 emission of aluminium production.
    Not explicitly as an equation in the guidelines, but required.

    Argument
    --------
    e_co2_anode (t/yr): float
        co2 emission from prebaked anode consumption.
    e_co2_pitch (t/yr): float
        co2 emission from pitch volatiles combustion.
    e_co2_packing (t/yr): float
        co2 emission from bake furnace packing material


    Returns
    -------
    e_co2 (t/yr): float
        co2 of aluminium production.

    """
    e_co2 = e_co2_anode + e_co2_pitch + e_co2_packing
    return e_co2


def e_co2_anode(nac, mp, s_a, ash_a):
    """
    Equation 4.21 (tier 2 and 3).

    This function calculates the co2 emission from prebaked anode consumption.

    Argument
    --------
    nac (t/t): float
        net prebaked anode consumption per tonne of aluminium.
    mp (t/yr): float
        total aluminium production.
    s_a (t/t): float
        sulphur content in baked anodes
    ash_a (t/t): float
        ash content in baked anodes

    Returns
    -------
    e_co2_anode (t/yr): float
        co2 from prebaked anode consumption.

    """
    e_co2_anode = nac * mp * (1 - s_a - ash_a) * 44 / 12
    return e_co2_anode


def e_co2_pitch(ga, h_w, ba, wt):
    """
    Equation 4.22 (tier 2 and 3).

    This function calculates the co2 emission from pitch volatiles combustion.

    Argument
    --------
    ga (t/yr): float
        initial weight of green anodes.
    h_w (t/t): float
        hydrogen content in green anodes.
    ba (t/yr): float
        baked anode production
    wt (t/t): float
        waste tar collected per anode as ratio

    Returns
    -------
    e_co2_pitch (t/yr): float
        co2 from pitch volatiles combustion.

    """
    e_co2_pitch = (ga - (h_w * ga) - ba - (wt * ga)) * 44 / 12
    return e_co2_pitch


def e_co2_packing(pcc, ba, s_pc, ash_pc):
    """
    Equation 4.23 (tier 2 and 3).

    This function calculates the co2 emission from bake furnace packing material.

    Argument
    --------
    pcc (t/t): float
        packing coke consumption.
    ba (t/yr): float
        baked anode production.
    s_pc (t/t): float
        sulphur content in packing coke
    ash_pc (t/t): float
        ash content in packing coke

    Returns
    -------
    e_co2_packing (t/yr): float
        co2 from bake furnace packing material.

    """
    e_co2_packing = pcc * ba * (1 - s_pc - ash_pc) * 44 / 12
    return e_co2_packing


def e_co2_soderberg(pc, mp, csm, bc, s_p, ash_p, h_p, s_c, ash_c, cd):
    """
    Equation 4.24 (tier 2 and 3).

    This function calculates the co2 emission from bake furnace packing material.

    Argument
    --------
    pc (t/t): float
        paste consumption per aluminium.
    csm (kg/t): float
        emissions of cyclohexane soluble matter, as kg per tonne aluminium.
    mp (t/yr): float
        total aluminium production
    bc (t/t): float
        binder content in paste (dry paste)
    s_p (t/t): float
        sulhur content in pitch
    ash_p (t/t): float
        ash content in pitch
    h_p (t/t): float
        hydrogen content in pitch
    s_c (t/t): float
        sulphur content in calcined coke
    ash_c (t/t): float
        ash content in calcined coke
    cd (t/t): float
        carbon in skimmed dust from soderberg cells

    Returns
    -------
    e_co2_soderberg (t/yr): float
        co2 emission from paste consumption (soderberg cells).

    """
    e_co2_soderberg = (
        (
            pc * mp
            - (csm * mp) / 1000
            - bc * pc * mp * (s_p + ash_p + h_p)
            - (1 - bc) * pc * mp * (s_c + ash_c)
            - mp * cd
        )
        * 44
        / 12
    )
    return e_co2_soderberg


def e_cf4_tier1_(ef, mp):
    """
    Equation 4.25 (tier 1).

    This function calculates the  emissions of cf4 from aluminium production.

    Argument
    --------
    ef (kg/t): float
        emission factor by technology type for cf4.
    mp (t/yr): float
        metal production by cell technology type.

    Returns
    -------
    e_cf4 (kg/yr): float
        emissions of cf4 from aluminium production.

    """
    e_cf4 = ef * mp
    return e_cf4


def e_c2f6_tier1_(ef, mp):
    """
    Equation 4.25 (tier 1).

    This function calculates the  emissions of c2f6 from aluminium production.

    Argument
    --------
    ef (kg/t): float
        emission factor by technology type for c2f6.
    mp (t/yr): float
        metal production by cell technology type.

    Returns
    -------
    e_c2f6 (kg/yr): float
        emissions of c2f6 from aluminium production.

    """
    e_c2f6 = ef * mp
    return e_c2f6


def e_cf4_tier2_3_(s_cf4, aem, mp):
    """
    Equation 4.26 (tier 2 and 3).

    This function calculates the  emissions of cf4 from aluminium production.

    Argument
    --------
    s_cf4 (kg/t / min/d): float
        slope coefficient for cf4.
    aem (min/d): float
        anode effect minutes per cell-day.
    mp (t/yr): float
        metal production by cell technology type.

    Returns
    -------
    e_cf4 (kg/yr): float
        emissions of cf4 from aluminium production.

    """
    e_cf4 = s_cf4 * aem * mp
    return e_cf4


def e_c2f6_tier2_3_(e_cf4, f):
    """
    Equation 4.26 (tier 2 and 3).

    This function calculates the  emissions of c2f6 from aluminium production.

    Argument
    --------
    e_cf4 (kg/yr): float
        emission of CF4 from aluminium production.
    f (kg/kg): float
        weight fraction of c2f6 per cf4.

    Returns
    -------
    e_c2f6 (kg/yr): float
        emissions of c2f6 from aluminium production.

    """
    e_c2f6 = e_cf4 * f
    return e_c2f6


def e_co2_magnesium(p, ef):
    """
    Equation 4.28, 4.29 (tier 1, 2).

    This function calculates the co2 emissions from primary magnesium production.

    Argument
    --------
    p (t/yr): float
        primary magnesium production by resource type .
    ef (t/t): float
        co2 emission factor.

    Returns
    -------
    e_co2_magnesium (Gg/yr): float
        co2 emissions from primary aluminium production.

    """
    e_co2_magnesium = p * ef * 0.001
    return e_co2_magnesium


def e_sf6_magnesium(mg_c, ef):
    """
    Equation 4.30 (tier 1).

    This function calculates the SF6 emissions from primary magnesium production.

    Argument
    --------
    mg_c (t/yr): float
        amount of magnesium casting.
    ef (kg/t): float
        SF6 emission factor.

    Returns
    -------
    e_sf6_magnesium (Gg/yr): float
        SF6 from primary aluminium production.

    """
    e_co2_magnesium = mg_c * ef * 0.001
    return e_co2_magnesium


def e_co2_lead(q, ef):
    """
    Equation 4.32 (tier 1). Revised.

    This function calculates the CO2 emissions from lead production.

    Argument
    --------
    q (t/yr): float
        amount of lead produced by process type.
    ef (kg/t): float
        CO2 emission factor for process type.

    Returns
    -------
    e_co2_lead (Gg/yr): float
        CO2 from lead production.

    """
    e_co2_lead = q * ef
    return e_co2_lead


def e_co2_zinc(q, ef):
    """
    Equation 4.33, 4.34 (tier 1). Revised.

    This function calculates the CO2 emissions from zinc production.

    Argument
    --------
    q (t/yr): float
        amount of zinc produced by process type.
    ef (kg/t): float
        CO2 emission factor for process type.

    Returns
    -------
    e_co2_lead (Gg/yr): float
        CO2 from zinc production.

    """
    e_co2_zinc = q * ef
    return e_co2_zinc
