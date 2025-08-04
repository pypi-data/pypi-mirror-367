import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def ethylene_recipe_emissions_tier1(
    year=2006,
    region="GB",
    product="ethylene",
    activity="sc",
    feedstocktype="naphtha",
    uncertainty="def",
):
    """Tier 1 method CO2 Emissions.
    Starting with data input for parameter pp_i (anual production of petrochemical)

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        type of petrochemical product
    activity : str
        type of petrochemical transforming activity i (e.g. conventional steam reforming of natural gas for methanol production)
    feedstocktype : str
        type of feedstock k used by activity i for the production of the petrochemical product
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'
    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Chemical sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "petrochem"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="pp_i",
        table="pp_i",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )

    seq.read_parameter(
        name="pp_share_i_j",
        table="pp_share_i_j",
        coords=[
            year,
            region,
            product,
            activity,
        ],
    )

    seq.read_parameter(
        name="pp_share_i_j_k",
        table="pp_share_i_j_k",
        coords=[
            year,
            region,
            product,
            activity,
            feedstocktype,
        ],
    )

    seq.read_parameter(
        name="ef_co2_i_k",
        table="ef_co2_i_k",
        coords=[
            year,
            region,
            product,
            activity,
            feedstocktype,
        ],
    )

    seq.read_parameter(
        name="gaf",
        table="gaf",
        coords=[year, region],
    )

    pp_i_j_k = seq.elementary.pp_i_j_k(
        pp_i=seq.step.pp_i.value,
        pp_share_i_j=seq.step.pp_share_i_j.value,
        pp_share_i_j_k=seq.step.pp_share_i_j_k.value,
    )

    seq.store_result(
        name="pp_i_j_k",
        value=pp_i_j_k,
        unit="t/year",
        year=year,
        lci_flag=f"supply|product|{product}",
    )

    value = seq.elementary.eco2_tier1(
        pp_i=seq.step.pp_i_j_k.value,
        ef=seq.step.ef_co2_i_k.value,
        gaf=seq.step.gaf.value,
    )

    seq.store_result(
        name="eco2_tier1",
        value=value,
        unit="t/year",
        year=year,
        lci_flag="emission|air|CO2",
    )

    # Feedstock use calculation using LCI coefficients

    seq.read_parameter(
        name="feedstock_use_in_refinery_per_ethylene",
        table="feedstock_use_in_refinery_per_ethylene",
        coords=[
            year,
            region,
            product,
            activity,
            feedstocktype,
        ],
    )

    feedstock_use = seq.elementary.input_use(
        pp_i_j_k=seq.step.pp_i_j_k.value,
        lci_coefficient=seq.step.feedstock_use_in_refinery_per_ethylene.value,
    )

    seq.store_result(
        name="feedstock_consumption_in_refinery_per_ethylene",
        value=feedstock_use,
        unit="t/yr",
        lci_flag=f"use|product|{feedstocktype}",
        eq_name="input_use",
    )

    #################################################################################################################
    # Energy use calculation using LCI coefficients
    #################################################################################################################
    if uncertainty in ["def", "min", "max", "sample"]:
        energy_inputs = seq.get_dimension_levels(
            year,
            region,
            activity,
            feedstocktype,
            table="energy_use_in_refinery_per_ethylene",
            uncert=uncertainty,
        )
    else:
        energy_inputs = seq.get_dimension_levels(
            year,
            region,
            activity,
            feedstocktype,
            table="energy_use_in_refinery_per_ethylene",
            uncert=uncertainty,
        )

    if energy_inputs:
        logger.info(f"energy inputs: {set(energy_inputs)}")
        for inputs in energy_inputs:
            # read supply coefficient
            seq.read_parameter(
                name=f"energy_use_in_refinery_per_ethylene_xxx_{inputs}_xxx",
                table="energy_use_in_refinery_per_ethylene",
                coords=[
                    year,
                    region,
                    activity,
                    feedstocktype,
                    inputs,
                ],
            )
            # calc supply
            value = seq.elementary.input_use(
                pp_i_j_k=seq.step.pp_i_j_k.value,
                lci_coefficient=getattr(
                    getattr(
                        seq.step,
                        f"energy_use_in_refinery_per_ethylene_xxx_{inputs}_xxx",
                    ),
                    "value",
                ),
            )
            # store supply
            seq.store_result(
                name=f"energy_use_in_refinery_per_ethylene_xxx_{inputs}_xxx",
                value=value,
                unit="TJ/yr",
                lci_flag=f"use|product|{inputs}",
                eq_name="input_use",
            )

    else:
        logger.info(
            f"No energy inputs use calculated using LCI coefficients for activity: {activity}"
        )

    #################################################################################################################
    # By-product supply calculation using LCI coefficients
    #################################################################################################################
    if uncertainty in ["def", "min", "max", "sample"]:
        byproduct_list = seq.get_dimension_levels(
            year,
            region,
            activity,
            feedstocktype,
            table="byproduct_in_refinery_per_ethylene",
            uncert=uncertainty,
        )
    else:
        byproduct_list = seq.get_dimension_levels(
            year,
            region,
            activity,
            feedstocktype,
            table="byproduct_in_refinery_per_ethylene",
            uncert=uncertainty,
        )

    if byproduct_list:
        logger.info(f"by products: {set(byproduct_list)}")
        for by_product in byproduct_list:
            # read supply coefficient
            seq.read_parameter(
                name=f"byproduct_in_refinery_per_ethylene_xxx_{by_product}_xxx",
                table="byproduct_in_refinery_per_ethylene",
                coords=[
                    year,
                    region,
                    activity,
                    feedstocktype,
                    by_product,
                ],
            )
            # calc supply
            value = seq.elementary.by_product_supply(
                pp_i_j_k=seq.step.pp_i_j_k.value,
                lci_coefficient=getattr(
                    getattr(
                        seq.step,
                        f"byproduct_in_refinery_per_ethylene_xxx_{by_product}_xxx",
                    ),
                    "value",
                ),
            )
            # store supply
            seq.store_result(
                name=f"by_product_supply_xxx_{by_product}_xxx",
                value=value,
                unit="t/yr",
                lci_flag=f"supply|product|{by_product}_from_{activity}",
                eq_name="by_product_supply",
            )
    else:
        logger.info(
            f"No by-product supply calculation using LCI coefficients for activity: {activity}"
        )

    logger.info("---> Ethylene sequence finalized.")
    return seq.step
