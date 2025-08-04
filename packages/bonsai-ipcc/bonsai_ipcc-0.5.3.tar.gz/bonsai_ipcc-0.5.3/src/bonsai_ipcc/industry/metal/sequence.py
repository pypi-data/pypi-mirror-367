import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1a_co2_coke(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1a method.

    CO2 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "coke"
    seq.store_signature(meta_dict)

    #'cao_in_clinker, ckd_correc_fact'
    seq.read_parameter(
        name="ck",
        table="ck",
        coords=[year, region, activity],
        lci_flag="supply|product|coke",
    )

    seq.read_parameter(
        name="ef_co2_coke", table="ef_co2_coke", coords=[year, region, activity]
    )

    value = seq.elementary.co2_coke_tier1a_(
        ck=seq.step.ck.value, ef_co2=seq.step.ef_co2_coke.value
    )

    seq.store_result(
        name="co2_coke_tier1a_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1a_ch4_coke(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1a method.

    CH4 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "coke"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="ck",
        table="ck",
        coords=[year, region, activity],
        lci_flag="supply|product|coke",
    )

    seq.read_parameter(
        name="ef_ch4_v3c4", table="ef_ch4_v3c4", coords=[year, region, activity]
    )

    value = seq.elementary.ch4_coke(
        ck=seq.step.ck.value, ef_ch4=seq.step.ef_ch4_v3c4.value
    )

    seq.store_result(
        name="ch4_emission",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1b_co2_coke(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 1b method.

    CO2 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "coke"
    seq.store_signature(meta_dict)

    #'cao_in_clinker, ckd_correc_fact'
    seq.read_parameter(
        name="ck",
        table="ck",
        coords=[year, region, activity],
        lci_flag="supply|product|coke",
    )

    seq.read_parameter(name="c_ck", table="c_ck", coords=[year, region])

    seq.read_parameter(name="cc", table="cc", coords=[year, region, activity])

    seq.read_parameter(name="c_cc", table="c_cc", coords=[year, region])

    value = seq.elementary.co2_coke_tier1b_(
        ck=seq.step.ck.value,
        cc=seq.step.cc.value,
        c_ck=seq.step.ck.value,
        c_cc=seq.step.cc.value,
    )

    seq.store_result(
        name="co2_coke_tier1b_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_co2_coke(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "coke"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cc",
        table="cc",
        coords=[year, region, activity],
        lci_flag="use|product|coking_coal",
    )
    seq.read_parameter(
        name="c_cc",
        table="c_cc",
        coords=[year, region],
    )
    seq.read_parameter(name="bg", table="bg", coords=[year, region, activity])
    seq.read_parameter(
        name="c_bg",
        table="c_bg",
        coords=[year, region],
    )

    seq.read_parameter(name="co", table="co", coords=[year, region, activity])
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    seq.read_parameter(name="cog", table="cog", coords=[year, region, activity])
    seq.read_parameter(
        name="c_cog",
        table="c_cog",
        coords=[year, region],
    )
    seq.read_parameter(
        name="e_flaring", table="e_flaring", coords=[year, region, activity]
    )

    # loop over all by-products
    d = seq.get_dimension_levels(year, region, activity, uncert="def", table="cob_b")
    value = 0.0
    for byproduct_type in d:

        seq.read_parameter(
            name=f"cob_b_xxx_{byproduct_type}_xxx",
            table="cob_b",
            coords=[year, region, activity, byproduct_type],
            lci_flag=f"supply|by-product|{byproduct_type}",
        )

        seq.read_parameter(
            name=f"c_b_xxx_{byproduct_type}_xxx",
            table="c_b",
            coords=[year, region, byproduct_type],
        )
        value += seq.elementary.c_cob(
            cob_b=getattr(
                getattr(seq.step, f"cob_b_xxx_{byproduct_type}_xxx"), "value"
            ),
            c_b=getattr(getattr(seq.step, f"c_b_xxx_{byproduct_type}_xxx"), "value"),
        )

    seq.store_result(name="c_cob", value=value, unit="t/yr")

    # loop (sum over all process materials)
    d = seq.get_dimension_levels(year, region, activity, uncert="def", table="pm_a")
    value = 0.0
    for material_type in d:

        seq.read_parameter(
            name=f"pm_a_xxx_{material_type}_xxx",
            table="pm_a",
            coords=[year, region, activity, material_type],
            lci_flag=f"use|product|{material_type}",
        )

        seq.read_parameter(
            name=f"c_a_{material_type}_xxx",
            table="c_a",
            coords=[year, region, material_type],
        )

        value += seq.elementary.c_pm(
            pm_a=getattr(getattr(seq.step, f"pm_a_xxx_{material_type}_xxx"), "value"),
            c_a=getattr(getattr(seq.step, f"c_a_xxx_{material_type}_xxx"), "value"),
        )
    seq.store_result(name="c_pm", value=value, unit="t/yr")

    value = seq.elementary.co2_coke_tier2_(
        cc=seq.step.cc.value,
        c_cc=seq.step.c_cc.value,
        c_pm=seq.step.c_pm.value,
        bg=seq.step.bg.value,
        c_bg=seq.step.c_bg.value,
        co=seq.step.c_bg.value,
        c_co=seq.step.c_co.value,
        cog=seq.step.cog.value,
        c_cog=seq.step.c_cog.value,
        c_cob=seq.step.c_cob.value,
        e_flaring=seq.step.e_flaring.value,
    )
    seq.store_result(name="co2_coke_tier2_", value=value, unit="t/yr", year=year)
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier3_co2_coke(
    year=2019,
    region="a specific plant",
    activity="by-product_recovery",
    uncertainty="def",
):
    """Template calculation sequence for tier 3 method. Plant-specific carbon content for materials and by-products required.

    CO2 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "coke"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cc",
        table="cc",
        coords=[year, region, activity],
        lci_flag="use|product|coking_coal",
    )
    seq.read_parameter(
        name="c_cc",
        table="c_cc",
        coords=[year, region],
    )
    seq.read_parameter(name="bg", table="bg", coords=[year, region, activity])
    seq.read_parameter(
        name="c_bg",
        table="c_bg",
        coords=[year, region],
    )

    seq.read_parameter(name="co", table="co", coords=[year, region, activity])
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    seq.read_parameter(name="cog", table="cog", coords=[year, region, activity])
    seq.read_parameter(
        name="c_cog",
        table="c_cog",
        coords=[year, region],
    )
    seq.read_parameter(
        name="e_flaring", table="e_flaring", coords=[year, region, activity]
    )

    # loop (sum over all process materials)
    d = seq.get_dimension_levels(year, region, activity, uncert="def", table="pm_a")
    d1 = seq.get_dimension_levels(year, region, activity, uncert="def", table="cob_b")
    value = 0.0
    for material_type in d:
        for byproduct_type in d1:

            seq.read_parameter(
                name=f"pm_a_xxx_{material_type}_{byproduct_type}_xxx",
                table="pm_a",
                coords=[year, region, activity, material_type],
                lci_flag=f"use|product|{material_type}",
            )

            seq.read_parameter(
                name=f"c_a_xxx_{material_type}_{byproduct_type}_xxx",
                table="c_a",
                coords=[year, region, material_type],
            )

            seq.read_parameter(
                name=f"cob_b_xxx_{material_type}_{byproduct_type}_xxx",
                table="cob_b",
                coords=[year, region, activity, byproduct_type],
                lci_flag=f"supply|by-product|{byproduct_type}",
            )

            seq.read_parameter(
                name=f"c_b_xxx_{material_type}_{byproduct_type}_xxx",
                table="c_b",
                coords=[year, region, byproduct_type],
            )

            value += seq.elementary.co2_coke_tier2_(
                cc=seq.step.cc.value,
                c_cc=seq.step.c_cc.value,
                pm_a=getattr(
                    getattr(seq.step, f"pm_a_xxx_{material_type}_{byproduct_type}_xxx"),
                    "value",
                ),
                c_a=getattr(
                    getattr(seq.step, f"c_a_xxx_{material_type}_{byproduct_type}_xxx"),
                    "value",
                ),
                bg=seq.step.bg.value,
                c_bg=seq.step.c_bg.value,
                co=seq.step.co.value,
                c_co=seq.step.c_co.value,
                cog=seq.step.cog.value,
                c_cog=seq.step.c_cog.value,
                cob_b=getattr(
                    getattr(
                        seq.step, f"cob_b_xxx_{material_type}_{byproduct_type}_xxx"
                    ),
                    "value",
                ),
                c_b=getattr(
                    getattr(seq.step, f"c_b_xxx_{material_type}_{byproduct_type}_xxx"),
                    "value",
                ),
                e_flaring=seq.step.e_flaring.value,
            )

    seq.store_result(
        name="co2_coke_tier2_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_co2_steel(year=2019, region="DE", activity="bof", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for steel production.
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
        type of steel making
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = "steel"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="q_steel",
        table="q_steel",
        coords=[year, region, activity],
        lci_flag="supply|product|steel",
    )
    seq.read_parameter(
        name="ef_co2_steel",
        table="ef_co2_steel",
        coords=[year, region, activity],
    )

    value = seq.elementary.co2_steelmaking_tier1_(
        q=seq.step.q_steel.value, ef_co2=seq.step.ef_co2_steel.value
    )
    seq.store_result(name="co2_steelmaking_tier1_", value=value, unit="t/yr", year=year)

    # pigiron
    seq.read_parameter(
        name="q_pigiron", table="q_pigiron", coords=[year, region, activity]
    )
    seq.read_parameter(
        name="ef_co2_pigiron",
        table="ef_co2_pigiron",
        coords=[year, region],
    )

    value = seq.elementary.co2_pigiron(
        q=seq.step.q_pigiron.value, ef_co2=seq.step.ef_co2_pigiron.value
    )
    seq.store_result(name="co2_pigiron", value=value, unit="t/yr", year=year)

    # dri
    seq.read_parameter(name="q_dri", table="q_dri", coords=[year, region, activity])
    seq.read_parameter(
        name="ef_co2_dri",
        table="ef_co2_dri",
        coords=[year, region],
    )

    value = seq.elementary.co2_dri_tier1_(
        q=seq.step.q_dri.value, ef_co2=seq.step.ef_co2_dri.value
    )
    seq.store_result(name="co2_dri_tier1_", value=value, unit="t/yr", year=year)

    # sinter
    seq.read_parameter(
        name="q_sinter", table="q_sinter", coords=[year, region, activity]
    )
    seq.read_parameter(
        name="ef_co2_sinter",
        table="ef_co2_sinter",
        coords=[year, region],
    )

    value = seq.elementary.co2_sinter_tier1_(
        q=seq.step.q_sinter.value, ef_co2=seq.step.ef_co2_sinter.value
    )
    seq.store_result(name="co2_sinter_tier1_", value=value, unit="t/yr", year=year)

    # ironpellet
    seq.read_parameter(
        name="q_pellet", table="q_pellet", coords=[year, region, activity]
    )
    seq.read_parameter(
        name="ef_co2_pellet",
        table="ef_co2_pellet",
        coords=[year, region],
    )

    value = seq.elementary.co2_pellet(
        q=seq.step.q_pellet.value, ef_co2=seq.step.ef_co2_pellet.value
    )
    seq.store_result(name="co2_pellet", value=value, unit="t/yr", year=year)

    # Co2 flaring
    seq.read_parameter(name="q_bfg", table="q_bfg", coords=[year, region, activity])
    seq.read_parameter(name="q_ldg", table="q_ldg", coords=[year, region, activity])
    seq.read_parameter(
        name="r_bfg",
        table="r_bfg",
        coords=[year, region, activity],
    )
    seq.read_parameter(
        name="cc_bfg",
        table="cc_bfg",
        coords=[year, region],
    )
    seq.read_parameter(
        name="r_ldg",
        table="r_ldg",
        coords=[year, region, activity],
    )
    seq.read_parameter(
        name="cc_ldg",
        table="cc_ldg",
        coords=[year, region],
    )

    value = seq.elementary.co2_flaring(
        q_bfg=seq.step.q_bfg.value,
        q_ldg=seq.step.q_ldg.value,
        r_bfg=seq.step.r_bfg.value,
        cc_bfg=seq.step.cc_bfg.value,
        r_ldg=seq.step.r_ldg.value,
        cc_ldg=seq.step.cc_ldg.value,
    )
    seq.store_result(name="co2_flaring", value=value, unit="t/yr", year=year)

    value = seq.elementary.co2_steel_total_tier1_(
        steel=seq.step.co2_steelmaking_tier1_.value,
        dri=seq.step.co2_dri_tier1_.value,
        pigiron=seq.step.co2_pigiron.value,
        sinter=seq.step.co2_sinter_tier1_.value,
        pellet=seq.step.co2_pellet.value,
        flaring=seq.step.co2_flaring.value,
    )
    seq.store_result(
        name="co2_steel_total_tier1_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_co2_steel(year=2019, region="DE", activity="bof", uncertainty="def"):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for steel and iron production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "steelmaking"
    meta_dict["product"] = "steel"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="pc",
        table="pc",
        coords=[year, region, activity],
        lci_flag="use|product|coke",
    )
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    seq.read_parameter(
        name="ci",
        table="ci",
        coords=[year, region],
        lci_flag="use|product|coal",
    )
    seq.read_parameter(
        name="c_cc",
        table="c_cc",
        coords=[year, region],
    )
    seq.read_parameter(
        name="l",
        table="l",
        coords=[year, region, activity],
        lci_flag="use|product|limestone",
    )
    seq.read_parameter(
        name="c_l",
        table="c_l",
        coords=[year, region],
    )
    seq.read_parameter(
        name="d",
        table="d",
        coords=[year, region, activity],
        lci_flag="use|product|dolomite",
    )
    seq.read_parameter(
        name="c_d",
        table="c_d",
        coords=[year, region],
    )
    seq.read_parameter(
        name="ce",
        table="ce",
        coords=[year, region, activity],
        lci_flag="use|product|carbon_electrode",
    )
    seq.read_parameter(
        name="c_ce",
        table="c_ce",
        coords=[year, region],
    )
    seq.read_parameter(
        name="cog_tier2",
        table="cog_tier2",
        coords=[year, region, activity],
        lci_flag="use|product|coke_oven_gas",
    )
    seq.read_parameter(
        name="c_cog",
        table="c_cog",
        coords=[year, region],
    )
    seq.read_parameter(
        name="s",
        table="q_steel",
        coords=[year, region, activity],
        lci_flag="supply|product|steel",
    )
    seq.read_parameter(
        name="c_s",
        table="c_s",
        coords=[year, region],
    )
    seq.read_parameter(
        name="ip",
        table="ip",
        coords=[year, region, activity],
        lci_flag="supply|by-product|iron",
    )
    seq.read_parameter(
        name="c_ip",
        table="c_ip",
        coords=[year, region],
    )
    seq.read_parameter(
        name="bfg",
        table="bfg",
        coords=[year, region, activity],
        lci_flag="supply|by-product|bfg",
    )
    seq.read_parameter(
        name="c_bg",
        table="c_bg",
        coords=[year, region],
    )

    # loop over all coke oven by-products
    d = seq.get_dimension_levels(
        year, region, activity, uncert="def", table="cob_a_tier2"
    )
    value = 0.0
    for byproduct_type in d:
        seq.read_parameter(
            name=f"cob_a_tier2_xxx_{byproduct_type}_xxx",
            table="cob_a_tier2",
            coords=[year, region, activity, byproduct_type],
            lci_flag=f"supply|by-product|{byproduct_type}",
        )
        seq.read_parameter(
            name=f"c_b_xxx_{byproduct_type}_xxx",
            table="c_b",
            coords=[year, region, byproduct_type],
        )
        value += seq.elementary.c_cob_a(
            cob_a=getattr(
                getattr(seq.step, f"cob_a_tier2_xxx_{byproduct_type}_xxx"), "value"
            ),
            c_a=getattr(getattr(seq.step, f"c_b_xxx_{byproduct_type}_xxx"), "value"),
        )
    seq.store_result(name="c_cob_a", value=value, unit="t/yr")

    # loop (sum over all input materials)
    d1 = seq.get_dimension_levels(year, region, activity, uncert="def", table="o_b")
    value = 0.0
    for material_type in d1:

        seq.read_parameter(
            name=f"o_b_xxx_{material_type}_xxx",
            table="o_b",
            coords=[year, region, activity, material_type],
            lci_flag="input",
        )
        seq.read_parameter(
            name=f"c_a_xxx_{material_type}_xxx",
            table="c_a",
            coords=[year, region, material_type],
        )
        value += seq.elementary.c_o_b(
            o_b=getattr(getattr(seq.step, f"o_b_xxx_{material_type}_xxx"), "value"),
            c_b=getattr(getattr(seq.step, f"c_a_xxx_{material_type}_xxx"), "value"),
        )
    seq.store_result(name="c_o_b", value=value, unit="t/yr")

    value = seq.elementary.co2_steelmaking_tier2_(
        pc=seq.step.pc.value,
        c_pc=seq.step.c_co.value,
        c_cob_a=seq.step.c_cob_a.value,
        ci=seq.step.ci.value,
        c_ci=seq.step.c_cc.value,
        l=seq.step.l.value,
        c_l=seq.step.c_l.value,
        d=seq.step.d.value,
        c_d=seq.step.c_d.value,
        ce=seq.step.ce.value,
        c_ce=seq.step.c_ce.value,
        c_o_b=seq.step.c_o_b.value,
        cog=seq.step.cog_tier2.value,
        c_cog=seq.step.c_cog.value,
        s=seq.step.s.value,
        c_s=seq.step.c_s.value,
        ip=seq.step.ip.value,
        c_ip=seq.step.c_ip.value,
        bfg=seq.step.bfg.value,
        c_bfg=seq.step.c_bg.value,
    )
    seq.store_result(name="co2_steelmaking_tier2_", value=value, unit="t/yr", year=year)

    # sinter
    seq.read_parameter(name="cbr", table="cbr", coords=[year, region, activity])
    seq.read_parameter(
        name="c_co",
        table="c_co",
        coords=[year, region],
    )
    # seq.read_parameter(
    #    name="cog_tier2",
    #    table="cog_tier2",
    #    coords=[year, region],
    # )
    # seq.read_parameter(
    #    name="c_cog",
    #    table="c_cog",
    #    coords=[year, region],
    # )
    # seq.read_parameter(name="bfg", table="bfg", coords=[year, region, activity])
    # seq.read_parameter(
    #    name="c_bg",
    #    table="c_bg",
    #    coords=[year, region],
    # )

    # loop over all materials
    d = seq.get_dimension_levels(
        year, region, activity, uncert="def", table="pm_a_sinter"
    )
    value = 0.0
    for material_type in d:
        seq.read_parameter(
            name=f"pm_a_sinter_xxx_{material_type}_xxx",
            table="pm_a_sinter",
            coords=[year, region, activity, material_type],
            lci_flag="input",
        )
        seq.read_parameter(
            name=f"c_a_xxx_{material_type}_xxx",
            table="c_a",
            coords=[year, region, material_type],
        )
        value += seq.elementary.c_pm_a(
            pm_a=getattr(
                getattr(seq.step, f"pm_a_sinter_xxx_{material_type}_xxx"), "value"
            ),
            c_a=getattr(getattr(seq.step, f"c_a_xxx_{material_type}_xxx"), "value"),
        )
    seq.store_result(name="c_pm_a", value=value, unit="t/yr")

    value = seq.elementary.co2_sinter_tier2_(
        cbr=seq.step.cbr.value,
        c_cbr=seq.step.c_co.value,
        cog=seq.step.cog_tier2.value,
        c_cog=seq.step.c_cog.value,
        bfg=seq.step.bfg.value,
        c_bfg=seq.step.c_bg.value,
        c_pm_a=seq.step.c_pm_a.value,
    )

    seq.store_result(name="co2_sinter_tier2_", value=value, unit="t/yr", year=year)

    # dri
    seq.read_parameter(
        name="dri_ng",
        table="dri_ng",
        coords=[year, region, activity],
    )
    seq.read_parameter(name="c_ng", table="c_ng", coords=[year, region])
    seq.read_parameter(
        name="dri_bz",
        table="dri_bz",
        coords=[year, region, activity],
    )
    seq.read_parameter(name="c_bz", table="c_bz", coords=[year, region])
    seq.read_parameter(
        name="dri_ck",
        table="dri_ck",
        coords=[year, region, activity],
    )
    seq.read_parameter(name="c_ck_energ", table="c_ck_energ", coords=[year, region])

    value = seq.elementary.co2_dri_tier2_(
        dri_ng=seq.step.dri_ng.value,
        c_ng=seq.step.c_ng.value,
        dri_bz=seq.step.dri_bz.value,
        c_bz=seq.step.c_bz.value,
        dri_ck=seq.step.dri_ck.value,
        c_ck=seq.step.c_ck_energ.value,
    )
    seq.store_result(name="co2_dri_tier2_", value=value, unit="t/yr", year=year)

    value = seq.elementary.co2_steel_total_tier2_(
        steel=seq.step.co2_steelmaking_tier2_.value,
        sinter=seq.step.co2_sinter_tier2_.value,
        dri=seq.step.co2_dri_tier2_.value,
    )
    seq.store_result(
        name="co2_steel_total_tier2_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_ch4_coke(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """Template calculation sequence for tier 2 method. Country-specific emission factors required!

    CH4 Emissions for coke production.
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
        type of coke production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    seq.store_signature(locals())

    seq.read_parameter(
        name="ck",
        table="ck",
        coords=[year, region, activity],
        lci_flag="supply|product|coke",
    )

    seq.read_parameter(
        name="ef_ch4_v3c4", table="ef_ch4_v3c4", coords=[year, region, activity]
    )

    value = seq.elementary.ch4_coke(
        ck=seq.step.ck.value, ef_ch4=seq.step.ef_ch4_v3c4.value
    )

    seq.store_result(
        name="ch4_coke",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_ch4_steel(year=2019, region="DE", activity="bof", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions for steelmaking.
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
        activity under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    # meta_dict["activity"] = "steelmaking"
    meta_dict["product"] = "steel"
    seq.store_signature(meta_dict)

    # sinter
    seq.read_parameter(
        name="q_sinter", table="q_sinter", coords=[year, region, activity]
    )
    seq.read_parameter(
        name="ef_ch4_si",
        table="ef_ch4_si",
        coords=[year, region],
    )

    value = seq.elementary.ch4_sinter(
        si=seq.step.q_sinter.value, ef_si=seq.step.ef_ch4_si.value
    )
    seq.store_result(name="ch4_sinter", value=value, unit="kg/yr", year=year)

    # pigiron
    seq.read_parameter(
        name="q_pigiron", table="q_pigiron", coords=[year, region, activity]
    )
    seq.read_parameter(
        name="ef_ch4_pi",
        table="ef_ch4_pi",
        coords=[year, region],
    )

    value = seq.elementary.ch4_pigiron(
        pi=seq.step.q_pigiron.value, ef_pi=seq.step.ef_ch4_pi.value
    )
    seq.store_result(name="ch4_pigiron", value=value, unit="kg/yr", year=year)

    # dri
    seq.read_parameter(name="q_dri", table="q_dri", coords=[year, region, activity])
    seq.read_parameter(
        name="ef_ch4_dri",
        table="ef_ch4_dri",
        coords=[year, region],
    )

    value = seq.elementary.ch4_dri(
        dri=seq.step.q_dri.value, ef_dri=seq.step.ef_ch4_dri.value
    )
    seq.store_result(name="ch4_dri", value=value, unit="kg/yr", year=year)

    value = seq.elementary.ch4_steel_total(
        sinter=seq.step.ch4_sinter.value,
        dri=seq.step.ch4_dri.value,
        pigiron=seq.step.ch4_pigiron.value,
    )
    seq.store_result(
        name="ch4_steel_total",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_n2o_flaring(year=2019, region="DE", activity="bof", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    N2O Emissions from BFG and LDG flaring.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "steelmaking"
    meta_dict["product"] = "steel"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="q_bfg",
        table="q_bfg",
        coords=[year, region, activity],
        lci_flag="use|product|bfg",
    )
    seq.read_parameter(
        name="q_ldg",
        table="q_ldg",
        coords=[year, region, activity],
        lci_flag="use|product|ldg",
    )
    seq.read_parameter(
        name="r_bfg",
        table="r_bfg",
        coords=[year, region],
    )
    seq.read_parameter(
        name="ef_n2o_bfg",
        table="ef_n2o_bfg",
        coords=[year, region],
    )
    seq.read_parameter(
        name="r_ldg",
        table="r_ldg",
        coords=[year, region, activity],
    )
    seq.read_parameter(
        name="ef_n2o_ldg",
        table="ef_n2o_ldg",
        coords=[year, region],
    )

    value = seq.elementary.n2o_flaring(
        q_bfg=seq.step.q_bfg.value,
        q_ldg=seq.step.q_ldg.value,
        r_bfg=seq.step.r_bfg.value,
        ef_bfg=seq.step.ef_n2o_bfg.value,
        r_ldg=seq.step.r_ldg.value,
        ef_ldg=seq.step.ef_n2o_ldg.value,
    )
    seq.store_result(
        name="n2o_flaring",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|N2O",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_co2_ferroalloy(
    year=2019, region="DE", product="ferrosilicon_45perc_si", uncertainty="def"
):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for ferroalloy production.
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
        type of ferroalloy
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "ferroalloy_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_ferroalloy",
        table="mp_ferroalloy",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )
    seq.read_parameter(
        name="ef_co2_ferroalloy",
        table="ef_co2_ferroalloy",
        coords=[year, region, product],
    )

    value = seq.elementary.co2_ferroalloy_tier1_(
        mp=seq.step.mp_ferroalloy.value, ef=seq.step.ef_co2_ferroalloy.value
    )
    seq.store_result(
        name="co2_ferroalloy_tier1_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_co2_ferroalloy(
    year=2019, region="DE", product="ferrosilicon_45perc_si", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for ferroalloy production.
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
        type of ferroalloy
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "ferroalloy_production"
    seq.store_signature(meta_dict)

    # loop over all agent types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_agent"
    )
    value = 0.0
    for agent_type in l:
        seq.read_parameter(
            name=f"m_agent_xxx_{agent_type}_xxx",
            table="m_agent",
            coords=[year, region, product, agent_type],
            lci_flag=f"use|product|{agent_type}",
        )
        seq.read_parameter(
            name=f"ef_agent_xxx_{agent_type}_xxx",
            table="ef_agent",
            coords=[year, region, agent_type],
        )
        value += seq.elementary.co2_in_agent_tier2_(
            m=getattr(getattr(seq.step, f"m_agent_xxx_{agent_type}_xxx"), "value"),
            ef=getattr(getattr(seq.step, f"a_agent_xxx_{agent_type}_xxx"), "value"),
        )
    seq.store_result(name="co2_in_agent_tier2_", value=value, unit="t/yr", year=year)

    # loop over all ore types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_ore"
    )
    value = 0.0
    for ore_type in l:
        seq.read_parameter(
            name=f"m_ore_xxx_{ore_type}_xxx",
            table="m_ore",
            coords=[year, region, product, ore_type],
            lci_flag=f"use|product|{ore_type}",
        )
        seq.read_parameter(
            name=f"ccontent_ore_xxx{ore_type}_xxx",
            table="ccontent_ore",
            coords=[year, region, ore_type],
        )
        value += seq.elementary.co2_in_ore(
            m=getattr(getattr(seq.step, f"m_ore_xxx_{ore_type}_xxx"), "value"),
            ccontent=getattr(
                getattr(seq.step, f"ccontent_ore_xxx_{ore_type}_xxx"), "value"
            ),
        )
    seq.store_result(name="co2_in_ore", value=value, unit="t/yr", year=year)

    # loop over all slag types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_slag"
    )
    value = 0.0
    for slag_type in l:
        seq.read_parameter(
            name=f"m_slag_xxx_{slag_type}_xxx",
            table="m_slag",
            coords=[year, region, product, slag_type],
            lci_flag=f"use|product|{slag_type}",
        )
        seq.read_parameter(
            name=f"ccontent_slag_{slag_type}_xxx",
            table="ccontent_slag",
            coords=[year, region, slag_type],
        )
        value += seq.elementary.co2_in_slag(
            m=getattr(getattr(seq.step, f"m_slag_xxx_{slag_type}_xxx"), "value"),
            ccontent=getattr(
                getattr(seq.step, f"ccontent_slag_xxx_{ore_type}_xxx"), "value"
            ),
        )
    seq.store_result(name="co2_in_slag", value=value, unit="t/yr", year=year)

    # loop over all non-product types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_out_non_product"
    )
    value = 0.0
    for non_type in l:
        seq.read_parameter(
            name=f"m_out_non_product_xxx_{non_type}_xxx",
            table="m_out_non_product",
            coords=[year, region, product, non_type],
        )
        seq.read_parameter(
            name=f"ccontent_out_non_product_xxx_{non_type}_xxx",
            table="ccontent_out_non_product",
            coords=[year, region, non_type],
        )
        value += seq.elementary.co2_out_non_product(
            m=getattr(
                getattr(seq.step, f"m_out_non_product_xxx_{non_type}_xxx"), "value"
            ),
            ccontent=getattr(
                getattr(seq.step, f"ccontent_out_non_product_xxx_{non_type}_xxx"),
                "value",
            ),
        )
    seq.store_result(name="co2_out_non_product", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="m_out_product",
        table="m_out_product",
        coords=[year, region, product],
        lci_flag=f"supply|prodcut|{product}",
    )
    seq.read_parameter(
        name="ccontent_out_product",
        table="ccontent_out_product",
        coords=[year, region, product],
    )
    value = seq.elementary.co2_out_product(
        m=seq.step.m_out_product.value,
        ccontent=seq.step.ccontent_out_product,
    )
    seq.store_result(name="co2_out_product", value=value, unit="t/yr", year=year)

    value = seq.elementary.co2_ferroalloy_tier2_3_(
        co2_in_agent=seq.step.co2_in_agent_tier2_.value,
        co2_in_ore=seq.step.co2_in_ore.value,
        co2_in_slag=seq.step.co2_in_slag.value,
        co2_out_product=seq.step.co2_out_product.value,
        co2_out_non_product=seq.step.co2_out_non_product.value,
    )
    seq.store_result(
        name="co2_ferroalloy_tier2_3_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier3_co2_ferroalloy(
    year=2019, region="DE", product="ferrosilicon_45perc_si", uncertainty="def"
):
    """Template calculation sequence for tier 3 method.

    CO2 Emissions for ferroalloy production.
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
        type of ferroalloy
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "ferroalloy_production"
    seq.store_signature(meta_dict)

    # loop over all agent types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_agent"
    )

    value = 0.0
    for agent_type in l:
        seq.read_parameter(
            name=f"m_agent_xxx_{agent_type}_xxx",
            table="m_agent",
            coords=[year, region, product, agent_type],
            lci_flag=f"use|product|{agent_type}",
        )
        seq.read_parameter(
            name=f"f_fix_c_xxx_{agent_type}_xxx",
            table="f_fix_c",
            coords=[year, region, agent_type],
        )
        seq.read_parameter(
            name=f"f_volatiles_xxx_{agent_type}_xxx",
            table="f_volatiles",
            coords=[year, region, agent_type],
        )
        seq.read_parameter(
            name=f"c_v_xxx_{agent_type}_xxx",
            table="c_v",
            coords=[year, region, agent_type],
        )
        value_c = seq.elementary.ccontent(
            f_fix_c=getattr(
                getattr(seq.step, f"f_fix_c_xxx_{agent_type}_xxx"), "value"
            ),
            f_volatiles=getattr(
                getattr(seq.step, f"f_volatiles_xxx_{agent_type}_xxx"), "value"
            ),
            c_v=getattr(getattr(seq.step, f"c_v_xxx_{agent_type}_xxx"), "value"),
        )
        seq.store_result(
            name=f"ccontent_xxx_{agent_type}_xxx", value=value_c, unit="t/t", year=year
        )

        value += seq.elementary.co2_in_agent_tier3_(
            m=getattr(getattr(seq.step, f"m_agent_xxx_{agent_type}_xxx"), "value"),
            ef=getattr(getattr(seq.step, f"ccontent_xxx_{agent_type}_xxx"), "value"),
        )
    seq.store_result(name="co2_in_agent_tier3_", value=value, unit="t/yr", year=year)

    # loop over all ore types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_ore"
    )
    value = 0.0
    for ore_type in l:
        seq.read_parameter(
            name=f"m_ore_xxx_{ore_type}_xxx",
            table="m_ore",
            coords=[year, region, product, ore_type],
            lci_flag=f"use|product|{ore_type}",
        )
        seq.read_parameter(
            name=f"ccontent_ore_xxx_{ore_type}_xxx",
            table="ccontent_ore",
            coords=[year, region, ore_type],
        )
        value += seq.elementary.co2_in_ore(
            m=getattr(getattr(seq.step, f"m_ore_xxx_{ore_type}_xxx"), "value"),
            ccontent=getattr(
                getattr(seq.step, f"ccontent_ore_xxx_{ore_type}_xxx"), "value"
            ),
        )
    seq.store_result(name="co2_in_ore", value=value, unit="t/yr", year=year)

    # loop over all slag types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_slag"
    )
    value = 0.0
    for slag_type in l:
        seq.read_parameter(
            name="m_slag",
            table="m_slag",
            coords=[year, region, product, slag_type],
            lci_flag=f"use|product|{slag_type}",
        )
        seq.read_parameter(
            name="ccontent_slag",
            table="ccontent_slag",
            coords=[year, region, slag_type],
        )
        value += seq.elementary.co2_in_slag(
            m=seq.seq.step.m_slag.value, ccontent=seq.step.ccontent_slag.value
        )
    seq.store_result(name="co2_in_slag", value=value, unit="t/yr", year=year)

    # loop over all non-product types
    l = seq.get_dimension_levels(
        year, region, product, uncert=uncertainty, table="m_out_non_product"
    )
    value = 0.0
    for non_type in l:
        seq.read_parameter(
            name=f"m_out_non_product_xxx_{non_type}_xxx",
            table="m_out_non_product",
            coords=[year, region, product, non_type],
        )
        seq.read_parameter(
            name=f"ccontent_out_non_product_xxx_{non_type}_xxx",
            table="ccontent_out_non_product",
            coords=[year, region, non_type],
        )
        value += seq.elementary.co2_out_non_product(
            m=getattr(
                getattr(seq.step, f"m_out_non_product_xxx_{non_type}_xxx"), "value"
            ),
            ccontent=getattr(
                getattr(seq.step, f"ccontent_out_non_product_xxx_{non_type}_xxx"),
                "value",
            ),
        )
    seq.store_result(name="co2_out_non_product", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="m_out_product",
        table="m_out_product",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )
    seq.read_parameter(
        name="ccontent_out_product",
        table="ccontent_out_product",
        coords=[year, region, product],
    )
    value = seq.elementary.co2_out_product(
        m=seq.seq.step.m_out_product.value,
        ccontent=seq.step.ccontent_out_product.value,
    )
    seq.store_result(name="co2_out_product", value=value, unit="t/yr", year=year)

    value = seq.elementary.co2_ferroalloy_tier2_3_(
        co2_in_agent=seq.step.co2_in_agent_tier3_.value,
        co2_in_ore=seq.step.co2_in_ore.value,
        co2_in_slag=seq.step.co2_in_slag.value,
        co2_out_product=seq.step.co2_out_product.value,
        co2_out_non_product=seq.step.co2_out_non_product.value,
    )
    seq.store_result(
        name="co2_ferroalloy_tier2_3_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_ch4_ferroalloy(
    year=2019, region="DE", product="ferrosilicon_45perc_si", uncertainty="def"
):
    """Template calculation sequence for tier 1 method.

    CH4 Emissions for ferroalloy production.
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
        type of ferroalloy
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "ferroalloy_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_ferroalloy",
        table="mp_ferroallay",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )
    seq.read_parameter(
        name="ef_ch4_ferroalloy_tier1",
        table="ef_ch4_ferroalloy_tier1",
        coords=[year, region, product],
    )
    value = seq.elementary.ch4_ferroalloy_tier1_(
        mp=seq.seq.step.mp_ferroalloy.value, ef=seq.step.ef_ch4_ferroalloy_tier1.value
    )
    seq.store_result(
        name="ch4_ferroalloy_tier1_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_ch4_ferroalloy(
    year=2019, region="DE", product="ferrosilicon_45perc_si", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CH4 Emissions for ferroalloy production.
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
        type of ferroalloy
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "ferroalloy_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_ferroalloy",
        table="mp_ferroalloy",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )

    # loop over all agent types
    l = seq.get_dimension_levels(
        year,
        region,
        product,
        uncert=uncertainty,
        table="furnace_operation_frac",
    )

    value = 0.0
    for furnace_type in l:

        seq.read_parameter(
            name=f"furnace_operation_frac_xxx_{furnace_type}_xxx",
            table="furnace_operation_frac",
            coords=[year, region, product, furnace_type],
        )

        seq.read_parameter(
            name=f"ef_ch4_ferroalloy_tier2_xxx_{furnace_type}_xxx",
            table="ef_ch4_ferroalloy_tier2",
            coords=[year, region, product, furnace_type],
        )
        value += seq.elementary.ch4_ferroalloy_tier2_(
            mp=getattr(
                getattr(seq.step, f"furnace_operation_frac_xxx_{furnace_type}_xxx"),
                "value",
            ),
            ef=getattr(
                getattr(seq.step, f"ef_ch4_ferroalloy_tier2_xxx_{furnace_type}_xxx"),
                "value",
            ),
            furnace_operation_frac=seq.step.furnace_operation_frac.value,
        )
    seq.store_result(
        name="ch4_ferroalloy_tier2_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_co2_alu(year=2019, region="DE", activity="prebake", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for alu production.
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
        process type of aluminium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "aluminium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_alu",
        table="mp_alu",
        coords=[year, region, activity],
        lci_flag="supply|product|aluminium",
    )
    seq.read_parameter(
        name="ef_co2_alu",
        table="ef_co2_alu",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_co2_tier1_(
        mp=seq.step.mp_alu.value, ef=seq.step.ef_co2_alu.value
    )

    seq.store_result(
        name="e_co2_tier1_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_co2_alu(year=2019, region="DE", activity="prebake_cwpb", uncertainty="def"):
    """Template calculation sequence for tier 2 and 3 method.

    CO2 Emissions for alu production.
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
        process type of aluminium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "aluminium"
    seq.store_signature(meta_dict)

    if "prebake" in activity:
        seq.read_parameter(name="nac_alu", table="nac_alu", coords=[year, region])
        seq.read_parameter(
            name="mp_alu",
            table="mp_alu",
            coords=[year, region, activity],
            lci_flag="supply|product|aluminium",
        )
        seq.read_parameter(name="s_a", table="s_a", coords=[year, region])
        seq.read_parameter(name="ash_a", table="ash_a", coords=[year, region])

        value = seq.elementary.e_co2_anode(
            nac=seq.step.nac_alu.value,
            mp=seq.step.mp_alu.value,
            s_a=seq.step.s_a.value,
            ash_a=seq.step.ash_a.value,
        )

        seq.store_result(name="e_co2_anode", value=value, unit="t/yr", year=year)

        seq.read_parameter(name="ga", table="ga", coords=[year, region])
        seq.read_parameter(name="h_w", table="h_w", coords=[year, region])
        seq.read_parameter(name="ba", table="ba", coords=[year, region])
        seq.read_parameter(name="wt", table="wt", coords=[year, region])

        value = seq.elementary.e_co2_pitch(
            ga=seq.step.ga.value,
            h_w=seq.step.h_w.value,
            ba=seq.step.ba.value,
            wt=seq.step.wt.value,
        )

        seq.store_result(name="e_co2_pitch", value=value, unit="t/yr", year=year)

        seq.read_parameter(name="pcc", table="pcc", coords=[year, region])
        seq.read_parameter(name="c_pc", table="c_pc", coords=[year, region])
        seq.read_parameter(name="ash_pc", table="ash_pc", coords=[year, region])

        value = seq.elementary.e_co2_packing(
            pcc=seq.step.pcc.value,
            ba=seq.step.ba.value,
            s_pc=seq.step.c_pc.value,
            ash_pc=seq.step.ash_pc.value,
        )

        seq.store_result(name="e_co2_packing", value=value, unit="t/yr", year=year)

        value = seq.elementary.e_co2_prebake(
            e_co2_pitch=seq.step.e_co2_pitch.value,
            e_co2_anode=seq.step.e_co2_anode.value,
            e_co2_packing=seq.step.e_co2_packing.value,
        )
        seq.store_result(
            name="e_co2_prebake",
            value=value,
            unit="t/yr",
            year=year,
            lci_flag="emission|air|CO2",
        )

    elif "soderberg" in activity:
        seq.read_parameter(
            name="pc_tier2", table="pc_tier2", coords=[year, region, activity]
        )
        seq.read_parameter(
            name="mp_alu",
            table="mp_alu",
            coords=[year, region, activity],
            lci_flag="supply|product|aluminium",
        )
        seq.read_parameter(name="csm", table="csm", coords=[year, region, activity])
        seq.read_parameter(name="bc", table="bc", coords=[year, region])
        seq.read_parameter(name="s_p", table="s_p", coords=[year, region])
        seq.read_parameter(name="ash_p", table="ash_p", coords=[year, region])
        seq.read_parameter(name="bh_pc", table="bh_pc", coords=[year, region])
        seq.read_parameter(name="s_c", table="s_c", coords=[year, region])
        seq.read_parameter(name="ash_c", table="ash_c", coords=[year, region])
        seq.read_parameter(name="cd", table="cd", coords=[year, region])
        value = seq.elementary.e_co2_soderberg(
            pc=seq.step.pc_tier2.value,
            mp=seq.step.mp_alu.value,
            csm=seq.step.csm.value,
            bc=seq.step.bc.value,
            s_p=seq.step.s_p.value,
            ash_p=seq.step.ash_p.value,
            h_p=seq.step.bh_pc.value,
            s_c=seq.step.s_c.value,
            ash_c=seq.step.ash_c.value,
            cd=seq.step.cd.value,
        )
        seq.store_result(
            name="e_co2_soderberg",
            value=value,
            unit="t/yr",
            year=year,
            lci_flag="emission|air|CO2",
        )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_cf4_alu(year=2019, region="DE", activity="prebake_cwpb", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CF4 Emissions for alu production.
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
        process type of aluminium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "aluminium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_alu",
        table="mp_alu",
        coords=[year, region, activity],
        lci_flag="supply|product|aluminium",
    )
    seq.read_parameter(
        name="ef_cf4_alu",
        table="ef_cf4_alu",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_cf4_tier1_(
        mp=seq.step.mp_alu.value, ef=seq.step.ef_cf4_alu.value
    )

    seq.store_result(
        name="e_cf4_tier1_",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|CF4",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_c2f6_alu(year=2019, region="DE", activity="prebake_cwpb", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    C2F6 Emissions for alu production.
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
        process type of aluminium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "aluminium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_alu",
        table="mp_alu",
        coords=[year, region, activity],
        lci_flag="supply|product|aluminium",
    )
    seq.read_parameter(
        name="ef_c2f6_alu",
        table="ef_c2f6_alu",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_c2f6_tier1_(
        mp=seq.step.mp_alu.value, ef=seq.step.ef_c2f6_alu.value
    )

    seq.store_result(
        name="e_c2f6_tier1_",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|C2F6",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier2_3_pfc_alu(year=2019, region="DE", activity="prebake_cwpb", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CF4 and C2F6 Emissions for alu production.
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
        process type of aluminium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "aluminium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mp_alu",
        table="mp_alu",
        coords=[year, region, activity],
        lci_flag="supply|product|aluminium",
    )
    seq.read_parameter(
        name="s_cf4_alu",
        table="s_cf4_alu",
        coords=[year, region, activity],
    )
    seq.read_parameter(
        name="aem",
        table="aem",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_cf4_tier2_3_(
        mp=seq.step.mp_alu.value, s=seq.step.s_cf4_alu.value, aem=seq.step.aem.value
    )

    seq.store_result(name="e_cf4_tier2_3_", value=value, unit="kg/yr", year=year)

    seq.read_parameter(
        name="f_alu",
        table="f_alu",
        coords=[year, region, activity],
    )

    value = seq.elementary.e_c2f6_tier2_3_(
        e_cf4=seq.step.e_cf4_tier2_3_.value, f=seq.step.f_alu.value
    )
    seq.store_result(
        name="e_c2f6_tier2_3_",
        value=value,
        unit="kg/yr",
        year=year,
        lci_flag="emission|air|C2F6",
    )

    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_2_co2_magnesium(
    year=2019, region="DE", carbonate_type="dolomite", uncertainty="def"
):
    """Template calculation sequence for tier 1 and tier 2 method.

    CO2 Emissions for primary magnesium production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    carbonate_type : str
        carbonate type used as raw material for magnesium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "magnesium_production"
    meta_dict["prodcut"] = "magnesium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="p_magnesium",
        table="p_magnesium",
        coords=[year, region, carbonate_type],
        lci_flag="supply|product|magnesium",
    )
    seq.read_parameter(
        name="ef_co2_magnesium",
        table="ef_co2_magnesium",
        coords=[year, region, carbonate_type],
    )
    value = seq.elementary.e_co2_magnesium(
        p=seq.step.p_magnesium.value, ef=seq.step.ef_co2_magnesium.value
    )

    seq.store_result(
        name="e_co2_magnesium",
        value=value,
        unit="Gg/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_sf6_magnesium(
    year=2019, region="DE", carbonate_type="dolomite", uncertainty="def"
):
    """Template calculation sequence for tier 1 method.

    SF6 Emissions for primary magnesium production.
    Each step either calls an elementary equation, calls a parameter,
    or performs a simple operation like a loop or a conditional.
    Each step delivers one return value and unit to the list of variables.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    carbonate_type : str
        carbonate type used as raw material for magnesium production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "magnesium_production"
    meta_dict["prodcut"] = "magnesium"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="mg_c_magnesium",
        table="mg_c_magnesium",
        coords=[year, region, carbonate_type],
        lci_flag="supply|product|magnesium",
    )
    seq.read_parameter(
        name="ef_sf6_magnesium",
        table="ef_sf6_magnesium",
        coords=[year, region, carbonate_type],
    )
    value = seq.elementary.e_sf6_magnesium(
        p=seq.step.mg_c_magnesium.value, ef=seq.step.ef_sf6_magnesium.value
    )

    seq.store_result(
        name="e_sf6_magnesium",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|SF6",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_co2_lead(year=2019, region="DE", activity="lead_default", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for lead production.
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
        process type for lead production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "lead"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="q_lead",
        table="q_lead",
        coords=[year, region, activity],
        lci_flag="supply|product|lead",
    )
    seq.read_parameter(
        name="ef_co2_lead",
        table="ef_co2_lead",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_co2_lead(
        q=seq.step.q_lead.value, ef=seq.step.ef_co2_lead.value
    )

    seq.store_result(
        name="e_co2_lead",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step


def tier1_co2_zinc(year=2019, region="DE", activity="zinc_default", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for lead production.
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
        process type for zinc production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Metal sequence started --->")

    meta_dict = locals()
    meta_dict["prodcut"] = "zinc"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="q_zinc",
        table="q_zinc",
        coords=[year, region, activity],
        lci_flag="supply|product|zinc",
    )
    seq.read_parameter(
        name="ef_co2_zinc",
        table="ef_co2_zinc",
        coords=[year, region, activity],
    )
    value = seq.elementary.e_co2_zinc(
        q=seq.step.q_zinc.value, ef=seq.step.ef_co2_zinc.value
    )

    seq.store_result(
        name="e_co2_zinc",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Metal sequence finalized.")
    return seq.step
