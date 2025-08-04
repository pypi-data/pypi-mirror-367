"""
Sequences to determine GHG emissions from managed soils.


"""


import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_n2o_inputs(
    year=2019,
    region="DE",
    product="wheat_spring",
    landuse_type="CL-ANNUAL",
    cultivation_type="N_unspec",
    climate_zone="temperate",
    moisture_regime="wet",
    landusechange=False,  # {"year_ref"=int, "landusechange_type":"CL_CL"}
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Direct emissions from nitrogen inputs into landuse.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        crop type.
    landuse_type : str
        type of landuse
    cultivation_type : str
        type of land cultivation
    climate_zone : str
        climate zone of region
    moisture_regime : str
        moisture regime of region
    landusechange : dict
        {"year_ref": 2020, "landusechange_type": "CL_CL"}
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "crop_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="yield_fresh",
        table="yield_fresh",
        coords=[year, region, landuse_type, product],
        lci_flag=f"supply|product|{product}",
    )

    seq.read_parameter(
        name="dry",
        table="dry",
        coords=[year, region, product],
    )

    value = seq.elementary.crop(
        yield_fresh=seq.step.yield_fresh.value, dry=seq.step.dry.value
    )
    seq.store_result(
        name="crop",
        value=value,
        unit="kg/ha",
        year=year,
    )

    seq.read_parameter(
        name="r_ag",
        table="r_ag",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="rs",
        table="rs",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="n_ag",
        table="n_ag",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="n_bg",
        table="n_bg",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="area",
        table="area",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_renew",
        table="frac_renew",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_remove",
        table="frac_remove",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_burnt",
        table="frac_burnt",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="c_f",
        table="c_f",
        coords=[year, region, product],
    )

    value = seq.elementary.f_cr(
        crop=seq.step.crop.value,
        r_ag=seq.step.r_ag.value,
        area=seq.step.area.value,
        n_ag=seq.step.n_ag.value,
        frac_remove=seq.step.frac_remove.value,
        frac_burnt=seq.step.frac_burnt.value,
        frac_renew=seq.step.frac_renew.value,
        c_f=seq.step.c_f.value,
        rs=seq.step.rs.value,
        n_bg=seq.step.n_bg.value,
    )
    seq.store_result(
        name="f_cr",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="n_mms",
        table="n_mms",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_comp",
        table="f_comp",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_sew",
        table="f_sew",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_ooa",
        table="f_ooa",
        coords=[year, region, landuse_type, product],
    )

    value = seq.elementary.f_on(
        f_am=seq.step.n_mms.value,
        f_sew=seq.step.f_sew.value,
        f_comp=seq.step.f_comp.value,
        f_ooa=seq.step.f_ooa.value,
    )
    seq.store_result(
        name="f_on",
        value=value,
        unit="kg/year",
        year=year,
    )

    if landusechange is not False:
        # inventory year
        # sum over all management types
        # climate_zone,moisture_regime,soil_type,landuse_type,management_practice,amendment_level
        year_ref = landusechange["year_ref"]
        landusechange_type = landusechange["landusechange_type"]

        d = seq.get_inventory_levels(table="a", year=year, region=region)
        value = 0.0
        for i in range(len(list(d.values())[0])):
            climate_zone = d["climate_zone"][i]
            moisture_regime = d["moisture_regime"][i]
            soil_type = d["soil_type"][i]
            landuse_type = d["landuse_type"][i]
            management_practice = d["management_practice"][i]
            amendment_level = d["amendment_level"][i]

            seq.read_parameter(
                name=f"a_xxx_0_{i}_xxx",
                table="a",
                coords=[
                    year,
                    region,
                    climate_zone,
                    moisture_regime,
                    soil_type,
                    landuse_type,
                    management_practice,
                    amendment_level,
                ],
            )

            seq.read_parameter(
                name=f"soc_ref_xxx_0_{i}_xxx",
                table="soc_ref",
                coords=[climate_zone, moisture_regime, soil_type],
            )

            seq.read_parameter(
                name=f"f_lu_xxx_0_{i}_xxx",
                table="f_lu",
                coords=[landuse_type, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name=f"f_mg_xxx_0_{i}_xxx",
                table="f_mg",
                coords=[management_practice, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name=f"f_i_xxx_0_{i}_xxx",
                table="f_i",
                coords=[amendment_level, climate_zone, moisture_regime],
            )

            value += seq.elementary.soc(
                soc_ref=getattr(getattr(seq.step, f"soc_ref_xxx_0_{i}_xxx"), "value"),
                f_lu=getattr(getattr(seq.step, f"f_lu_xxx_0_{i}_xxx"), "value"),
                f_mg=getattr(getattr(seq.step, f"f_mg_xxx_0_{i}_xxx"), "value"),
                f_i=getattr(getattr(seq.step, f"f_i_xxx_0_{i}_xxx"), "value"),
                a=getattr(getattr(seq.step, f"a_xxx_0_{i}_xxx"), "value"),
            )
        seq.store_result(
            name="soc_xxx_0_xxx",
            value=value,
            unit="t",
            year=year,
        )

        # inventory year
        # sum over all management types
        d = seq.get_inventory_levels(table="a", year=year_ref, region=region)
        value = 0.0
        for i in range(len(list(d.values())[0])):
            climate_zone = d["climate_zone"][i]
            moisture_regime = d["moisture_regime"][i]
            soil_type = d["soil_type"][i]
            landuse_type = d["landuse_type"][i]
            management_practice = d["management_practice"][i]
            amendment_level = d["amendment_level"][i]

            seq.read_parameter(
                name=f"soc_ref_xxx_T_{i}_xxx",
                table="soc_ref",
                coords=[climate_zone, moisture_regime, soil_type],
            )

            seq.read_parameter(
                name=f"f_lu_xxx_T_{i}_xxx",
                table="f_lu",
                coords=[landuse_type, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name=f"f_mg_xxx_T_{i}_xxx",
                table="f_mg",
                coords=[management_practice, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name=f"f_i_xxx_T_{i}_xxx",
                table="f_i",
                coords=[amendment_level, climate_zone, moisture_regime],
            )

            seq.read_parameter(
                name=f"a_xxx_T_{i}_xxx",
                table="a",
                coords=[
                    year_ref,
                    region,
                    climate_zone,
                    moisture_regime,
                    soil_type,
                    landuse_type,
                    management_practice,
                    amendment_level,
                ],
            )

            value += seq.elementary.soc(
                soc_ref=getattr(getattr(seq.step, f"soc_ref_xxx_T_{i}_xxx"), "value"),
                f_lu=getattr(getattr(seq.step, f"f_lu_xxx_T_{i}_xxx"), "value"),
                f_mg=getattr(getattr(seq.step, f"f_mg_xxx_T_{i}_xxx"), "value"),
                f_i=getattr(getattr(seq.step, f"f_i_xxx_T_{i}_xxx"), "value"),
                a=getattr(getattr(seq.step, f"a_xxx_T_{i}_xxx"), "value"),
            )
        seq.store_result(
            name="soc_xxx_T_xxx",
            value=value,
            unit="t",
            year=year_ref,
        )

        value = seq.elementary.delta_c_mineral(
            soc_0=seq.step.soc_xxx_0_xxx.value,
            soc_t=seq.step.soc_xxx_T_xxx.value,
            d=20,
        )
        seq.store_result(
            name="delta_c_mineral",
            value=value,
            unit="t/year",
            year=year,
        )

        seq.read_parameter(
            name="r",
            table="r",
            coords=[year, region, landusechange_type],
        )

        value = seq.elementary.f_som(
            delta_c_mineral=seq.step.delta_c_mineral.value, r=seq.step.r.value
        )
        seq.store_result(
            name="f_som",
            value=value,
            unit="kg/year",
            year=year,
        )

    else:
        logger.info(
            "Not able to estimate gross changes of mineral soil C. Consider to collect the required data. Bias in the N2O estimate."
        )
        value = 0.0
        seq.store_result(
            name="f_som",
            value=value,
            unit="kg/year",
            year=year,
        )

    seq.read_parameter(
        name="ef1",
        table="ef1",
        coords=[year, region, cultivation_type, moisture_regime],
    )

    seq.read_parameter(
        name="f_sn",
        table="f_sn",
        coords=[year, region, landuse_type, cultivation_type],
    )

    value = seq.elementary.n2o_n_inputs(
        f_sn=seq.step.f_sn.value,
        f_on=seq.step.f_on.value,
        f_cr=seq.step.f_cr.value,
        f_som=seq.step.f_som.value,
        ef1=seq.step.ef1.value,
    )
    seq.store_result(
        name="n2o_n_inputs",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_inputs.value)
    seq.store_result(
        name="n2o",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier1_n2o_os(
    year=2019,
    region="DE",
    landuse_type="CL",
    climate_zone="temperate",
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Direct emissions from managed organic soils.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    landuse_type : str
        type of landuse
    climate_zone : str
        climate zone of region
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "crop_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="ef2",
        table="ef2",
        coords=[landuse_type, climate_zone],
    )

    seq.read_parameter(
        name="f_os",
        table="f_os",
        coords=[year, region, landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_os(f_os=seq.step.f_os.value, ef2=seq.step.ef2.value)
    seq.store_result(
        name="n2o_n_os",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_os.value)
    seq.store_result(
        name="n2o",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier1_n2o_prp(
    year=2010,
    region="DE",
    landuse_type="CL",
    product="cattle-dairy",
    climate_zone="temperate",
    uncertainty="def",
):
    """Tier 1 method N2O Emissions.

    Direct emissions from urine and dung inputs inputs into landuse.

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    landuse_type : str
        type of landuse
    product : str
        crop type.
    climate_zone : str
        climate zone of region
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "animal_production"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="weight",
        table="weight",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="n_rate",
        table="n_rate",
        coords=[year, region, product],
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

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="ms",
        table="ms",
        coords=[year, region, product, "pasture"],
    )

    value = seq.elementary.f_prp(
        n=seq.step.n.value,
        nex=seq.step.nex_tier1_.value,
        ms=seq.step.ms.value,
    )

    seq.store_result(
        name="f_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef3",
        table="ef3",
        coords=[landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_prp(f_prp=seq.step.f_prp.value, ef3=seq.step.ef3.value)
    seq.store_result(
        name="n2o_n_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_prp.value)
    seq.store_result(
        name="n2o_prp",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> soil sequence finalized.")
    return seq.step


def tier2_n2o_direct(
    year=2019,
    region="DE",
    product="wheat_spring",
    landuse_type="CL",
    cultivation_type="N_unspec",
    species_type="cattle-dairy",
    moisture_regime="wet",
    climate_zone="temperal",
    uncertainty="def",
):
    """Tier 2 method N2O Emissions.

    Direct emissions from landuse.
    TODO: split up so that emission can be allocated to activity and product

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        crop type.
    landuse_type : str
        type of landuse
    cultivation_type : str
        type of land cultivation
    climate_zone : str
        climate zone of region
    moisture_regime : str
        moisture regime of region
    landusechange : dict
        {"year_ref": 2020, "landusechange_type": "CL_CL"}
    uncertainty : str
        'analytical', 'monte_carlo' or a property dimension, e.g. 'def'

    Returns
    -------
    VALUE: DataClass
        Inlcudes the results of each step of the sequence.
    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("soils sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "crop_production"
    seq.store_signature(meta_dict)

    # N2O directly from N inputs (inputs)
    seq.read_parameter(
        name="yield_fresh",
        table="yield_fresh",
        coords=[year, region, landuse_type, product],
        lci_flag=f"supply|product|{product}",
    )

    seq.read_parameter(
        name="dry",
        table="dry",
        coords=[year, region, product],
    )

    value = seq.elementary.crop(
        yield_fresh=seq.step.yield_fresh.value, dry=seq.step.dry.value
    )
    seq.store_result(
        name="crop",
        value=value,
        unit="kg/ha",
        year=year,
    )

    seq.read_parameter(
        name="r_ag",
        table="r_ag",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="rs",
        table="rs",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="n_ag",
        table="n_ag",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="n_bg",
        table="n_bg",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="area",
        table="area",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_renew",
        table="frac_renew",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_remove",
        table="frac_remove",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="frac_burnt",
        table="frac_burnt",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="c_d",
        table="c_d",
        coords=[year, region, product],
    )

    value = seq.elementary.f_cr(
        crop=seq.step.crop.value,
        r_ag=seq.step.r_ag.value,
        area=seq.step.area.value,
        n_ag=seq.step.n_ag.value,
        frac_remove=seq.step.frac_remove.value,
        frac_burnt=seq.step.frac_burnt.value,
        frac_renew=seq.step.frac_renew.value,
        c_f=seq.step.c_d.value,
        rs=seq.step.rs.value,
        n_bg=seq.step.n_bg.value,
    )
    seq.store_result(
        name="f_cr",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="f_am",
        table="f_am",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_comp",
        table="f_comp",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_sew",
        table="f_sew",
        coords=[year, region, landuse_type, product],
    )

    seq.read_parameter(
        name="f_ooa",
        table="f_ooa",
        coords=[year, region, landuse_type, product],
    )

    value = seq.elementary.f_on(
        f_am=seq.step.f_am.value,
        f_sew=seq.step.f_sew.value,
        f_comp=seq.step.f_comp.value,
        f_ooa=seq.step.f_ooa.value,
    )
    seq.store_result(
        name="f_on",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef1",
        table="ef1",
        coords=[year, region, cultivation_type, moisture_regime],
    )

    seq.read_parameter(
        name="f_sn",
        table="f_sn",
        coords=[year, region, landuse_type, cultivation_type],
    )

    value = seq.elementary.n2o_n_inputs(
        f_sn=seq.step.f_sn.value,
        f_on=seq.step.f_on.value,
        f_cr=seq.step.f_cr.value,
        f_som=seq.step.f_som.value,
        ef1=seq.step.ef1.value,
    )
    seq.store_result(
        name="n2o_n_inputs",
        value=value,
        unit="kg/year",
        year=year,
    )

    # N2O from organic soils (os)
    seq.read_parameter(
        name="ef2",
        table="ef2",
        coords=[landuse_type, climate_zone],
    )

    seq.read_parameter(
        name="f_os",
        table="f_os",
        coords=[year, region, landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_os(f_os=seq.step.f_os.value, ef2=seq.step.ef2.value)
    seq.store_result(
        name="n2o_n_os",
        value=value,
        unit="kg/year",
        year=year,
    )

    # N2O from urine of animals on pasture-range-paddock (prp)
    seq.read_parameter(
        name="weight",
        table="weight",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="n_rate",
        table="n_rate",
        coords=[year, region, species_type],
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

    seq.read_parameter(
        name="n",
        table="n",
        coords=[year, region, species_type],
    )

    seq.read_parameter(
        name="ms",
        table="ms",
        coords=[year, region, species_type, "pasture"],
    )

    value = seq.elementary.f_prp(
        n=seq.step.n.value,
        nex=seq.step.nex_tier1_.value,
        ms=seq.step.ms.value,
    )

    seq.store_result(
        name="f_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    seq.read_parameter(
        name="ef3",
        table="ef3",
        coords=[landuse_type, climate_zone],
    )

    value = seq.elementary.n2o_n_prp(f_prp=seq.step.f_prp.value, ef3=seq.step.ef3.value)
    seq.store_result(
        name="n2o_n_prp",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o_n_direct(
        n2o_n_inputs=seq.step.n2o_n_inputs.value,
        n2o_n_os=seq.step.n2o_n_inputs.value,
        n2o_n_prp=seq.step.n2o_n_prp.value,
    )
    seq.store_result(
        name="n2o_n_direct",
        value=value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.n2o(n2o_n=seq.step.n2o_n_direct.value)
    seq.store_result(
        name="n2o",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|N2O",
    )

    logger.info("---> soil sequence finalized.")
    return seq.step
