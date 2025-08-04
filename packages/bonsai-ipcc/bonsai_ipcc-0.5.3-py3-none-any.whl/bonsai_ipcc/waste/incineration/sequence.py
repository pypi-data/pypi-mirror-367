"""
Sequences to determine GHG emissions from incineration.

Decision tree for CO2:
    - tier 1: default data to quantify waste generation, composition and management practice
              (requirement: incineration or open burning is not a key category)
    - tier 2a: country-specific data to quantify waste generation and composition
               default data for emission factors and waste management
    - tier 2b: country-specific data for waste generation, composition and management practice
    - tier 3: plant- or management-specific data

Decision tree for CH4 and N2O:
    - tier 1: estimate total amount of wastes incinerated or open-burned and use default emission factors
              (requirement: incineration or open burning is not a key category)
    - tier 2: country-specific data by waste type, technology and management practice
    - tier 3: plant- or management-specific data
"""


import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_co2(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 1 method CO2 Emissions.

    Default data to quantify waste generation, composition and management practice
    (requirement: incineration or open burning is not a key category)

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")

    meta_dict = locals()

    seq.store_signature(meta_dict)

    if product.startswith("msw_"):
        if activity != "open_burn":
            seq.read_parameter(
                name="urb_population", table="urb_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_frac_to_incin",
                table="msw_frac_to_incin",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = (
                seq.elementary.msw_to_incin(
                    urb_population=seq.step.urb_population.value,
                    msw_gen_rate=seq.step.msw_gen_rate.value,
                    msw_frac_to_incin=seq.step.msw_frac_to_incin.value,
                    msw_type_frac=seq.step.msw_type_frac.value,
                )
                / 1000
            )  # conversion from tonnes to Gg

            seq.store_result(
                name="msw_to_incin",
                value=value,
                unit="Gg/year",
                year=year,
            )

            seq.read_parameter(
                name="incintype_frac",
                table="incintype_frac",
                coords=[year, region, activity],
            )

            value = seq.elementary.waste_to_technology(
                waste=seq.step.msw_to_incin.value,
                technologyrate=seq.step.incintype_frac.value,
            )
            seq.store_result(
                name="waste_to_technology",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

        else:
            seq.read_parameter(
                name="total_population", table="total_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="p_frac",
                table="p_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="b_frac",
                table="b_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = seq.elementary.msw_open_burned(
                total_population=seq.step.total_population.value,
                p_frac=seq.step.p_frac.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                b_frac=seq.step.b_frac.value,
                msw_type_frac=seq.step.msw_type_frac.value,
            )

            seq.store_result(
                name="waste_to_technology",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

    else:
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="isw_total", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        seq.read_parameter(
            name="isw_type_frac", table="isw_type_frac", coords=[year, region, product]
        )

        value = seq.elementary.isw_to_incin(
            isw_total=seq.step.isw_total.value,
            isw_type_frac=seq.step.isw_type_frac.value,
            isw_frac_to_incin=seq.step.isw_frac_to_incin.value,
        )

        seq.store_result(name="isw_to_incin", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="incintype_frac",
            table="incintype_frac",
            coords=[year, region, activity],
        )

        value = seq.elementary.waste_to_technology(
            waste=seq.step.isw_to_incin.value,
            technologyrate=seq.step.incintype_frac.value,
        )
        seq.store_result(
            name="waste_to_technology",
            value=value,
            unit="Gg/year",
            year=year,
            lci_flag=f"use|waste|{product}",
        )

    seq.read_parameter(name="dm", table="dm", coords=[year, region, product])

    seq.read_parameter(name="cf", table="cf", coords=[year, region, product])

    seq.read_parameter(name="fcf", table="fcf", coords=[region, product, activity])

    seq.read_parameter(name="of", table="of", coords=[region, product, activity])

    value = seq.elementary.co2_emissions(
        waste=seq.step.waste_to_technology.value,
        dm=seq.step.dm.value,
        cf=seq.step.cf.value,
        fcf=seq.step.fcf.value,
        of=seq.step.of.value,
    )

    seq.store_result(
        name="co2_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier1_ch4(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 1 method CH4 Emissions.

    Default data to quantify waste generation, composition and management practice
    (requirement: incineration or open burning is not a key category)

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    if product.startswith("msw_"):
        if activity != "open_burn":
            seq.read_parameter(
                name="urb_population", table="urb_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_frac_to_incin",
                table="msw_frac_to_incin",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = (
                seq.elementary.msw_to_incin(
                    urb_population=seq.step.urb_population.value,
                    msw_gen_rate=seq.step.msw_gen_rate.value,
                    msw_frac_to_incin=seq.step.msw_frac_to_incin.value,
                    msw_type_frac=seq.step.msw_type_frac.value,
                )
                / 1000
            )  # conversion from tonnes to gg

            seq.store_result(
                name="sw_per_treat",
                value=value,
                unit="Gg/year",
                year=year,
            )

            seq.read_parameter(
                name="incintype_frac",
                table="incintype_frac",
                coords=[year, region, activity],
            )

            value = seq.elementary.waste_to_technology(
                waste=seq.step.sw_per_treat.value,
                technologyrate=seq.step.incintype_frac.value,
            )
            seq.store_result(
                name="sw_per_tech",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

        else:
            seq.read_parameter(
                name="total_population", table="total_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="p_frac",
                table="p_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="b_frac",
                table="b_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = seq.elementary.msw_open_burned(
                total_population=seq.step.total_population.value,
                p_frac=seq.step.p_frac.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                b_frac=seq.step.b_frac.value,
                msw_type_frac=seq.step.msw_type_frac.value,
            )

            seq.store_result(
                name="sw_per_tech",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

    else:
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="isw_total", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        seq.read_parameter(
            name="isw_type_frac", table="isw_type_frac", coords=[year, region, product]
        )

        value = seq.elementary.isw_to_incin(
            isw_total=seq.step.isw_total.value,
            isw_type_frac=seq.step.isw_type_frac.value,
            isw_frac_to_incin=seq.step.isw_frac_to_incin.value,
        )

        seq.store_result(name="isw_to_incin", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="incintype_frac",
            table="incintype_frac",
            coords=[year, region, activity],
        )

        value = seq.elementary.waste_to_technology(
            waste=seq.step.isw_to_incin.value,
            technologyrate=seq.step.incintype_frac.value,
        )
        seq.store_result(
            name="sw_per_tech",
            value=value,
            unit="Gg/year",
            year=year,
            lci_flag=f"use|waste|{product}",
        )

    seq.read_parameter(
        name="ef_ch4", table="ef_ch4", coords=[region, product, activity]
    )

    value = seq.elementary.ch4_emissions(
        waste=seq.step.sw_per_tech.value,
        ef_ch4=seq.step.ef_ch4.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier1_n2o(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Default data to quantify waste generation, composition and management practice
    (requirement: incineration or open burning is not a key category)

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    if product.startswith("msw_"):
        if activity != "open_burn":
            seq.read_parameter(
                name="urb_population", table="urb_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_frac_to_incin",
                table="msw_frac_to_incin",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = (
                seq.elementary.msw_to_incin(
                    urb_population=seq.step.urb_population.value,
                    msw_gen_rate=seq.step.msw_gen_rate.value,
                    msw_frac_to_incin=seq.step.msw_frac_to_incin.value,
                    msw_type_frac=seq.step.msw_type_frac.value,
                )
                / 1000
            )  # conversion from tonnes to gg

            seq.store_result(
                name="sw_per_treat",
                value=value,
                unit="Gg/year",
                year=year,
            )

            seq.read_parameter(
                name="incintype_frac",
                table="incintype_frac",
                coords=[year, region, activity],
            )

            value = seq.elementary.waste_to_technology(
                waste=seq.step.sw_per_treat.value,
                technologyrate=seq.step.incintype_frac.value,
            )
            seq.store_result(
                name="sw_per_tech",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

        else:
            seq.read_parameter(
                name="total_population", table="total_population", coords=[year, region]
            )

            seq.read_parameter(
                name="msw_gen_rate", table="msw_gen_rate", coords=[year, region]
            )

            seq.read_parameter(
                name="p_frac",
                table="p_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="b_frac",
                table="b_frac",
                coords=[year, region],
            )

            seq.read_parameter(
                name="msw_type_frac",
                table="msw_type_frac",
                coords=[year, region, product],
            )

            value = seq.elementary.msw_open_burned(
                total_population=seq.step.total_population.value,
                p_frac=seq.step.p_frac.value,
                msw_gen_rate=seq.step.msw_gen_rate.value,
                b_frac=seq.step.b_frac.value,
                msw_type_frac=seq.step.msw_type_frac.value,
            )

            seq.store_result(
                name="sw_per_tech",
                value=value,
                unit="Gg/year",
                year=year,
                lci_flag=f"use|waste|{product}",
            )

    else:
        seq.read_parameter(name="gdp", table="gdp", coords=[year, region])

        seq.read_parameter(
            name="isw_gen_rate", table="isw_gen_rate", coords=[year, region]
        )

        value = seq.elementary.isw_total(
            gdp=seq.step.gdp.value, waste_gen_rate=seq.step.isw_gen_rate.value
        )
        seq.store_result(name="isw_total", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        seq.read_parameter(
            name="isw_type_frac", table="isw_type_frac", coords=[year, region, product]
        )

        value = seq.elementary.isw_to_incin(
            isw_total=seq.step.isw_total.value,
            isw_type_frac=seq.step.isw_type_frac.value,
            isw_frac_to_incin=seq.step.isw_frac_to_incin.value,
        )

        seq.store_result(name="isw_to_incin", value=value, unit="Gg/year", year=year)

        seq.read_parameter(
            name="incintype_frac",
            table="incintype_frac",
            coords=[year, region, activity],
        )

        value = seq.elementary.waste_to_technology(
            waste=seq.step.isw_to_incin.value,
            technologyrate=seq.step.incintype_frac.value,
        )
        seq.store_result(
            name="sw_per_tech",
            value=value,
            unit="Gg/year",
            year=year,
            lci_flag=f"use|waste|{product}",
        )

    seq.read_parameter(
        name="ef_n2o", table="ef_n2o", coords=[region, product, activity]
    )

    value = seq.elementary.n2o_emissions(
        waste=seq.step.sw_per_tech.value,
        ef_n2o=seq.step.ef_n2o.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier2a_co2(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 2a method CO2 Emissions.

    Country-specific data to quantify waste generation and composition
    Default data for emission factors and waste management

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    if product.startswith("msw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="msw_frac_to_incin", table="msw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    elif product.startswith("isw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="incintype_frac",
        table="incin_ob_type_frac",
        coords=[year, region, activity],
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.sw_per_treat.value, technologyrate=seq.step.incintype_frac.value
    )
    seq.store_result(
        name="sw_per_tech",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(name="dm", table="dm", coords=[year, region, product])

    seq.read_parameter(name="cf", table="cf", coords=[year, region, product])

    seq.read_parameter(name="fcf", table="fcf", coords=[region, product, activity])

    seq.read_parameter(name="of", table="of", coords=[region, product, activity])

    value = seq.elementary.co2_emissions(
        waste=seq.step.sw_per_tech.value,
        dm=seq.step.dm.value,
        cf=seq.step.cf.value,
        fcf=seq.step.fcf.value,
        of=seq.step.of.value,
    )

    seq.store_result(
        name="co2_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier2b_co2(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 2b method CO2 Emissions.

    Country-specific data for waste generation, composition and management practice

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    if product.startswith("msw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="msw_frac_to_incin", table="msw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    elif product.startswith("isw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="incintype_frac",
        table="incin_ob_type_frac",
        coords=[year, region, activity],
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.sw_per_treat.value, technologyrate=seq.step.incintype_frac.value
    )
    seq.store_result(
        name="sw_per_tech",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    logger.info("paramter 'dm' needs to be country-specific")
    seq.read_parameter(name="dm", table="dm", coords=[year, region, product])

    logger.info("paramter 'cf' needs to be country-specific")
    seq.read_parameter(name="cf", table="cf", coords=[year, region, product])

    seq.read_parameter(name="fcf", table="fcf", coords=[region, product, activity])

    seq.read_parameter(name="of", table="of", coords=[region, product, activity])

    value = seq.elementary.co2_emissions(
        waste=seq.step.sw_per_tech.value,
        dm=seq.step.dm.value,
        cf=seq.step.cf.value,
        fcf=seq.step.fcf.value,
        of=seq.step.of.value,
    )

    seq.store_result(
        name="co2_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier3_co2(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 3 method CO2 Emissions.

    Plant- or management-specific data

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)

    logger.info("paramter 'SW' needs to be plant-specific")
    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech_incin",
        coords=[year, region, product, activity],
        lci_flag=f"use|waste|{product}",
    )

    logger.info("paramter 'dm' needs to be plant-specific in dim 'region'")
    seq.read_parameter(name="dm", table="dm", coords=[year, region, product])

    logger.info("paramter 'cf' needs to be plant-specific in dim 'region'")
    seq.read_parameter(name="cf", table="cf", coords=[year, region, product])

    logger.info("paramter 'fcf' needs to be plant-specific in dim 'region'")
    seq.read_parameter(name="fcf", table="fcf", coords=[region, product, activity])

    logger.info("paramter 'of' needs to be plant-specific")
    seq.read_parameter(name="of", table="of", coords=[region, product, activity])

    value = seq.elementary.co2_emissions(
        waste=seq.step.sw_per_tech.value,
        dm=seq.step.dm.value,
        cf=seq.step.cf.value,
        fcf=seq.step.fcf.value,
        of=seq.step.of.value,
    )

    seq.store_result(
        name="co2_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CO2",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier2_ch4(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 2 method CH4 Emissions.

    Country-specific data to quantify waste generation and composition
    Default data for emission factors and waste management

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)
    logger.info("For tier 2 the parameters should be region-specific.")

    if product.startswith("msw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="msw_frac_to_incin", table="msw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    elif product.startswith("isw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="incintype_frac",
        table="incin_ob_type_frac",
        coords=[year, region, activity],
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.sw_per_treat.value, technologyrate=seq.step.incintype_frac.value
    )
    seq.store_result(
        name="sw_per_tech",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(
        name="ef_ch4", table="ef_ch4", coords=[region, product, activity]
    )

    value = seq.elementary.ch4_emissions(
        waste=seq.step.sw_per_tech.value,
        ef_ch4=seq.step.ef_ch4.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier2_n2o(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 2 method N2O Emissions.

    Country-specific data to quantify waste generation and composition
    Default data for emission factors and waste management

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)
    logger.info("For tier 2 the parameters should be region-specific.")
    if product.startswith("msw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="msw_frac_to_incin", table="msw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.msw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    elif product.startswith("isw_"):
        seq.read_parameter(name="sw", table="sw", coords=[year, region, product])

        seq.read_parameter(
            name="isw_frac_to_incin", table="isw_frac_to_incin", coords=[year, region]
        )

        value = seq.elementary.waste_to_treatment(
            waste=seq.step.sw.value, treatmentrate=seq.step.isw_frac_to_incin.value
        )
        seq.store_result(name="sw_per_treat", value=value, unit="Gg/year", year=year)

    seq.read_parameter(
        name="incintype_frac",
        table="incin_ob_type_frac",
        coords=[year, region, activity],
    )

    value = seq.elementary.waste_to_technology(
        waste=seq.step.sw_per_treat.value, technologyrate=seq.step.incintype_frac.value
    )
    seq.store_result(
        name="sw_per_tech",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(
        name="ef_n2o", table="ef_n2o", coords=[region, product, activity]
    )

    value = seq.elementary.n2o_emissions(
        waste=seq.step.sw_per_tech.value,
        ef_n2o=seq.step.ef_n2o.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier3_n2o(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 3 method N2O Emissions.

    Plant- or management-specific data

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)
    logger.info("paramter 'SW' needs to be plant-specific")
    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech",
        coords=[year, region, product, activity],
        lci_flag=f"use|waste|{product}",
    )

    seq.read_parameter(name="ec", table="ec", coords=[year, region, product, activity])

    seq.read_parameter(
        name="fgv", table="fgv", coords=[year, region, product, activity]
    )

    value = seq.elementary.n2o_emissions_tier3(
        iw=seq.step.sw_per_tech.value,
        ec=seq.step.ec.value,
        fgv=seq.step.fgv.value,
    )

    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step


def tier3_ch4(
    year=2010,
    region="BG",
    product="msw_food",
    activity="open_burn",
    uncertainty="def",
):
    """Tier 3 method CH4 Emissions.

    Plant- or management-specific data

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        Fraction of solid waste.
    activity : str
        Type of waste incineration.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Incineration sequence started --->")
    meta_dict = locals()

    seq.store_signature(meta_dict)
    logger.info("paramter 'SW' needs to be plant-specific")
    seq.read_parameter(
        name="sw_per_tech",
        table="sw_per_tech",
        coords=[year, region, product, activity],
        lci_flag=f"use|waste|{product}",
    )

    logger.info("paramter 'ef_ch4' needs to be country-specific or plant-specific")
    seq.read_parameter(
        name="ef_ch4", table="ef_ch4", coords=[region, product, activity]
    )

    value = seq.elementary.ch4_emissions(
        waste=seq.step.sw_per_tech.value,
        ef_ch4=seq.step.ef_ch4.value,
    )

    seq.store_result(
        name="ch4_emissions",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> Incineration sequence finalized.")
    return seq.step
