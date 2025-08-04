import logging
from dataclasses import replace

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def coke_tier1(
    year=2019, region="DE", activity="by-product_recovery", uncertainty="def"
):
    """
    calculation sequence based on the tier 1a method of ipcc.

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
    logger.info("PPF sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = f"coke_from_{activity}"
    seq.store_signature(meta_dict)

    # read country data
    seq.read_parameter(
        name="coke",
        table="coke",
        coords=[year, region],
    )
    # read country coefficient
    seq.read_parameter(
        name="coke_activity_per_reg",
        table="coke_activity_per_reg",
        coords=[year, region, activity],
    )
    # calc reference supply
    value = seq.elementary.ck_calculated(
        coke=seq.step.coke.value,
        coke_activity_per_reg=seq.step.coke_activity_per_reg.value,
    )
    # store reference supply
    seq.store_result(
        name="ck_calculated",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag=f"supply|product|coke_from_{activity}",
    )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_coke"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_coke"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_coke_xxx_{input_product}_xxx",
            table="energy_use_per_coke",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.ck_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_coke_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )
    #    # read emission coefficient TODO: loop over emissions (same unit!)
    #    seq.read_parameter(
    #        name="ef_co2_coke", table="ef_co2_coke", coords=[year, region, activity]
    #    )
    #    # calc emission
    #    value = seq.elementary.co2_coke_tier1a_(
    #        ck=seq.step.ck_calculated.value, ef_co2=seq.step.ef_co2_coke.value
    #    )
    #    # store emission
    #    seq.store_result(
    #        name="co2_coke_tier1a_",
    #        value=value,
    #        unit="t/yr",
    #        year=year,
    #        lci_flag="emission|air|CO2",
    #    )
    #
    #    # read emission coefficient TODO: loop over emissions (same unit!)
    #    seq.read_parameter(
    #        name="ef_ch4_coke", table="ef_ch4_coke", coords=[year, region, activity]
    #    )
    #    # calc emission
    #    value = seq.elementary.ch4_coke(
    #        ck=seq.step.ck_calculated.value, ef_ch4=seq.step.ef_ch4_coke.value
    #    )
    #    # store emission
    #    seq.store_result(
    #        name="ch4_coke",
    #        value=value,
    #        unit="t/yr",
    #        year=year,
    #        lci_flag="emission|air|CH4",
    #    )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="emission_per_coke"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="emission_per_coke"
        )

    for emission in d:
        # read use coefficient
        seq.read_parameter(
            name=f"emission_per_coke_xxx_{emission}_xxx",
            table="emission_per_coke",
            coords=[year, region, activity, emission],
        )
        # calc use
        value = seq.elementary.emission(
            product_output=seq.step.ck_calculated.value,
            emission_product_ratio=getattr(
                getattr(seq.step, f"emission_per_coke_xxx_{emission}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"emission_xxx_{emission}_xxx",
            value=value,
            unit="t/yr",
            lci_flag=f"emission|air|{emission}",
        )

    # read use coefficient TODO: loop over raw materials (same unit!)
    seq.read_parameter(
        name="coal_use_per_coke",
        table="coal_use_per_coke",
        coords=[year, region, activity],
    )
    # calc use
    value = seq.elementary.coal_use(
        coke_output=seq.step.ck_calculated.value,
        coal_coke_ratio=seq.step.coal_use_per_coke.value,
    )
    # store use
    seq.store_result(
        name="coal_use",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="use|product|coking_coal",
    )

    # add all by-products to production process
    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year,
            region,
            activity,
            uncert=uncertainty,
            table="byproduct_supply_per_coke",
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="byproduct_supply_per_coke"
        )

    for by_product in d:
        # read supply coefficient
        seq.read_parameter(
            name=f"byproduct_supply_per_coke_xxx_{by_product}_xxx",
            table="byproduct_supply_per_coke",
            coords=[year, region, activity, by_product],
        )
        # calc supply
        value = seq.elementary.by_product_supply(
            coke=seq.step.ck_calculated.value,
            ratio=getattr(
                getattr(seq.step, f"byproduct_supply_per_coke_xxx_{by_product}_xxx"),
                "value",
            ),
        )
        # store supply
        seq.store_result(
            name=f"by_product_supply_xxx_{by_product}_xxx",
            value=value,
            unit="t/yr",
            lci_flag=f"supply|product|{by_product}",
        )

    # add all feedstock uses to production process
    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year,
            region,
            activity,
            uncert=uncertainty,
            table="feedstock_use_per_coke",
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="feedstock_use_per_coke"
        )
    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"feedstock_use_per_coke_xxx_{input_product}_xxx",
            table="feedstock_use_per_coke",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.feedstock_use(
            product_output=seq.step.ck_calculated.value,
            feedstock_product_ratio=getattr(
                getattr(seq.step, f"feedstock_use_per_coke_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"feedstock_use_xxx_{input_product}_xxx",
            value=value,
            unit="kg/yr",
            lci_flag=f"use|product|{input_product}",
        )

    # add transfer coefficients
    if uncertainty in ["def", "min", "max", "sample"]:
        p = seq.get_dimension_levels(
            year,
            region,
            activity,
            uncert=uncertainty,
            table="product_transf_coeff_coke",
        )
    else:
        p = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="product_transf_coeff_coke"
        )

    for input_product in p:
        if uncertainty in ["def", "min", "max", "sample"]:
            r = seq.get_dimension_levels(
                year,
                region,
                activity,
                input_product,
                uncert=uncertainty,
                table="product_transf_coeff_coke",
            )
        else:
            r = seq.get_dimension_levels(
                year,
                region,
                activity,
                input_product,
                uncert="def",
                table="product_transf_coeff_coke",
            )

        for reference_output in r:

            seq.read_parameter(
                name=f"product_transf_coeff_coke_xxx_{input_product}_{reference_output}_xxx",
                table="product_transf_coeff_coke",
                coords=[
                    year,
                    region,
                    activity,
                    input_product,
                    reference_output,
                ],
                lci_flag=f"transf_coeff|product|{input_product}|{reference_output}",
            )

    if uncertainty in ["def", "min", "max", "sample"]:
        p = seq.get_dimension_levels(
            year,
            region,
            activity,
            uncert=uncertainty,
            table="emission_transf_coeff_coke",
        )
    else:
        p = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="emission_transf_coeff_coke"
        )

    for input_product in p:
        if uncertainty in ["def", "min", "max", "sample"]:
            r = seq.get_dimension_levels(
                year,
                region,
                activity,
                input_product,
                uncert=uncertainty,
                table="emission_transf_coeff_coke",
            )
        else:
            r = seq.get_dimension_levels(
                year,
                region,
                activity,
                input_product,
                uncert="def",
                table="emission_transf_coeff_coke",
            )

        for reference_output in r:

            seq.read_parameter(
                name=f"emission_transf_coeff_coke_xxx_{input_product}_{reference_output}_xxx",
                table="emission_transf_coeff_coke",
                coords=[
                    year,
                    region,
                    activity,
                    input_product,
                    reference_output,
                ],
                lci_flag=f"transf_coeff|emission|{input_product}|{reference_output}",
            )

    logger.info("---> PPF sequence finalized.")
    return seq.step


def steel_tier1(year=2019, region="DE", activity="bof", uncertainty="def"):
    """
    calculation sequence based on the tier 1 method of ipcc.

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
        type of steel production
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("PPF sequence started --->")

    meta_dict = locals()
    meta_dict["product"] = f"steel_from_{activity}"
    seq.store_signature(meta_dict)

    # read country data
    seq.read_parameter(
        name="steel",
        table="steel",
        coords=[year, region],
    )
    # read country coefficient
    seq.read_parameter(
        name="steel_activity_per_reg",
        table="steel_activity_per_reg",
        coords=[year, region, activity],
    )
    # calc reference supply
    value = seq.elementary.steel_calculated(
        steel=seq.step.steel.value,
        steel_activity_per_reg=seq.step.steel_activity_per_reg.value,
    )
    # store reference supply
    seq.store_result(
        name="steel_calculated",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag=f"supply|product|steel_from_{activity}",
    )

    seq.read_parameter(
        name="pigiron_per_steel",
        table="pigiron_per_steel",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="dri_per_steel", table="dri_per_steel", coords=[year, region, activity]
    )

    seq.read_parameter(
        name="sinter_per_steel",
        table="sinter_per_steel",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="pellet_per_steel",
        table="pellet_per_steel",
        coords=[year, region, activity],
    )

    value = seq.elementary.q_pigiron_calculated(
        steel=seq.step.steel_calculated.value,
        pigiron_per_steel=seq.step.pigiron_per_steel.value,
    )
    seq.store_result(name="q_pigiron", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="iron_ore_per_pigiron",
        table="iron_ore_per_pigiron",
        coords=[year, region],
    )

    value = seq.elementary.iron_ore_use_pigiron(
        pig_iron=seq.step.q_pigiron.value, factor=seq.step.iron_ore_per_pigiron.value
    )
    seq.store_result(
        name="iron_ore_use_pigiron",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="use|product|iron_ore",
    )

    value = seq.elementary.q_dri_calculated(
        steel=seq.step.steel_calculated.value,
        dri_per_steel=seq.step.dri_per_steel.value,
    )
    seq.store_result(name="q_dri", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="iron_ore_per_dri",
        table="iron_ore_per_dri",
        coords=[year, region],
    )

    value = seq.elementary.iron_ore_use_dri(
        dri=seq.step.q_dri.value, factor=seq.step.iron_ore_per_dri.value
    )
    seq.store_result(
        name="iron_ore_use_dri",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="use|product|iron_ore",
    )

    value = seq.elementary.q_sinter_calculated(
        steel=seq.step.steel_calculated.value,
        sinter_per_steel=seq.step.sinter_per_steel.value,
    )
    seq.store_result(name="q_sinter", value=value, unit="t/yr", year=year)

    value = seq.elementary.q_pellet_calculated(
        steel=seq.step.steel_calculated.value,
        pellet_per_steel=seq.step.pellet_per_steel.value,
    )
    seq.store_result(name="q_pellet", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="bfg_per_steel", table="bfg_per_steel", coords=[year, region, activity]
    )

    value = seq.elementary.q_bfg_calculated(
        steel=seq.step.steel_calculated.value,
        bfg_per_steel=seq.step.bfg_per_steel.value,
    )
    seq.store_result(name="q_bfg", value=value, unit="t/yr", year=year)

    seq.read_parameter(
        name="ldg_per_steel", table="ldg_per_steel", coords=[year, region, activity]
    )
    value = seq.elementary.q_ldg_calculated(
        steel=seq.step.steel_calculated.value,
        ldg_per_steel=seq.step.ldg_per_steel.value,
    )
    seq.store_result(name="q_ldg", value=value, unit="t/yr", year=year)

    ### co2 ####
    seq.read_parameter(
        name="ef_co2_steel",
        table="ef_co2_steel",
        coords=[year, region, activity],
    )

    value = seq.elementary.co2_steelmaking_tier1_(
        q=seq.step.steel_calculated.value, ef_co2=seq.step.ef_co2_steel.value
    )
    seq.store_result(name="co2_steelmaking_tier1_", value=value, unit="t/yr", year=year)

    # pigiron

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
        name="ef_co2_pellet",
        table="ef_co2_pellet",
        coords=[year, region],
    )

    value = seq.elementary.co2_pellet(
        q=seq.step.q_pellet.value, ef_co2=seq.step.ef_co2_pellet.value
    )
    seq.store_result(name="co2_pellet", value=value, unit="t/yr", year=year)

    # Co2 flaring

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

    ## ch4 ##
    # sinter
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
        name="ef_ch4_pi",
        table="ef_ch4_pi",
        coords=[year, region],
    )

    value = seq.elementary.ch4_pigiron(
        pi=seq.step.q_pigiron.value, ef_pi=seq.step.ef_ch4_pi.value
    )
    seq.store_result(name="ch4_pigiron", value=value, unit="kg/yr", year=year)

    # dri
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

    ## n2o

    seq.read_parameter(
        name="ef_n2o_bfg",
        table="ef_n2o_bfg",
        coords=[year, region],
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

    # add inputs
    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_steel"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_steel"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_steel_xxx_{input_product}_xxx",
            table="energy_use_per_steel",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.steel_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_steel_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_A_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_dri"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_dri"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_dri_xxx_{input_product}_xxx",
            table="energy_use_per_dri",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.steel_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_dri_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_B_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_pellet"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_pellet"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_pellet_xxx_{input_product}_xxx",
            table="energy_use_per_pellet",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.steel_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_pellet_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_C_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_pigiron"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_pigiron"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_pigiron_xxx_{input_product}_xxx",
            table="energy_use_per_pigiron",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.steel_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_pigiron_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_D_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="energy_use_per_sinter"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="energy_use_per_sinter"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"energy_use_per_sinter_xxx_{input_product}_xxx",
            table="energy_use_per_sinter",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.energy_use(
            product_output=seq.step.steel_calculated.value,
            energy_product_ratio=getattr(
                getattr(seq.step, f"energy_use_per_sinter_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"energy_use_xxx_E_{input_product}_xxx",
            value=value,
            unit="GJ/yr",
            lci_flag=f"use|product|{input_product}",
        )

    if uncertainty in ["def", "min", "max", "sample"]:
        d = seq.get_dimension_levels(
            year, region, activity, uncert=uncertainty, table="feedstock_use_per_steel"
        )
    else:
        d = seq.get_dimension_levels(
            year, region, activity, uncert="def", table="feedstock_use_per_steel"
        )

    for input_product in d:
        # read use coefficient
        seq.read_parameter(
            name=f"feedstock_use_per_steel_xxx_{input_product}_xxx",
            table="feedstock_use_per_steel",
            coords=[year, region, activity, input_product],
        )
        # calc use
        value = seq.elementary.feedstock_use(
            product_output=seq.step.steel_calculated.value,
            feedstock_product_ratio=getattr(
                getattr(seq.step, f"feedstock_use_per_steel_xxx_{input_product}_xxx"),
                "value",
            ),
        )
        # store use
        seq.store_result(
            name=f"feedstock_use_xxx_{input_product}_xxx",
            value=value,
            unit="kg/yr",
            lci_flag=f"use|product|{input_product}",
        )

    logger.info("---> PPF sequence finalized.")
    return seq.step
