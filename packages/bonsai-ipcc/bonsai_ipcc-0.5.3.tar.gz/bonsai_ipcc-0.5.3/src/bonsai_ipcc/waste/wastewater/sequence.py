"""
Sequences to determine GHG emissions from wastewater.

Decision tree for CH4 (domestic wastewater):
    - tier 1: wastewater is not a key category (treatment),
              no activity data available to categorize discharge by type of waterbody (discharge)
    - tier 2: country-specific emission factors availablle for pathways (treatment),
              no country-specific method available to categorize discharge by type of waterbody (discharge)
    - tier 3: country-specific method for facility-specific CH4 emissions available (treatment),
              country-specific method available to categorize discharge by type of waterbody (discharge)

Decision tree for CH4 (industrial wastewater):
    - tier 1: wastewater is not a key category (treatment),
              wastewater is not a key category and no activity data to categoorize by type of waterbody (discharge)
    - tier 2: wastewater outflow data for industrial sectors available (treatment),
              wastewater is not a key category and activity data to categoorize by type of waterbody (discharge)
    - tier 3: country-specific method for individual facilities and sectors available (treatment and discharge)

Decision tree for N2O (domestic wastewater):
    - tier 1: wastewater is not a key category (treatment),
              no activity data available to categorize discharge by type of waterbody (discharge)
    - tier 2: country-specific emission factors availablle for pathways (treatment)
    - tier 3: country-specific method for facility-specific N2O emissions available (treatment),
              country-specific method available to categorize discharge by type of waterbody (discharge)

Decision tree for N2O (industrial wastewater):
    - tier 1: wastewater is not a key category (treatment),
              no activity data or country-specific method available to categorize by type of waterbody (discharge)
    - tier 2: N and wastewater outflow data for industrial sectors available (treatment),
    - tier 3: country-specific method for individual facilities and sectors available (treatment)
              country-specific method available to categorice by type of waterbody and (discharge)
"""

import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_ch4_domestic(
    year=2010,
    region="BG",
    activity="septic-tank",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions for domestic wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Wastewater sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = "ww_domestic"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="total_population", table="total_population", coords=[year, region]
    )

    seq.read_parameter(name="bod", table="bod", coords=[year, region])

    value = seq.elementary.ww_domestic(
        p=seq.step.total_population.value, bod=seq.step.bod.value
    )

    seq.store_result(name="ww_domestic", value=value, unit="kg/yr", year=year)

    seq.read_parameter(
        name="ww_per_tech_dom", table="ww_per_tech_dom", coords=[year, region, activity]
    )
    value = seq.elementary.ww_tech(
        ww=seq.step.ww_domestic.value, ww_per_tech=seq.step.ww_per_tech_dom.value
    )

    seq.store_result(
        name="ww_tech",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="use|waste|ww_domestic",
    )

    seq.read_parameter(
        name="i",
        table="i",
        coords=[region, activity],
    )

    # loop over all population types
    l = seq.get_dimension_levels(year, region, uncert=uncertainty, table="u")
    value = 0.0
    for population_type in l:
        seq.read_parameter(
            name=f"u_xxx_{population_type}_xxx",
            table="u",
            coords=[year, region, population_type],
        )

        seq.read_parameter(
            name=f"t_xxx_{population_type}_xxx",
            table="t",
            coords=[year, region, population_type, activity],
        )

        value += seq.elementary.tow_system(
            tow=seq.step.ww_tech.value,
            u=getattr(getattr(seq.step, f"u_xxx_{population_type}_xxx"), "value"),
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            i=seq.step.i.value,
        )

    seq.store_result(
        name="tow_system",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="tow_rem", table="tow_rem", coords=[year, region, activity])

    # loop over all population types
    l = seq.get_dimension_levels(year, region, uncert=uncertainty, table="u")
    value = 0.0
    for population_type in l:

        value += seq.elementary.tow_eff_treat_system(
            tow=seq.step.tow_system.value,
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            tow_rem=seq.step.tow_rem.value,
        )

    seq.store_result(
        name="tow_eff_treat_system",
        value=value,
        unit="kg/yr",
        year=year,
    )

    if "_aerob" in activity:
        seq.read_parameter(
            name="s_mass", table="s_mass", coords=[year, region, activity]
        )
        seq.read_parameter(name="k_rem", table="k_rem", coords=[year, region, activity])
        value = seq.elementary.s_aerob(
            s_mass=seq.step.s_mass.value, k_rem=seq.step.k_rem.value
        )
        seq.store_result(
            name="s_aerob",
            value=value,
            unit="kg/yr",
            year=year,
        )

    if "septic" in activity:
        seq.read_parameter(name="f_ww", table="f_ww", coords=[year, region])
        value = seq.elementary.s_septic(
            tow_septic=seq.step.tow_eff_treat_system.value, f=seq.step.f_ww.value
        )
        seq.store_result(
            name="s_septic",
            value=value,
            unit="kg/yr",
            year=year,
        )

    seq.read_parameter(name="b0_bod", table="b0_bod", coords=[year, region])

    # wastewater treatment type
    seq.read_parameter(
        name="mcf_wwatertreat",
        table="mcf_wwatertreat",
        coords=[year, region, activity],
    )

    value = seq.elementary.ef_ch4_treat(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwatertreat.value
    )

    seq.store_result(
        name="ef_ch4_treat",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge type
    seq.read_parameter(
        name="mcf_wwaterdischarge",
        table="mcf_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.ef_ch4_discharge(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwaterdischarge.value
    )

    seq.store_result(
        name="ef_ch4_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="r_ww_dom",
        table="r_ww_dom",
        coords=[year, region, activity],
        lci_flag="supply|by-product|methane",
    )

    if "_aerob" in activity:
        # wastewater treatmant
        value = seq.elementary.ch4_emissions_treatment(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_aerob.value,
            ef=seq.step.ef_ch4_treat.value,
            r=seq.step.r_ww_dom.value,
        )
        seq.store_result(
            name="ch4_emissions_treatment",
            value=value,
            unit="kg/yr",
            year=year,
        )

        # wastewater discharge
        value = seq.elementary.ch4_emissions_discharge(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_aerob.value,
            ef=seq.step.ef_ch4_discharge.value,
            r=seq.step.r_ww_dom.value,
        )
    if "septic" in activity:
        # wastewater treatmant
        value = seq.elementary.ch4_emissions_treatment(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_septic.value,
            ef=seq.step.ef_ch4_treat.value,
            r=seq.step.r_ww_dom.value,
        )

        seq.store_result(
            name="ch4_emissions_treatment",
            value=value,
            unit="kg/yr",
            year=year,
        )

        # wastewater discharge
        value = seq.elementary.ch4_emissions_discharge(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_septic.value,
            ef=seq.step.ef_ch4_discharge.value,
            r=seq.step.r_ww_dom.value,
        )

    seq.store_result(
        name="ch4_emissions_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.ch4_emissions(
        seq.step.ch4_emissions_treatment.value, seq.step.ch4_emissions_discharge.value
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    # 5. STEP: 4.1
    # emissions from anaerob digestion of sludge from wastewater treatment
    # considerred in biological

    logger.info("---> wastewater sequence finalized.")
    return seq.step


def tier1_ch4_industrial(
    year=2010,
    region="BG",
    product="ww_pulp",
    activity="coll_treat_aerob_centralised_industry",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions for industrial wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        industry in which wastewater treatment occurs
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    seq.read_parameter(name="p", table="p", coords=[year, region, product])

    seq.read_parameter(name="w", table="w", coords=[year, region, product])

    seq.read_parameter(name="cod", table="cod", coords=[year, region, product])

    value = seq.elementary.ww_industrial(
        p=seq.step.p.value, w=seq.step.w.value, cod=seq.step.cod.value
    )

    seq.store_result(name="ww_industrial", value=value, unit="kg/yr", year=year)

    seq.read_parameter(
        name="ww_per_tech_ind",
        table="ww_per_tech_ind",
        coords=[year, region, activity, product],
    )
    value = seq.elementary.ww_tech(
        ww=seq.step.ww_industrial.value, ww_per_tech=seq.step.ww_per_tech_ind.value
    )

    seq.store_result(
        name="ww_tech",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(name="b0_cod", table="b0_cod", coords=[year, region])

    seq.read_parameter(
        name="mcf", table="mcf_wwatertreat", coords=[year, region, activity]
    )

    value = seq.elementary.ef_ch4_ind(b0=seq.step.b0_cod.value, mcf=seq.step.mcf.value)
    seq.store_result(
        name="ef_ch4_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="s_ww", table="s_ww", coords=[year, region, product])

    seq.read_parameter(
        name="r_ww_ind",
        table="r_ww_ind",
        coords=[year, region, activity, product],
        lci_flag="supply|by-product|methane",
    )

    value = seq.elementary.ch4_emissions_system_ind(
        tow=seq.step.ww_tech.value,
        s=seq.step.s_ww.value,
        ef=seq.step.ef_ch4_ind.value,
        r=seq.step.r_ww_ind.value,
    )

    seq.store_result(
        name="ch4_emissions_system_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge type
    seq.read_parameter(
        name="mcf_wwaterdischarge",
        table="mcf_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    seq.read_parameter(name="b0_bod", table="b0_bod", coords=[year, region])

    value = seq.elementary.ef_ch4_discharge(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwaterdischarge.value
    )

    seq.store_result(
        name="ef_ch4_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge
    value = seq.elementary.ch4_emissions_discharge(
        tow=seq.step.ww_tech.value,
        s=seq.step.s_ww.value,
        ef=seq.step.ef_ch4_discharge.value,
        r=seq.step.r_ww_ind.value,
    )

    seq.store_result(
        name="ch4_emissions_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.ch4_emissions(
        seq.step.ch4_emissions_system_ind.value, seq.step.ch4_emissions_discharge.value
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> wastewater sequence finalized.")
    return seq.step


def tier1_n2o_domestic(
    year=2010,
    region="DE",
    activity="uncoll_untreated",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    N2O Emissions for domestic wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = "ww_domestic"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="protein_supply", table="protein_supply", coords=[year, region]
    )

    seq.read_parameter(name="fpc", table="fpc", coords=[year, region])

    value = seq.elementary.protein(
        protein_supply=seq.step.protein_supply.value, fpc=seq.step.fpc.value
    )
    seq.store_result(
        name="protein",
        value=value,
        unit="kg/cap/yr",
        year=year,
    )

    seq.read_parameter(
        name="p_treatment", table="p_treatment", coords=[year, region, activity]
    )

    seq.read_parameter(name="f_npr", table="f_npr", coords=[year, region])

    seq.read_parameter(name="n_hh", table="n_hh", coords=[year, region])

    seq.read_parameter(name="f_non_con", table="f_non_con", coords=[year, region])

    seq.read_parameter(
        name="f_ind_com", table="f_ind_com", coords=[year, region, activity]
    )

    value = seq.elementary.tn_domestic(
        p_treatment=seq.step.p_treatment.value,
        protein=seq.step.protein.value,
        f_npr=seq.step.f_npr.value,
        n_hh=seq.step.n_hh.value,
        f_non_con=seq.step.f_non_con.value,
        f_ind_com=seq.step.f_ind_com.value,
    )
    seq.store_result(
        name="tn_domestic",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="n_rem", table="n_rem", coords=[year, region, activity])
    # loop over all population types
    l = seq.get_dimension_levels(year, region, uncert=uncertainty, table="u")
    value = 0.0
    for population_type in l:

        seq.read_parameter(
            name=f"t_xxx_{population_type}_xxx",
            table="t",
            coords=[year, region, population_type, activity],
        )

        value += seq.elementary.n_effluent_dom_system(
            tn_dom=seq.step.tn_domestic.value,
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            n_rem=seq.step.n_rem.value,
        )
    seq.store_result(
        name="n_effluent_dom_system",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwatertreat",
        table="ef_n2o_wwatertreat",
        coords=[year, region, activity],
    )
    value = 0.0
    for population_type in l:

        seq.read_parameter(
            name=f"u_xxx_{population_type}_xxx",
            table="u",
            coords=[year, region, population_type],
        )
        value += seq.elementary.n2o_plants(
            u=getattr(getattr(seq.step, f"u_xxx_{population_type}_xxx"), "value"),
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            ef=seq.step.ef_n2o_wwatertreat.value,
            tn_dom=seq.step.tn_domestic.value,
        )

    seq.store_result(
        name="n2o_plants",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwaterdischarge",
        table="ef_n2o_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.n2o_effluent(
        n_effluent=seq.step.n_effluent_dom_system.value,
        ef_effluent=seq.step.ef_n2o_wwaterdischarge.value,
    )
    seq.store_result(
        name="n2o_effluent",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.n2o_emissions(
        seq.step.n2o_plants.value, seq.step.n2o_effluent.value
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> wastewater sequence finalized.")
    return seq.step


def tier1_n2o_industrial(
    year=2010,
    region="BG",
    activity="uncoll_untreated",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    product="ww_meat",
    uncertainty="def",
):
    """Template calculation sequence for tier 1 method.

    N2O Emissions for industrial wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    product : str
        industry in which wastewater treatment occurs
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(name="p", table="p", coords=[year, region, product])

    seq.read_parameter(name="w", table="w", coords=[year, region, product])

    seq.read_parameter(name="tn", table="tn", coords=[year, region, product])

    value = seq.elementary.tn_industry(
        p=seq.step.p.value, w=seq.step.w.value, tn=seq.step.tn.value
    )
    seq.store_result(
        name="tn_industry",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(
        name="t_ind",
        table="t_ind",
        coords=[year, region, activity, product],
    )

    seq.read_parameter(
        name="ef", table="ef_n2o_wwatertreat", coords=[year, region, activity]
    )

    value = seq.elementary.n2o_plants_ind(
        t_ind=seq.step.t_ind.value,
        ef=seq.step.ef.value,
        tn_ind=seq.step.tn_industry.value,
    )
    seq.store_result(
        name="n2o_plants_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="n_rem", table="n_rem", coords=[year, region, activity])

    value = seq.elementary.n_effluent_ind(
        tn_ind=seq.step.tn.value, t_ind=seq.step.t_ind.value, n_rem=seq.step.n_rem.value
    )
    seq.store_result(
        name="n_effluent_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwaterdischarge",
        table="ef_n2o_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.n2o_effluent_ind(
        n_effluent_ind=seq.step.n_effluent_ind.value,
        ef_effluent=seq.step.ef_n2o_wwaterdischarge.value,
    )
    seq.store_result(
        name="n2o_effluent_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.n2o_emissions(
        seq.step.n2o_plants_ind.value, seq.step.n2o_effluent_ind.value
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> wastewater sequence finalized.")
    return seq.step


def tier2_ch4_domestic(
    year=2010,
    region="BG",
    activity="septic-tank",
    wwaterdischarge_type="freshwater_aquatic_other_tier2",
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    CH4 Emissions for domestic wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = "ww_domestic"
    seq.store_signature(meta_dict)

    logger.info("Tier 2 sequence requires country-specific data for parameters.")
    seq.read_parameter(
        name="tow_per_tech_dom",
        table="tow_per_tech_dom",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="t_per_tech", table="t_per_tech", coords=[year, region, activity]
    )

    seq.read_parameter(name="tow_rem", table="tow_rem", coords=[year, region, activity])

    value = seq.elementary.tow_eff_treat_system(
        tow=seq.step.tow_per_tech_dom.value,
        t=seq.step.t_per_tech.value,
        tow_rem=seq.step.tow_rem.value,
    )

    seq.store_result(
        name="tow_eff_treat_system",
        value=value,
        unit="kg/yr",
        year=year,
    )

    if "_aerob" in activity:
        seq.read_parameter(
            name="s_mass", table="s_mass", coords=[year, region, activity]
        )
        seq.read_parameter(name="k_rem", table="k_rem", coords=[year, region, activity])
        value = seq.elementary.s_aerob(
            s_mass=seq.step.s_mass.value, k_rem=seq.step.k_rem.value
        )
        seq.store_result(
            name="s_aerob",
            value=value,
            unit="kg/yr",
            year=year,
        )

    if "septic" in activity:
        seq.read_parameter(name="f_ww", table="f_ww", coords=[year, region])
        value = seq.elementary.s_septic(
            tow_septic=seq.step.tow_eff_treat_system.value, f=seq.step.f_ww.value
        )
        seq.store_result(
            name="s_septic",
            value=value,
            unit="kg/yr",
            year=year,
        )

    seq.read_parameter(name="b0_bod", table="b0_bod", coords=[year, region])

    # wastewater treatment type
    seq.read_parameter(
        name="mcf_wwatertreat",
        table="mcf_wwatertreat",
        coords=[year, region, activity],
    )

    value = seq.elementary.ef_ch4_treat(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwatertreat.value
    )

    seq.store_result(
        name="ef_ch4_treat",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge type
    seq.read_parameter(
        name="mcf_wwaterdischarge",
        table="mcf_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.ef_ch4_discharge(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwaterdischarge.value
    )

    seq.store_result(
        name="ef_ch4_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="r_ww_dom",
        table="r_ww_dom",
        coords=[year, region, activity],
        lci_flag="supply|by-product|methane",
    )

    if "_aerob" in activity:
        # wastewater treatmant
        value = seq.elementary.ch4_emissions_treatment(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_aerob.value,
            ef=seq.step.ef_ch4_treat.value,
            r=seq.step.r_ww_dom.value,
        )
        seq.store_result(
            name="ch4_emissions_treatment",
            value=value,
            unit="kg/yr",
            year=year,
        )

        # wastewater discharge
        value = seq.elementary.ch4_emissions_discharge(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_aerob.value,
            ef=seq.step.ef_ch4_discharge.value,
            r=seq.step.r_ww_dom.value,
        )
    if "septic" in activity:
        # wastewater treatmant
        value = seq.elementary.ch4_emissions_treatment(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_septic.value,
            ef=seq.step.ef_ch4_treat.value,
            r=seq.step.r_ww_dom.value,
        )

        seq.store_result(
            name="ch4_emissions_treatment",
            value=value,
            unit="kg/yr",
            year=year,
        )

        # wastewater discharge
        value = seq.elementary.ch4_emissions_discharge(
            tow=seq.step.tow_eff_treat_system.value,
            s=seq.step.s_septic.value,
            ef=seq.step.ef_ch4_discharge.value,
            r=seq.step.r_ww_dom.value,
        )

    seq.store_result(
        name="ch4_emissions_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.ch4_emissions(
        seq.step.ch4_emissions_treatment.value, seq.step.ch4_emissions_discharge.value
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Wastewater sequence finalized.")
    return seq.step


def tier2_ch4_industrial(
    year=2010,
    region="BG",
    product="pulp",
    activity="coll_treat_aerob_centralised_industry",
    wwaterdischarge_type="freshwater_aquatic_other_tier2",
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    CH4 Emissions for industrial wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        industry in which wastewater treatment occurs
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="tow",
        table="tow_per_tech_ind",
        coords=[year, region, activity, product],
        lci_flag=f"use|waste|{product}",
    )

    logger.info(
        "for tier 2 method parameter 'b0_cod' needs to include country-specific values."
    )
    seq.read_parameter(name="b0_cod", table="b0_cod", coords=[year, region])

    logger.info(
        "for tier 2 method parameter 'mcf_wwatertreat' needs to include country-specific values."
    )
    seq.read_parameter(
        name="mcf", table="mcf_wwatertreat", coords=[year, region, activity]
    )

    value = seq.elementary.ef_ch4_ind(b0=seq.step.b0_cod.value, mcf=seq.step.mcf.value)
    seq.store_result(
        name="ef_ch4_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="s_ww", table="s_ww", coords=[year, region, product])

    seq.read_parameter(
        name="r_ww_ind",
        table="r_ww_ind",
        coords=[year, region, activity],
        lci_flag="supply|by-product|methane",
    )

    value = seq.elementary.ch4_emissions_system_ind(
        tow=seq.step.tow.value,
        s=seq.step.s_ww.value,
        ef=seq.step.ef_ch4_ind.value,
        r=seq.step.r_ww_ind.value,
    )

    seq.store_result(
        name="ch4_emissions_system_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge type
    seq.read_parameter(
        name="mcf_wwaterdischarge",
        table="mcf_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.ef_ch4_discharge(
        b0=seq.step.b0_bod.value, mcf=seq.step.mcf_wwaterdischarge.value
    )

    seq.store_result(
        name="ef_ch4_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # wastewater discharge
    value = seq.elementary.ch4_emissions_discharge(
        tow=seq.step.tow_efftreat.value,
        s=seq.step.s.value,
        ef=seq.step.ef_ch4_discharge.value,
        r=seq.step.r_ww_ind.value,
    )

    seq.store_result(
        name="ch4_emissions_discharge",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.ch4_emissions(
        seq.step.ch4_emissions_system_ind.value, seq.step.ch4_emissions_discharge.value
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Wastewater sequence finalized.")
    return seq.step


def tier2_n2o_domestic(
    year=2010,
    region="DE",
    activity="uncoll_untreated",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    N2O Emissions for domestic wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("wastewater sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = "ww_domestic"
    seq.store_signature(meta_dict)

    logger.info("Tier 2 sequence requires country-specific data for parameters.")
    seq.read_parameter(
        name="protein_supply", table="protein_supply", coords=[year, region]
    )

    seq.read_parameter(name="fpc", table="fpc", coords=[year, region])

    value = seq.elementary.protein(
        protein_supply=seq.step.protein_supply.value, fpc=seq.step.fpc.value
    )
    seq.store_result(
        name="protein",
        value=value,
        unit="kg/cap/yr",
        year=year,
    )

    seq.read_parameter(
        name="p_treatment", table="p_treatment", coords=[year, region, activity]
    )

    seq.read_parameter(name="f_npr", table="f_npr", coords=[year, region])

    seq.read_parameter(name="n_hh", table="n_hh", coords=[year, region])

    seq.read_parameter(name="f_non_con", table="f_non_con", coords=[year, region])

    seq.read_parameter(
        name="f_ind_com", table="f_ind_com", coords=[year, region, activity]
    )

    value = seq.elementary.tn_domestic(
        p_treatment=seq.step.p_treatment.value,
        protein=seq.step.protein.value,
        f_npr=seq.step.f_npr.value,
        n_hh=seq.step.n_hh.value,
        f_non_con=seq.step.f_non_con.value,
        f_ind_com=seq.step.f_ind_com.value,
    )
    seq.store_result(
        name="tn_domestic",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="n_rem", table="n_rem", coords=[year, region, activity])
    # loop over all population types
    l = seq.get_dimension_levels(year, region, uncert=uncertainty, table="u")
    value = 0.0
    for population_type in l:

        seq.read_parameter(
            name=f"t_xxx_{population_type}_xxx",
            table="t",
            coords=[year, region, population_type, activity],
        )

        value += seq.elementary.n_effluent_dom_system(
            tn_dom=seq.step.tn_domestic.value,
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            n_rem=seq.step.n_rem.value,
        )
    seq.store_result(
        name="n_effluent_dom_system",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwatertreat",
        table="ef_n2o_wwatertreat",
        coords=[year, region, activity],
    )
    value = 0.0
    for population_type in l:

        seq.read_parameter(
            name=f"u_xxx_{population_type}_xxx",
            table="u",
            coords=[year, region, population_type],
        )
        value += seq.elementary.n2o_plants(
            u=getattr(getattr(seq.step, f"u_xxx_{population_type}_xxx"), "value"),
            t=getattr(getattr(seq.step, f"t_xxx_{population_type}_xxx"), "value"),
            ef=seq.step.ef_n2o_wwatertreat.value,
            tn_dom=seq.step.tn_domestic.value,
        )

    seq.store_result(
        name="n2o_plants",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwaterdischarge",
        table="ef_n2o_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.n2o_effluent(
        n_effluent=seq.step.n_effluent_dom_system.value,
        ef_effluent=seq.step.ef_n2o_wwaterdischarge.value,
    )
    seq.store_result(
        name="n2o_effluent",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.n2o_emissions(
        seq.step.n2o_plants.value, seq.step.n2o_effluent.value
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> wastewater sequence finalized.")
    return seq.step


def tier2_n2o_industrial(
    year=2010,
    region="BG",
    activity="uncoll_untreated",
    wwaterdischarge_type="freshwater_aquatic_tier1",
    product="ww_meat",
    uncertainty="def",
):
    """Template calculation sequence for tier 2 method.

    N2O Emissions for industrial wastewater treatment.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    activity : str
        wastewater treatment technology
    wwaterdischarge_type : str
        wastewater discharge type
    product : str
        industry in which wastewater treatment occurs
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Wastewater sequence started --->")
    seq.store_signature(locals())

    logger.info("Tier 2 sequence requires country-specific data for parameters.")
    seq.read_parameter(name="p", table="p", coords=[year, region, product])

    seq.read_parameter(name="w", table="w", coords=[year, region, product])

    seq.read_parameter(name="tn", table="tn", coords=[year, region, product])

    value = seq.elementary.tn_industry(
        p=seq.step.p.value, w=seq.step.w.value, tn=seq.step.tn.value
    )
    seq.store_result(
        name="tn_industry",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(
        name="t_ind",
        table="t_ind",
        coords=[year, region, activity, product],
    )

    seq.read_parameter(
        name="ef", table="ef_n2o_wwatertreat", coords=[year, region, activity]
    )

    value = seq.elementary.n2o_plants_ind(
        t_ind=seq.step.t_ind.value,
        ef=seq.step.ef.value,
        tn_ind=seq.step.tn_industry.value,
    )
    seq.store_result(
        name="n2o_plants_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(name="n_rem", table="n_rem", coords=[year, region, activity])

    value = seq.elementary.n_effluent_ind(
        tn_ind=seq.step.tn.value, t_ind=seq.step.t_ind.value, n_rem=seq.step.n_rem.value
    )
    seq.store_result(
        name="n_effluent_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    seq.read_parameter(
        name="ef_n2o_wwaterdischarge",
        table="ef_n2o_wwaterdischarge",
        coords=[year, region, wwaterdischarge_type],
    )

    value = seq.elementary.n2o_effluent_ind(
        n_effluent_ind=seq.step.n_effluent_ind.value,
        ef_effluent=seq.step.ef_n2o_wwaterdischarge.value,
    )
    seq.store_result(
        name="n2o_effluent_ind",
        value=value,
        unit="kg/yr",
        year=year,
    )

    # total
    value = seq.elementary.n2o_emissions(
        seq.step.n2o_plants_ind.value, seq.step.n2o_effluent_ind.value
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> Wastewater sequence finalized.")
    return seq.step
