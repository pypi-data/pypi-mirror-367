"""
Sequences to determine GHG emission"s from mineral industry.
"""

"""
As the PPF model for cement includes some additional equations not covered by the IPCC
guidelines, the "Sequence.py" file is located in the PPF repository and is calling the
IPCC equations from "elementary.py" in the IPCC repository when needed. Therefore this
file remains empty.
"""

import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_co2_cement(year=2010, region="BG", product="portland", uncertainty="def"):
    """Template calculation sequence for tier 1 method.

    CO2 Emissions for cement production.
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
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "cement_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="ckd_correc_fact", table="ckd_correc_fact", coords=[year, region]
    )

    value = seq.elementary.ef_clc(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        ckd_correc_fact=seq.step.ckd_correc_fact.value,
    )

    seq.store_result(name="ef_clc", value=value, unit="t/t", year=year)

    seq.read_parameter(
        name="m_c",
        table="m_c",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )

    seq.read_parameter(
        name="c_cl",
        table="c_cl",
        coords=[year, region, product],
        lci_flag=f"transf_coeff|product|clinker|{product}",
    )

    seq.read_parameter(name="im_cl", table="im_cl", coords=[year, region, product])

    seq.read_parameter(name="ex_cl", table="ex_cl", coords=[year, region, product])

    value = seq.elementary.co2_emissions_tier1_(
        m_c=seq.step.m_c.value,
        c_cl=seq.step.c_cl.value,
        im_cl=seq.step.im_cl.value,
        ex_cl=seq.step.ex_cl.value,
        ef_clc=seq.step.ef_clc.value,
    )

    seq.store_result(
        name="co2_emissions_tier1_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier2_co2_cement_simple(
    year=2010, region="BG", product="portland", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for cement production.
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
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "cement_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="cao_non_carbo_frac",
        table="cao_non_carbo_frac",
        coords=[year, region, product],
    )

    value = seq.elementary.ef_cl(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_non_carbo_frac=seq.step.cao_non_carbo_frac.value,
    )

    seq.store_result(name="ef_cl", value=value, unit="t/t", year=year)

    seq.read_parameter(  # also equation 2.5 possible, but more data required
        name="ckd_correc_fact", table="ckd_correc_fact", coords=[year, region]
    )

    seq.read_parameter(
        name="m_cl",
        table="m_cl",
        coords=[year, region, product],
        lci_flag="use|product|clinker",
    )

    value = seq.elementary.co2_emissions_tier2_(
        m_cl=seq.step.m_cl.value,
        ef_cl=seq.step.ef_cl.value,
        cf_ckd=seq.step.ckd_correc_fact.value,
    )

    seq.store_result(
        name="co2_emissions_tier2_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier2_co2_cement_extended(
    year=2010, region="BG", product="portland", uncertainty="def"
):
    """Template calculation sequence for tier 2 method.

    CO2 Emissions for cement production.
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
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "cement_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cao_in_clinker", table="cao_in_clinker", coords=[year, region]
    )

    seq.read_parameter(
        name="cao_non_carbo_frac",
        table="cao_non_carbo_frac",
        coords=[year, region, product],
    )

    value = seq.elementary.ef_cl(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_non_carbo_frac=seq.step.cao_non_carbo_frac.value,
    )

    seq.store_result(name="ef_cl", value=value, unit="t/t", year=year)

    seq.read_parameter(
        name="m_cl",
        table="m_cl",
        coords=[year, region, product],
        lci_flag="use|product|clinker",
    )

    # loop (sum over all carbonate types)
    d = seq.get_dimension_levels(year, region, product, uncert="def", table="c_d")
    value = 0.0
    for carbonate_type in d:

        seq.read_parameter(
            name=f"m_d_xxx_{carbonate_type}_xxx",
            table="m_d",
            coords=[year, region, product, carbonate_type],
        )

        seq.read_parameter(
            name=f"c_d_xxx_{carbonate_type}_xxx",
            table="c_d",
            coords=[year, region, product, carbonate_type],
        )
        seq.read_parameter(
            name=f"f_d_xxx_{carbonate_type}_xxx",
            table="f_d",
            coords=[year, region, product, carbonate_type],
        )
        seq.read_parameter(
            name=f"ef_c_xxx_{carbonate_type}_xxx",
            table="ef_c",
            coords=[year, region, carbonate_type],
        )
        value += seq.elementary.cf_ckd(
            m_d=getattr(getattr(seq.step, f"m_d_xxx_{carbonate_type}_xxx"), "value"),
            m_cl=seq.step.m_cl.value,
            c_d=getattr(getattr(seq.step, f"c_d_xxx_{carbonate_type}_xxx"), "value"),
            f_d=getattr(getattr(seq.step, f"f_d_xxx_{carbonate_type}_xxx"), "value"),
            ef_c=getattr(getattr(seq.step, f"ef_c_xxx_{carbonate_type}_xxx"), "value"),
            ef_cl=seq.step.ef_cl.value,
        )

    seq.store_result(name="cf_ckd", value=value, unit="t/t", year=year)

    seq.read_parameter(name="m_cl", table="m_cl", coords=[year, region, product])

    value = seq.elementary.co2_emissions_tier2_(
        m_cl=seq.step.m_cl.value,
        ef_cl=seq.step.ef_cl.value,
        cf_ckd=seq.step.cf_ckd.value,
    )

    seq.store_result(
        name="co2_emissions_tier2_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step


def tier3_co2_cement(year=2010, region="BG", product="portland", uncertainty="def"):
    """Template calculation sequence for tier 3 method.

    CO2 Emissions for cement production.
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
        type of cement
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Mineral sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "cement_production"
    seq.store_signature(meta_dict)

    # loop sum over all carbonates i
    carb = seq.get_dimension_levels(year, region, product, uncert="def", table="m_i")
    value = 0.0
    for carbonate_type in carb:
        seq.read_parameter(
            name=f"ef_c_xxx_{carbonate_type}_xxx",
            table="ef_c",
            coords=[year, region, carbonate_type],
        )

        seq.read_parameter(
            name=f"m_i_xxx_{carbonate_type}_xxx",
            table="m_i",
            coords=[year, region, product, carbonate_type],
            lci_flag=f"use|product|{carbonate_type}",
        )

        seq.read_parameter(
            name=f"f_i_xxx_{carbonate_type}_xxx",
            table="f_i",
            coords=[year, region, product, carbonate_type],
        )
        value += seq.elementary.co2_emissions_tier3_carb(
            ef_i=getattr(getattr(seq.step, f"ef_c_xxx_{carbonate_type}_xxx"), "value"),
            m_i=getattr(getattr(seq.step, f"m_i_xxx_{carbonate_type}_xxx"), "value"),
            f_i=getattr(getattr(seq.step, f"f_i_xxx_{carbonate_type}_xxx"), "value"),
        )
    seq.store_result(
        name="co2_emissions_tier3_carb", value=value, unit="t/yr", year=year
    )

    # loop over all carbonates that are not calcined
    not_calcined = seq.get_dimension_levels(
        year, region, product, uncert="def", table="m_k"
    )
    value = 0.0
    for carbonate_type in not_calcined:
        seq.read_parameter(
            name=f"m_d_xxx_{carbonate_type}_xxx",
            table="m_d",
            coords=[year, region, product, carbonate_type],
        )

        seq.read_parameter(
            name=f"c_d_xxx_{carbonate_type}_xxx",
            table="c_d",
            coords=[year, region, product, carbonate_type],
        )

        seq.read_parameter(
            name=f"f_d_xxx_{carbonate_type}_xxx",
            table="f_d",
            coords=[year, region, product, carbonate_type],
        )

        seq.read_parameter(
            name=f"ef_d_xxx_{carbonate_type}_xxx",
            table="ef_d",
            coords=[year, region, product, carbonate_type],
        )
        value += seq.elementary.co2_emissions_tier3_kiln(
            m_d=getattr(getattr(seq.step, f"m_d_xxx_{carbonate_type}_xxx"), "value"),
            c_d=getattr(getattr(seq.step, f"c_d_xxx_{carbonate_type}_xxx"), "value"),
            f_d=getattr(getattr(seq.step, f"f_d_xxx_{carbonate_type}_xxx"), "value"),
            ef_d=getattr(getattr(seq.step, f"ef_d_xxx_{carbonate_type}_xxx"), "value"),
        )
    seq.store_result(
        name="co2_emissions_tier3_kiln", value=value, unit="t/yr", year=year
    )

    # loop over all other material types
    other = seq.get_dimension_levels(year, region, product, uncert="def", table="m_k")
    value = 0.0
    for other_material_type in other:
        seq.read_parameter(
            name=f"m_k_xxx_{other_material_type}_xxx",
            table="m_k",
            coords=[year, region, product, other_material_type],
        )

        seq.read_parameter(
            name=f"x_k_xxx_{other_material_type}_xxx",
            table="x_k",
            coords=[year, region, product, other_material_type],
        )

        seq.read_parameter(
            name=f"ef_k_xxx_{other_material_type}_xxx",
            table="ef_k",
            coords=[year, region, product, other_material_type],
        )

        value += seq.elementary.co2_emissions_tier3_other(
            m_k=getattr(
                getattr(seq.step, f"m_k_xxx_{other_material_type}_xxx"), "value"
            ),
            x_k=getattr(
                getattr(seq.step, f"x_k_xxx_{other_material_type}_xxx"), "value"
            ),
            ef_k=getattr(
                getattr(seq.step, f"ef_k_xxx_{other_material_type}_xxx"), "value"
            ),
        )
    seq.store_result(
        name="co2_emissions_tier3_other", value=value, unit="t/yr", year=year
    )

    value = seq.elementary.co2_emissions_tier3_(
        carb=seq.step.co2_emissions_tier3_carb.value,
        kiln=seq.step.co2_emissions_tier3_kiln.value,
        other=seq.step.co2_emissions_tier3_other.value,
    )

    seq.store_result(
        name="co2_emissions_tier3_",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Mineral sequence finalized.")
    return seq.step
