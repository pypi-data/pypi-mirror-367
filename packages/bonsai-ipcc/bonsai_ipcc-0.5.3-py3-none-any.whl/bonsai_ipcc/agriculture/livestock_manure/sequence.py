"""
Sequences to determine GHG emissions from manure treatment.


"""


import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_n2o(
    year=2010,
    region="NZ",
    animal="cattle-dairy",
    activity="lagoon",
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Emissions from manure treatment.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    animal : str
        animal category.
    activity : str
        Type of manure treatmant.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = f"manure_{animal}"
    seq.store_signature(meta_dict)

    # nex:

    seq.read_parameter(
        name="weight",
        table="weight",
        coords=[year, region, animal],
    )

    seq.read_parameter(
        name="n_rate",
        table="n_rate",
        coords=[year, region, animal],
    )

    value = seq.elementary.nex_tier1_(
        n_rate=seq.step.n_rate.value,
        tam=seq.step.weight.value,
    )

    seq.store_result(
        name="nex_tier1_",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    # n2o_direct_mm:

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, animal],
    )

    seq.read_parameter(
        name="ms",
        table="ms",
        coords=[year, region, animal, activity],
    )

    seq.read_parameter(
        name="ef3",
        table="ef3",
        coords=[activity],
    )

    value = seq.elementary.n2o_direct_mm(
        n=seq.step.n.value,
        nex=seq.step.nex_tier1_.value,
        ms=seq.step.ms.value,
        ef=seq.step.ef3.value,
    )

    seq.store_result(
        name="n2o_direct_mm",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_gas",
        table="frac_gas",
        coords=[year, region, animal, activity],
    )
    value = seq.elementary.n_volatilization(
        n=seq.step.n.value,
        nex=seq.step.nex_tier1_.value,
        awms=seq.step.ms.value,
        frac_gas=seq.step.frac_gas.value,
    )
    seq.store_result(
        name="n_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_leach",
        table="frac_leach",
        coords=[year, region, animal, activity],
    )
    value = seq.elementary.n_leaching(
        n=seq.step.n.value,
        nex=seq.step.nex_tier1_.value,
        awms=seq.step.ms.value,
        frac_leach=seq.step.frac_leach.value,
    )
    seq.store_result(
        name="n_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="ef4",
        table="ef4",
        coords=[seq.step.moisture_regime.value],
    )
    value = seq.elementary.n2o_g(
        n_volatilization=seq.step.n_volatilization.value,
        ef4=seq.step.ef4.value,
    )
    seq.store_result(
        name="n2o_g",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef5",
        table="ef5",
        coords=[],
    )
    value = seq.elementary.n2o_l(
        n_leaching=seq.step.n_leaching.value,
        ef5=seq.step.ef5.value,
    )
    seq.store_result(
        name="n2o_l",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o_emissions(
        seq.step.n2o_g.value, seq.step.n2o_l.value, seq.step.n2o_direct_mm.value
    )
    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_n2o(
    year=2019,
    region="DE",
    animal="cattle-dairy",
    feeding_situation="stall",
    diet_type="forage-high",
    activity="solid-storage",
    uncertainty="def",
):
    """Tier 2 method N2O Emissions.

    Emission from manure treatment.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    animal : str
        animal category.
    feeding_situation : str
        feeding situation of the animal
    diet_type : str
        diet type of the animal
    activity : str
        Type of manure treatment.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = f"manure_{animal}"
    seq.store_signature(meta_dict)

    seq.read_parameter(name="cf_i", table="cf_i", coords=[animal])

    seq.read_parameter(name="weight", table="weight", coords=[year, region, animal])

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if animal.startswith(("cattle", "buffalo", "sheep", "goat")):
        if animal.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a_cattle", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a_cattle.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="nea_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="weight", table="weight", coords=[year, region, animal]
            )

            seq.read_parameter(name="c", table="c", coords=[animal])

            seq.read_parameter(name="mw", table="mw", coords=[year, region, animal])

            seq.read_parameter(name="wg", table="wg", coords=[year, region, animal])

            value = seq.elementary.neg_cattle_(
                bw=seq.step.weight.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="neg_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="milk", table="milk", coords=[year, region, animal])

            seq.read_parameter(name="fat", table="fat", coords=[year, region, animal])

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="nel_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, animal]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="c_pregnancy", table="c_pregnancy", coords=[animal])

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, animal],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="de", table="de", coords=[year, region, animal])
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in animal and "calve" in animal:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.weight.value
                )
                seq.store_result(
                    name="dmi_calve_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_calve_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in animal and "growing" in animal:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.weight.value
                )
                seq.store_result(
                    name="dmi_growing_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_growing_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )

            elif "cattle" in animal and "bull" in animal:
                value = seq.elementary.dmi_steer_(bw=seq.step.weight.value)
                seq.store_result(
                    name="dmi_steer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_steer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )

            elif "cattle" in animal and "heifer" in animal:
                value = seq.elementary.dmi_heifer_(bw=seq.step.weight.value)
                seq.store_result(
                    name="dmi_heifer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_heifer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )

            elif "cattle" in animal and "dairy" in animal:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.weight.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi_lactating_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_lactating_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )

            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.nea_cattle_.value,
                    ne_l=seq.step.nel_cattle_.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.neg_cattle_.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="cattletier2_",
                )

        seq.read_parameter(name="cp", table="cp", coords=[year, region, animal])

        value = seq.elementary.nintake_cattletier2_(
            ge=seq.step.ge.value, cp=seq.step.cp.value
        )
        seq.store_result(
            name="nintake_cattletier2_",
            value=value,
            unit="kg/piece/day",
            year=year,
        )

        # TODO: use equations n_retention instead of parameter n_retention_frac?
        seq.read_parameter(
            name="n_retention_frac",
            table="n_retention_frac",
            coords=[year, region, animal],
        )

        value = seq.elementary.nex_atier2_(
            n_intake=seq.step.nintake_cattletier2_.value,
            n_retention_frac=seq.step.n_retention_frac.value,
        )
        seq.store_result(
            name="nex_atier2_",
            value=value,
            unit="kg/piece/year",
            year=year,
        )

        seq.read_parameter(name="n", table="n", coords=[year, region, animal])
        seq.read_parameter(
            name="ms", table="ms", coords=[year, region, animal, activity]
        )
        seq.read_parameter(name="ef", table="ef3", coords=[activity])
        value = seq.elementary.n2o_direct_mm(
            n=seq.step.n.value,
            nex=seq.step.nex_atier2_.value,
            ms=seq.step.ms.value,
            ef=seq.step.ef.value,
        )
        seq.store_result(
            name="n2o_direct_mm",
            value=value,
            unit="kg/year",
            year=year,
        )

    elif animal.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="nea_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="bw_i", table="bw_i", coords=[year, region, animal])

        seq.read_parameter(name="bw_f", table="bw_f", coords=[year, region, animal])

        seq.read_parameter(name="a", table="a", coords=[animal])

        seq.read_parameter(name="b", table="b", coords=[animal])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="neg_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(name="milk", table="milk", coords=[year, region, animal])

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, animal]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="nel_asheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, animal]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, animal]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="c_pregnancy", table="c_pregnancy", coords=[animal])

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, animal],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, animal])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.nea_sheep_.value,
            ne_l=seq.step.nel_asheep_.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.neg_sheep_.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
            parameter_flag="sheeptier2_",
        )

        seq.read_parameter(name="cp", table="cp", coords=[year, region, animal])

        value = seq.elementary.nintake_cattletier2_(
            ge=seq.step.ge.value, cp=seq.step.cp.value
        )
        seq.store_result(
            name="nintake_cattletier2_",
            value=value,
            unit="kg/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="n_retention_frac",
            table="n_retention_frac",
            coords=[year, region, animal],
        )

        value = seq.elementary.nex_atier2_(
            n_intake=seq.step.nintake_cattletier2_.value,
            n_retention_frac=seq.step.n_retention_frac.value,
        )
        seq.store_result(
            name="nex_atier2_",
            value=value,
            unit="kg/piece/year",
            year=year,
        )

        seq.read_parameter(name="n", table="n", coords=[year, region, animal])
        seq.read_parameter(
            name="ms", table="ms", coords=[year, region, animal, activity]
        )
        seq.read_parameter(name="ef", table="ef3", coords=[activity])
        value = seq.elementary.n2o_direct_mm(
            n=seq.step.n.value,
            nex=seq.step.nex_atier2_.value,
            ms=seq.step.ms.value,
            ef=seq.step.ef.value,
        )
        seq.store_result(
            name="n2o_direct_mm",
            value=value,
            unit="kg/year",
            year=year,
        )

    seq.read_parameter(
        name="frac_gas",
        table="frac_gas",
        coords=[year, region, animal, activity],
    )
    value = seq.elementary.n_volatilization(
        n=seq.step.n.value,
        nex=seq.step.nex_atier2_.value,
        awms=seq.step.ms.value,
        frac_gas=seq.step.frac_gas.value,
    )
    seq.store_result(
        name="n_volatilization",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="frac_leach",
        table="frac_leach",
        coords=[year, region, animal, activity],
    )
    value = seq.elementary.n_leaching(
        n=seq.step.n.value,
        nex=seq.step.nex_atier2_.value,
        awms=seq.step.ms.value,
        frac_leach=seq.step.frac_leach.value,
    )
    seq.store_result(
        name="n_leaching",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(name="moisture_regime", table="moisture_regime", coords=[region])

    seq.read_parameter(
        name="ef4",
        table="ef4",
        coords=[seq.step.moisture_regime.value],
    )
    value = seq.elementary.n2o_g(
        n_volatilization=seq.step.n_volatilization.value,
        ef4=seq.step.ef4.value,
    )
    seq.store_result(
        name="n2o_g",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef5",
        table="ef5",
        coords=[],
    )
    value = seq.elementary.n2o_l(
        n_leaching=seq.step.n_leaching.value,
        ef5=seq.step.ef5.value,
    )
    seq.store_result(
        name="n2o_l",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o_emissions(seq.step.n2o_g.value, seq.step.n2o_l.value)
    seq.store_result(
        name="n2o_emissions",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier1_ch4_enteric(
    year=2010,
    region="DE",
    product="cattle-dairy",
    uncertainty="def",
):
    """Tier 1 method CH4 Emissions.

    Enteric emissions from animals.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        animal category.
    feeding_situation : str
        feeding situation of the animal
    diet_type : str
        diet type of the animal
    activity : str
        Type of manure treatment.
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "animal_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="ef",
        table="ef",
        coords=[year, region, product],
    )
    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )
    value = seq.elementary.e(
        n=seq.step.n.value,
        ef=seq.step.ef.value,
    )
    seq.store_result(
        name="e", value=value, unit="Gg/year", year=year, lci_flag="emission|air|CH4"
    )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_ch4_enteric(
    year=2010,
    region="DE",
    product="cattle-dairy",
    feeding_situation="stall",
    diet_type="undefined",
    uncertainty="def",
):
    """
    diet_type : str
        optional, required for growing cattle and calve
    feeding_situation : str
        optional, required for cattle and buffalo
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "animal_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(name="cf_i", table="cf_i", coords=[product])

    seq.read_parameter(name="weight", table="weight", coords=[year, region, product])

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if product.startswith(("cattle", "buffalo", "sheep", "goat")):
        if product.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="nea_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="bw", table="weight", coords=[year, region, product]
            )

            seq.read_parameter(name="c", table="c", coords=[product])
            logger.info("mw")
            seq.read_parameter(name="mw", table="mw", coords=[year, region, product])

            seq.read_parameter(name="wg", table="wg", coords=[year, region, product])

            value = seq.elementary.neg_cattle_(
                bw=seq.step.bw.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="neg_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="milk", table="milk", coords=[year, region, product]
            )

            seq.read_parameter(name="fat", table="fat", coords=[year, region, product])

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="nel_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, product]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="c_pregnancy", table="c_pregnancy", coords=[product]
            )

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, product],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="de", table="de", coords=[year, region, product])
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in product and "calve" in product:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi_calve_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_calve_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in product and "growing" in product:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi_growing_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_growing_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in product and "bull" in product:

                value = seq.elementary.dmi_steer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi_steer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_steer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in product and "heifer" in product:
                value = seq.elementary.dmi_heifer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi_heifer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_heifer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in product and "dairy" in product:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.bw.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi_lactating_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_lactating_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                )
            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.nea_cattle_.value,
                    ne_l=seq.step.nel_cattle_.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.neg_cattle_.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="cattletier2_",
                )
    elif product.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="nea_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="bw_i", table="bw_i", coords=[year, region, product])

        seq.read_parameter(name="bw_f", table="bw_f", coords=[year, region, product])

        seq.read_parameter(name="a", table="a", coords=[product])

        seq.read_parameter(name="b", table="b", coords=[product])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="neg_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(name="milk", table="milk", coords=[year, region, product])

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, product]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="nel_asheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, product]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, product]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="c_pregnancy", table="c_pregnancy", coords=[product])

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, product],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, product])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.nea_sheep_.value,
            ne_l=seq.step.nel_asheep_.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.neg_sheep_.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
            parameter_flag="sheeptier2_",
        )

    seq.read_parameter(
        name="ym",
        table="ym",
        coords=[year, region, product, diet_type],
    )
    value = seq.elementary.ef_atier2_(
        ge=seq.step.ge.value,
        ym=seq.step.ym.value,
    )
    seq.store_result(
        name="ef_atier2_",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )
    value = seq.elementary.e(
        n=seq.step.n.value,
        ef=seq.step.ef_atier2_.value,
    )
    seq.store_result(
        name="e",
        value=value,
        unit="Gg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier1_ch4_manure(
    year=2019,
    region="DE",
    animal="cattle-dairy",
    activity="drylot",
    climate_zone="temperate-cool",
    moisture_regime="moist",
    uncertainty="def",
):
    """Tier 1 method CH4 Emissions.

    Emissions from manure treatment.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    animal : str
        animal category.
    activity : str
        Type of manure treatment.
    climate_zone : str
        climate zone of region
    moisture_regime : str
        moisture regime in region
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = f"manure_{animal}"

    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, animal],
    )

    if animal in [
        "deer",
        "reindeer",
        "rabbit",
        "furbearing_mink",
        "furbearing_fox",
        "ostrich",
    ]:
        seq.read_parameter(
            name="ef_ch4_v4c10_others",
            table="ef_ch4_v4c10_others",
            coords=[animal],
        )
        value = seq.elementary.ch4_other_animals(
            n=seq.step.n.value,
            ef_others=seq.step.ef_ch4_v4c10_others.value,
        )
        seq.store_result(
            name="ch4_other_animals",
            value=value,
            unit="kg/year",
            year=year,
            lci_flag="emission|air|CH4",
        )
    else:
        seq.read_parameter(
            name="vs_rate",
            table="vs_rate",
            coords=[year, region, animal],
        )
        seq.read_parameter(
            name="weight",
            table="weight",
            coords=[year, region, animal],
        )
        value = seq.elementary.vs_tier1_(
            vs_rate=seq.step.vs_rate.value,
            tam=seq.step.weight.value,
        )
        seq.store_result(
            name="vs_tier1_",
            value=value,
            unit="kg/1000kg/year",
            year=year,
        )

        seq.read_parameter(
            name="ef_ch4_v4c10",
            table="ef_ch4_v4c10",
            coords=[animal, activity, climate_zone, moisture_regime],
        )
        seq.read_parameter(
            name="ms",
            table="ms",
            coords=[year, region, animal, activity],
        )
        seq.read_parameter(
            name="n",
            table="n",
            coords=[year, region, animal],
        )
        value = seq.elementary.ch4_mm(
            n=seq.step.n.value,
            vs=seq.step.vs_tier1_.value,
            awms=seq.step.ms.value,
            ef=seq.step.ef_ch4_v4c10.value,
        )
        seq.store_result(
            name="ch4_mm",
            value=value,
            unit="kg/year",
            year=year,
            lci_flag="emission|air|CH4",
        )
    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step


def tier2_ch4_manure(
    year=2019,
    region="DE",
    animal="cattle-dairy",
    feeding_situation="stall",
    diet_type="forage-mod",
    activity="drylot",
    climate_zone="temperate-cool",
    moisture_regime="moist",
    uncertainty="def",
):
    """Tier 2 method CH4 Emissions.

    Emissions from manure treatment.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    animal : str
        animal category.
    feeding_situation : str
        feeding situation of animal
    diet_type :str
        diet type of animal
    activity : str
        Type of manure treatment.
    climate_zone : str
        climate zone of region
    moisture_regime : str
        moisture regime in region
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """

    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("livestock-manure-treat sequence started --->")
    meta_dict = locals()
    meta_dict["product"] = f"manure_{animal}"

    seq.store_signature(meta_dict)

    #### activity
    seq.read_parameter(name="cf_i", table="cf_i", coords=[animal])

    seq.read_parameter(name="weight", table="weight", coords=[year, region, animal])

    value = seq.elementary.ne_m(cf_i=seq.step.cf_i.value, weight=seq.step.weight.value)

    seq.store_result(
        name="ne_m",
        value=value,
        unit="MJ/piece/day",
        year=year,
    )

    if animal.startswith(("cattle", "buffalo", "sheep", "goat")):
        if animal.startswith(("cattle", "buffalo")):
            seq.read_parameter(
                name="c_a_cattle", table="c_a_cattle", coords=[feeding_situation]
            )

            value = seq.elementary.nea_cattle_(
                c_a=seq.step.c_a_cattle.value, ne_m=seq.step.ne_m.value
            )
            seq.store_result(
                name="nea_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="weight", table="weight", coords=[year, region, animal]
            )

            seq.read_parameter(name="c", table="c", coords=[animal])

            seq.read_parameter(name="mw", table="mw", coords=[year, region, animal])

            seq.read_parameter(name="wg", table="wg", coords=[year, region, animal])

            value = seq.elementary.neg_cattle_(
                bw=seq.step.weight.value,
                c=seq.step.c.value,
                mw=seq.step.mw.value,
                wg=seq.step.wg.value,
            )
            seq.store_result(
                name="neg_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="milk", table="milk", coords=[year, region, animal])

            seq.read_parameter(name="fat", table="fat", coords=[year, region, animal])

            value = seq.elementary.nel_cattle_(
                milk=seq.step.milk.value, fat=seq.step.fat.value
            )
            seq.store_result(
                name="nel_cattle_",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(
                name="workhours", table="workhours", coords=[year, region, animal]
            )

            value = seq.elementary.ne_work(
                ne_m=seq.step.ne_m.value, hours=seq.step.workhours.value
            )
            seq.store_result(
                name="ne_work",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="c_pregnancy", table="c_pregnancy", coords=[animal])

            seq.read_parameter(
                name="ratio_preg",
                table="ratio_preg",
                coords=[year, region, animal],
            )

            value = seq.elementary.ne_p(
                ne_m=seq.step.ne_m.value,
                c_pregnancy=seq.step.c_pregnancy.value,
                ratio_preg=seq.step.ratio_preg.value,
            )
            seq.store_result(
                name="ne_p",
                value=value,
                unit="MJ/piece/day",
                year=year,
            )

            seq.read_parameter(name="de", table="de", coords=[year, region, animal])
            value = seq.elementary.rem(de=seq.step.de.value)
            seq.store_result(
                name="rem",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            value = seq.elementary.reg(de=seq.step.de.value)
            seq.store_result(
                name="reg",
                value=value,
                unit="MJ/MJ",
                year=year,
            )

            if "cattle" in animal and "calve" in animal:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_calve_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi_calve_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_calve_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in animal and "growing" in animal:
                seq.read_parameter(
                    name="ne_mf", table="ne_mf", coords=[year, region, diet_type]
                )

                value = seq.elementary.dmi_growing_(
                    ne_mf=seq.step.ne_mf.value, bw=seq.step.bw.value
                )
                seq.store_result(
                    name="dmi_growing_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_growing_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in animal and "bull" in animal:

                value = seq.elementary.dmi_steer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi_steer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_steer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in animal and "heifer" in animal:
                value = seq.elementary.dmi_heifer_(bw=seq.step.bw.value)
                seq.store_result(
                    name="dmi_heifer_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_heifer_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            elif "cattle" in animal and "dairy" in animal:
                value = seq.elementary.fcm(
                    milk=seq.step.milk.value, fat=seq.step.fat.value
                )
                seq.store_result(
                    name="fcm",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )

                value = seq.elementary.dmi_lactating_(
                    bw=seq.step.bw.value, fcm=seq.step.fcm.value
                )
                seq.store_result(
                    name="dmi_lactating_",
                    value=value,
                    unit="kg/piece/day",
                    year=year,
                )
                value = seq.elementary.ge_fromdmi_(dmi=seq.step.dmi_lactating_.value)
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="fromdmi_",
                )
            else:
                value = seq.elementary.ge_cattletier2_(
                    ne_m=seq.step.ne_m.value,
                    ne_a=seq.step.nea_cattle_.value,
                    ne_l=seq.step.nel_cattle_.value,
                    ne_p=seq.step.ne_p.value,
                    ne_work=seq.step.ne_work.value,
                    ne_g=seq.step.neg_cattle_.value,
                    reg=seq.step.reg.value,
                    rem=seq.step.rem.value,
                    de=seq.step.de.value,
                )
                seq.store_result(
                    name="ge",
                    value=value,
                    unit="MJ/piece/day",
                    year=year,
                    parameter_flag="cattletier2_",
                )

    elif animal.startswith(("sheep", "goat")):
        seq.read_parameter(name="c_a_sheep", table="c_a_sheep")

        value = seq.elementary.nea_sheep_(
            c_a=seq.step.c_a_sheep.value, weight=seq.step.weight.value
        )
        seq.store_result(
            name="nea_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="bw_i", table="bw_i", coords=[year, region, animal])

        seq.read_parameter(name="bw_f", table="bw_f", coords=[year, region, animal])

        seq.read_parameter(name="a", table="a", coords=[animal])

        seq.read_parameter(name="b", table="b", coords=[animal])

        value = seq.elementary.neg_sheep_(
            bw_f=seq.step.bw_f.value,
            bw_i=seq.step.bw_i.value,
            a=seq.step.a.value,
            b=seq.step.b.value,
        )
        seq.store_result(
            name="neg_sheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        # eq 10.9 or 10.10
        seq.read_parameter(name="milk", table="milk", coords=[year, region, animal])

        seq.read_parameter(
            name="ev_milk", table="ev_milk", coords=[year, region, animal]
        )

        value = seq.elementary.nel_asheep_(
            milk=seq.step.milk.value, ev_milk=seq.step.ev_milk.value
        )
        seq.store_result(
            name="nel_asheep_",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(
            name="ev_wool", table="ev_wool", coords=[year, region, animal]
        )
        seq.read_parameter(
            name="pr_wool", table="pr_wool", coords=[year, region, animal]
        )

        value = seq.elementary.ne_wool(
            ev_wool=seq.step.ev_wool.value, pr_wool=seq.step.pr_wool.value
        )
        seq.store_result(
            name="ne_wool",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="c_pregnancy", table="c_pregnancy", coords=[animal])

        seq.read_parameter(
            name="ratio_preg",
            table="ratio_preg",
            coords=[year, region, animal],
        )
        value = seq.elementary.ne_p(
            ne_m=seq.step.ne_m.value,
            c_pregnancy=seq.step.c_pregnancy.value,
            ratio_preg=seq.step.ratio_preg.value,
        )
        seq.store_result(
            name="ne_p",
            value=value,
            unit="MJ/piece/day",
            year=year,
        )

        seq.read_parameter(name="de", table="de", coords=[year, region, animal])
        value = seq.elementary.rem(de=seq.step.de.value)
        seq.store_result(
            name="rem",
            value=value,
            unit="MJ/MJ",
            year=year,
        )
        value = seq.elementary.reg(de=seq.step.de.value)
        seq.store_result(
            name="reg",
            value=value,
            unit="MJ/MJ",
            year=year,
        )

        value = seq.elementary.ge_sheeptier2_(
            ne_m=seq.step.ne_m.value,
            ne_a=seq.step.nea_sheep_.value,
            ne_l=seq.step.nel_asheep_.value,
            ne_p=seq.step.ne_p.value,
            ne_wool=seq.step.ne_wool.value,
            ne_g=seq.step.neg_sheep_.value,
            reg=seq.step.reg.value,
            rem=seq.step.rem.value,
            de=seq.step.de.value,
        )
        seq.store_result(
            name="ge",
            value=value,
            unit="MJ/piece/day",
            year=year,
            parameter_flag="sheeptier2_",
        )

    seq.read_parameter(name="ash", table="ash", coords=[year, region, animal])
    seq.read_parameter(name="ue", table="ue", coords=[year, region, animal])
    value = seq.elementary.vs_tier2_(
        ge=seq.step.ge.value,
        de=seq.step.de.value,
        ue=seq.step.ue.value,
        ash=seq.step.ash.value,
    )
    seq.store_result(
        name="vs_tier2_",
        value=value,
        unit="kg/piece/day",
        year=year,
    )

    seq.read_parameter(name="b0", table="b0", coords=[year, region, animal])
    seq.read_parameter(
        name="mcf_v4c10",
        table="mcf_v4c10",
        coords=[activity, climate_zone, moisture_regime],
    )
    seq.read_parameter(name="ms", table="ms", coords=[year, region, animal, activity])
    value = seq.elementary.ef_mm(
        vs=seq.step.vs_tier2_.value,
        b0=seq.step.b0.value,
        mcf=seq.step.mcf_v4c10.value,
        awms=seq.step.ms.value,
    )
    seq.store_result(
        name="ef_mm",
        value=value,
        unit="kg/piece/year",
        year=year,
    )

    seq.read_parameter(name="n", table="n", coords=[year, region, animal])
    value = seq.elementary.ch4_mm(
        n=seq.step.n.value,
        vs=seq.step.vs.value,
        ef=seq.step.ef_mm.value,
        awms=seq.step.awms.value,
    )
    seq.store_result(
        name="ch4_mm",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> livestock-manure-treat sequence finalized.")
    return seq.step
