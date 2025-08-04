# -*- coding: utf-8 -*-
"""

Created on Wed Oct 25 09:18:25 2023

@author: Mathieu Delpierre (2.-0 LCA Consultants)

Sequences to determine GHG emissions' from cement industry (combination of IPCC
equations and extensions added to them.
"""

from logging import getLogger

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = getLogger("root")


####################################################################################
# --------------------- Sequence on cement production ---------------------------- #
####################################################################################


def cement_production(
    year=2011,
    region="US",
    product="portland",
    uncertainty="def",
):
    """
    This function calculates different factors related to the production of
    cement, namely: the mass of clinker needed to produce the cement considered (in
    tonnes), the electricity needed in TJ, the energy (heat) needed in TJ, the gypsum
    needed (in tonne), the production of CKD (Cwement Kiln Dust, in tonnes), and of
    cement waste during construction (in tonnes).

    Parameters
    ----------
    year : integer, optional
        Year of the cement production. The default is 2011.
    region : string, optional
        Region of the cement production. The default is "US".
    product : string, optional
        Type of cement that is produced. The default is "portland".
    uncertainty : string, optional
        Defined the type of uncertianty that we want to consider in the calculation. The
        default is "def".

    Returns
    -------
    Python object
        A Python object os created with different attrobutes that contain the results
        mentioned in the description above.

    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)

    logger.info("cement-production sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "cement_production"
    seq.store_signature(meta_dict)

    # Mass of cement
    seq.read_parameter(
        name="cement_prod_world",
        table="cement_prod_world",
        coords=[year, region],
        lci_flag="supply|product|cement",
    )

    # Proportion of clinker in cement
    seq.read_parameter(
        name="c_cl",
        table="c_cl",
        coords=[year, region, product],
        lci_flag="transf_coeff|product|clinker|cement",
    )

    # Mass clinker
    mass_clinker = seq.elementary.mass_clinker(
        mass_cement=seq.step.cement_prod_world.value, clink_on_cem=seq.step.c_cl.value
    )

    seq.store_result(
        name="mass_clinker",
        value=mass_clinker,
        unit="tonnes",
        year=year,
        lci_flag="use|product|clinker",
    )

    # Electricity use for cement production (in TJ/tonne)
    seq.read_parameter(
        name="elec_use",
        table="elec_use",
        coords=[year, region],
    )

    # Electricity consumption for cement production (combining
    # calcination + cement mill):
    elec_use_cement = seq.elementary.elec_use_cement(
        mass_cement=seq.step.cement_prod_world.value,
        elec_intensity=seq.step.elec_use.value,
    )

    seq.store_result(
        name="elec_use_cement",
        value=elec_use_cement,
        unit="TJ",
        year=year,
        lci_flag="use|product|electricity",
    )

    # Energy needs for the cement production (heat)
    seq.read_parameter(
        name="energy_cement",
        table="energy_cement",
        coords=[year, region, product],
    )

    # energy_need_cement = seq.step.energy_cement.value * seq.step.mass_cement.value
    energy_need_cement = seq.elementary.energy_need_cement(
        mass_cement=seq.step.cement_prod_world.value,
        energy_cement=seq.step.energy_cement.value,
    )

    seq.store_result(
        name="energy_need_cement",
        value=energy_need_cement,
        unit="TJ",
        year=year,
        lci_flag="use|product|steam",
    )

    # Gypsum consumption in the cement mill process
    seq.read_parameter(
        name="gypsum_coeff",
        table="gypsum_coeff",
        coords=[year, region],
    )

    gypsum_use_cement_mill = seq.elementary.gypsum_use_cement_mill(
        mass_cement=seq.step.cement_prod_world.value,
        gyp_intensity=seq.step.gypsum_coeff.value,
    )

    seq.store_result(
        name="gypsum_use_cement_mill",
        value=gypsum_use_cement_mill,
        unit="tonnes",
        year=year,
        lci_flag="use|product|gypsum",
    )

    seq.read_parameter(
        name="product_trans_coeff_gypsum",
        table="product_trans_coeff_gypsum",
        coords=[year, region],
        lci_flag="transf_coeff|product|gypsum|cement",
    )

    # Production of CKD that will be sent to landfill
    seq.read_parameter(
        name="ckd_on_clinker",
        table="ckd_on_clinker",
        coords=[year, region],
        lci_flag="transf_coeff|waste|clinker|CKD",
    )

    seq.read_parameter(
        name="coeff_ckd_landfill",
        table="coeff_ckd_landfill",
        coords=[year, region],
    )

    ckd_landfill = seq.elementary.ckd_landfill(
        mass_clinker=seq.step.mass_clinker.value,
        ckd_on_clinker=seq.step.ckd_on_clinker.value,
        coeff_ckd_landfill=seq.step.coeff_ckd_landfill.value,
    )

    seq.store_result(
        name="ckd_landfill",
        value=ckd_landfill,
        unit="tonnes",
        year=year,
        lci_flag="supply|product|CKD",
    )

    # Waste production from cement during construction
    seq.read_parameter(
        name="cement_loss_construction",
        table="cement_loss_construction",
        coords=[year, region],
        lci_flag="transf_coeff|waste|cement|cement_waste",
    )

    waste_cement_construction = seq.elementary.waste_cement_construction(
        mass_cement=seq.step.cement_prod_world.value,
        loss_coeff=seq.step.cement_loss_construction.value,
    )

    seq.store_result(
        name="waste_cement_construction",
        value=waste_cement_construction,
        unit="tonnes",
        year=year,
        lci_flag="supply|product|cement_waste",
    )

    # cao_on_clinker
    seq.read_parameter(
        name="cao_in_clinker",
        table="cao_in_clinker",
        coords=[year, region],
        lci_flag="transf_coeff|product|calcium_oxide|clinker",
    )

    # ckd_correc_fact
    seq.read_parameter(
        name="ckd_correc_fact",
        table="ckd_correc_fact",
        coords=[year, region],
    )

    # corrected emission factor for clinker production
    ef_clc = seq.elementary.ef_clc(
        cao_in_clinker=seq.step.cao_in_clinker.value,
        ckd_correc_fact=seq.step.ckd_correc_fact.value,
    )

    seq.store_result(
        name="ef_clc",
        value=ef_clc,
        unit="tonnes CO2/tonne of clinker",
        year=year,
    )

    # CO2-emissions from the cement production (tier 2 equation from IPCC if we start
    # from clinker production volumes).
    co2_emissions_tier2_ = seq.elementary.co2_emissions_tier2_(
        m_cl=seq.step.mass_clinker.value, ef_cl=0.51, cf_ckd=1.073
    )

    seq.store_result(
        name="co2_emissions_tier2_",
        value=co2_emissions_tier2_,
        unit="tonnes",
        year=year,
        lci_flag="emission|product|co2",
    )

    # add transfer coefficients
    # for clinker
    transfer_coeff_gypsum = seq.read_parameter(
        name="product_trans_coeff_gypsum",
        table="product_trans_coeff_gypsum",
        coords=[year, region],
        lci_flag="transf_coeff|product|clinker|cement",
    )

    # for gypsum
    transfer_coeff_gypsum = seq.read_parameter(
        name="product_trans_coeff_gypsum",
        table="product_trans_coeff_gypsum",
        coords=[year, region],
        lci_flag="transf_coeff|product|gypsum|cement",
    )

    logger.info("---> cement model finished.")
    return seq.step


####################################################################################
# --------------------- Sequence on concrete production -------------------------- #
####################################################################################


def concrete_production(
    year=2011,
    region="US",
    product="portland",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)

    logger.info("concrete-production sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "concrete_production"
    seq.store_signature(meta_dict)

    # Mass of cement
    seq.read_parameter(
        name="cement_prod_world",
        table="cement_prod_world",
        coords=[year, region],
    )

    ####### Production of concrete #########
    seq.read_parameter(
        name="volumic_mass_concrete",
        table="volumic_mass_concrete",
        coords=[year, region],
    )

    seq.read_parameter(
        name="cement_distrib",
        table="cement_distrib",
        coords=[year, region, "concrete"],
    )

    seq.read_parameter(
        name="inputs_concrete",
        table="inputs_concrete",
        coords=[year, region, "cement"],
    )

    seq.read_parameter(
        name="volumic_mass_concrete",
        table="volumic_mass_concrete",
        coords=[year, region],
    )

    mass_concrete = seq.elementary.mass_concrete(
        mass_cement=seq.step.cement_prod_world.value,
        cement_to_concrete_coeff=seq.step.cement_distrib.value,
        cement_use_concrete=seq.step.inputs_concrete.value,
        volumic_mass_concrete=seq.step.volumic_mass_concrete.value,
    )

    seq.store_result(
        name="mass_concrete",
        value=mass_concrete,
        unit="tonnes",
        year=year,
        lci_flag="supply|product|concrete",
    )

    # Consumption of water for concrete production
    seq.read_parameter(
        name="inputs_concrete",
        table="inputs_concrete",
        coords=[year, region, "water"],
    )

    water_use_concrete = seq.elementary.water_use_concrete(
        mass_concrete=seq.step.mass_concrete.value,
        volumic_mass_concrete=seq.step.volumic_mass_concrete.value,
        water_use_concrete=seq.step.inputs_concrete.value,
    )

    seq.store_result(
        name="water_use_concrete",
        value=water_use_concrete,
        unit="tonnes",
        year=year,
        lci_flag="use|product|water",
    )

    # Consumption of aggregates for concrete production
    seq.read_parameter(
        name="inputs_concrete",
        table="inputs_concrete",
        coords=[year, region, "aggregate"],
    )

    aggregate_use_concrete = seq.elementary.aggregate_use_concrete(
        mass_concrete=seq.step.mass_concrete.value,
        volumic_mass_concrete=seq.step.volumic_mass_concrete.value,
        aggregate_use_concrete=seq.step.inputs_concrete.value,
    )

    seq.store_result(
        name="aggregate_use_concrete",
        value=aggregate_use_concrete,
        unit="tonnes",
        year=year,
        lci_flag="use|product|aggregate",
    )

    # Consumption of electricity for concrete production
    seq.read_parameter(
        name="inputs_concrete",
        table="inputs_concrete",
        coords=[year, region, "electricity"],
    )

    elec_use_concrete = seq.elementary.elec_use_concrete(
        mass_concrete=seq.step.mass_concrete.value,
        volumic_mass_concrete=seq.step.volumic_mass_concrete.value,
        elec_use_concrete=seq.step.inputs_concrete.value,
    )

    seq.store_result(
        name="elec_use_concrete",
        value=elec_use_concrete,
        unit="TJ",
        year=year,
        lci_flag="use|product|electricity",
    )

    # Transfer coefficients
    # cement_in_concrete
    seq.read_parameter(
        name="product_trans_coeff_concrete",
        table="product_trans_coeff_concrete",
        coords=[year, region, "cement"],
        lci_flag="transf_coeff|product|cement|concrete",
    )

    # water_in_concrete
    seq.read_parameter(
        name="product_trans_coeff_concrete",
        table="product_trans_coeff_concrete",
        coords=[year, region, "water"],
        lci_flag="transf_coeff|product|water|concrete",
    )

    # Emission/losses of water
    water_emission_cement = seq.elementary.water_emission_cement(
        water_use=seq.step.water_use_concrete.value,
        fraction_water_emission=(1 - seq.step.product_trans_coeff_concrete.value),
    )

    seq.store_result(
        name="water_emission_cement",
        value=water_emission_cement,
        unit="tonnes",
        year=year,
        lci_flag="emission|product|water",
    )

    # aggregate_in_concrete
    seq.read_parameter(
        name="product_trans_coeff_concrete",
        table="product_trans_coeff_concrete",
        coords=[year, region, "aggregate"],
        lci_flag="transf_coeff|product|aggregate|concrete",
    )

    logger.info("---> concrete model finished.")
    return seq.step


####################################################################################
# ----------------------- Sequence on mortar production -------------------------- #
####################################################################################


def mortar_production(
    year=2011,
    region="US",
    product="portland",
    uncertainty="def",
):
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)

    logger.info("mortar-production sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "mortar_production"
    seq.store_signature(meta_dict)

    # Mass of cement
    seq.read_parameter(
        name="cement_prod_world",
        table="cement_prod_world",
        coords=[year, region],
    )

    ####### Production of mortar #########

    # Volumic mass of mortar (in kg/m3)
    seq.read_parameter(
        name="volumic_mass_mortar",
        table="volumic_mass_mortar",
        coords=[year, region],
    )

    # Share of cement used for mortar production
    seq.read_parameter(
        name="cement_distrib",
        table="cement_distrib",
        coords=[year, region, "mortar"],
    )

    # Consumption of cement for mortar production
    seq.read_parameter(
        name="inputs_mortar",
        table="inputs_mortar",
        coords=[year, region, "cement"],
    )

    mass_mortar = seq.elementary.mass_mortar(
        mass_cement=seq.step.cement_prod_world.value,
        cement_to_mortar_coeff=seq.step.cement_distrib.value,
        cement_use_mortar=seq.step.inputs_mortar.value,
        volumic_mass_mortar=seq.step.volumic_mass_mortar.value,
    )

    seq.store_result(
        name="mass_mortar",
        value=mass_mortar,
        unit="tonnes",
        year=year,
        lci_flag="supply|product|mortar",
    )

    # Consumption of water for mortar production
    seq.read_parameter(
        name="inputs_mortar",
        table="inputs_mortar",
        coords=[year, region, "water"],
    )

    water_use_mortar = seq.elementary.water_use_mortar(
        mass_mortar=seq.step.mass_mortar.value,
        volumic_mass_mortar=seq.step.volumic_mass_mortar.value,
        water_use_mortar=seq.step.inputs_mortar.value,
    )

    seq.store_result(
        name="water_use_mortar",
        value=water_use_mortar,
        unit="tonnes",
        year=year,
        lci_flag="use|product|water",
    )

    # Consumption of sand for mortar production
    seq.read_parameter(
        name="inputs_mortar",
        table="inputs_mortar",
        coords=[year, region, "sand"],
    )

    sand_use_mortar = seq.elementary.sand_use_mortar(
        mass_mortar=seq.step.mass_mortar.value,
        volumic_mass_mortar=seq.step.volumic_mass_mortar.value,
        sand_use_mortar=seq.step.inputs_mortar.value,
    )

    seq.store_result(
        name="sand_use_mortar",
        value=sand_use_mortar,
        unit="tonnes",
        year=year,
        lci_flag="use|product|sand",
    )

    # Consumption of lime for mortar production
    seq.read_parameter(
        name="inputs_mortar",
        table="inputs_mortar",
        coords=[year, region, "lime"],
    )

    lime_use_mortar = seq.elementary.lime_use_mortar(
        mass_mortar=seq.step.mass_mortar.value,
        volumic_mass_mortar=seq.step.volumic_mass_mortar.value,
        lime_use_mortar=seq.step.inputs_mortar.value,
    )

    seq.store_result(
        name="lime_use_mortar",
        value=lime_use_mortar,
        unit="tonnes",
        year=year,
        lci_flag="use|product|lime",
    )

    # Consumption of electricity for mortar production
    seq.read_parameter(
        name="inputs_mortar",
        table="inputs_mortar",
        coords=[year, region, "electricity"],
    )

    elec_use_mortar = seq.elementary.elec_use_mortar(
        mass_mortar=seq.step.mass_mortar.value,
        volumic_mass_mortar=seq.step.volumic_mass_mortar.value,
        elec_use_mortar=seq.step.inputs_mortar.value,
    )

    seq.store_result(
        name="elec_use_mortar",
        value=elec_use_mortar,
        unit="TJ",
        year=year,
        lci_flag="use|product|electricity",
    )

    # Transfer coeffcieints
    # cement_in_mortar
    seq.read_parameter(
        name="product_trans_coeff_mortar",
        table="product_trans_coeff_mortar",
        coords=[year, region, "cement"],
        lci_flag="transf_coeff|product|cement|mortar",
    )

    # water_in_mortar
    seq.read_parameter(
        name="product_trans_coeff_mortar",
        table="product_trans_coeff_mortar",
        coords=[year, region, "water"],
        lci_flag="transf_coeff|product|water|mortar",
    )

    # Emission/losses of water
    water_emission_cement = seq.elementary.water_emission_cement(
        water_use=seq.step.water_use_mortar.value,
        fraction_water_emission=(1 - seq.step.product_trans_coeff_mortar.value),
    )

    seq.store_result(
        name="water_emission_cement",
        value=water_emission_cement,
        unit="tonnes",
        year=year,
        lci_flag="emission|product|water",
    )

    # sand_in_mortar
    seq.read_parameter(
        name="product_trans_coeff_mortar",
        table="product_trans_coeff_mortar",
        coords=[year, region, "sand"],
        lci_flag="transf_coeff|product|sand|mortar",
    )

    # lime_in_mortar
    seq.read_parameter(
        name="product_trans_coeff_mortar",
        table="product_trans_coeff_mortar",
        coords=[year, region, "lime"],
        lci_flag="transf_coeff|product|lime|mortar",
    )

    logger.info("---> mortar model finished.")
    return seq.step


####################################################################################
# -------------------- Sequence on carbonation on concrete ----------------------- #
####################################################################################


def carbonation_cement_concrete(
    year=2011,
    lifetime_use_cement=10,
    region="US",
    product="portland",
    uncertainty="def",
    exposure_condition="Exposed outdoor",
    compressive_strength="16-23 Mpa",
    structure="Wall",
    cement_product="concrete",
):
    """
    This sequence function calculates the amount of carbonation that takes place in
    concrete, depending on the lifetime of use. A global result (over the whole
    lifetime) and a yearly result (for each year) is calculated in tonnes of
    CO2-absorbed.

    Parameters
    ----------
    year : integer, optional
        Year of cement production (and by assumption concrete). The default is 2011.
    lifetime_use_cement : integer, optional
        Number of years that the concrete is used. The default is 10.
    region : string, optional
        Region where the concrete is used. The default is "US".
    product : string, optional
        Type of cement that is used to later produce concrete. The default is "portland".
    uncertainty : string, optional
        Defines the type of uncertainty we want to consider. The default is "def".
    exposure_condition : string, optional
        Defines the exposure condition of concrete. The default is "Exposed outdoor".
    compressive_strength : string, optional
        Defines the compressive stremght of concrete. The default is "16-23 Mpa".
    structure : string, optional
        Defines the type of structure in which the concrete is used. The default is
        "Wall".
    cement_product : string, optional
        Defined the type of cement-product that is considered (in this case, concrete).
        The default is "concrete".

    Returns
    -------
    Python object
        The Python object contains attributes with the results mentioned in the
        description above.

    """
    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)

    logger.info("cement-test sequence started --->")
    seq.store_signature(locals())

    meta_dict = locals()
    meta_dict["product"] = "concrete"
    meta_dict["activity"] = "use_concrete"
    seq.store_signature(meta_dict)

    # Mass of cement
    seq.read_parameter(
        name="cement_prod_world",
        table="cement_prod_world",
        coords=[year, region],
    )

    seq.read_parameter(
        name="cao_in_clinker",
        table="cao_in_clinker",
        coords=[year, region],
    )

    seq.read_parameter(
        name="c_cl",
        table="c_cl",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="cement_distrib",
        table="cement_distrib",
        coords=[year, region, cement_product],
    )

    seq.read_parameter(
        name="amount_of_addition",
        table="amount_of_addition",
        coords=[year, region, product],
    )

    # Mass clinker
    mass_clinker = seq.elementary.mass_clinker(
        mass_cement=seq.step.cement_prod_world.value, clink_on_cem=seq.step.c_cl.value
    )

    seq.store_result(
        name="mass_clinker",
        value=mass_clinker,
        unit="tonnes",
        year=year,
        lci_flag="use|product|clinker",
    )

    # Calculation of the sponge effect - Approach with detailed equations
    seq.read_parameter(
        name="carb_coeff_env",
        table="carb_coeff_env",
        coords=[year, region, exposure_condition, compressive_strength],
    )

    seq.read_parameter(
        name="carb_coeff_add",
        table="carb_coeff_add",
        coords=[year, region, seq.step.amount_of_addition.value],
    )

    seq.read_parameter(
        name="carb_coeff_co2",
        table="carb_coeff_co2",
        coords=[year, region],
    )

    seq.read_parameter(
        name="carb_coeff_cc",
        table="carb_coeff_cc",
        coords=[year, region],
    )

    # carbonation_rate_concrete
    carbonation_rate = seq.elementary.carbonation_rate(
        carb_coeff_env=seq.step.carb_coeff_env.value,
        carb_coeff_add=seq.step.carb_coeff_add.value,
        carb_coeff_co2=seq.step.carb_coeff_co2.value,
        carb_coeff_cc=seq.step.carb_coeff_cc.value,
    )

    seq.store_result(
        name="carbonation_rate",
        value=carbonation_rate,
        unit="mm/year",
        year=year,
    )

    seq.read_parameter(
        name="expo_use_life",
        table="expo_use_life",
        coords=[year, region],
    )

    carbonation_depth = seq.elementary.carbonation_depth(
        carbonation_rate=seq.step.carbonation_rate.value,
        react_time=lifetime_use_cement,
    )

    seq.store_result(
        name="carbonation_depth",
        value=carbonation_depth,
        unit="mm",
        year=year,
    )

    seq.read_parameter(
        name="cement_on_concrete",
        table="cement_on_concrete",
        coords=[year, region, compressive_strength],
    )

    seq.read_parameter(
        name="thickness_concrete",
        table="thickness_concrete",
        coords=[year, region, structure],
    )

    concrete_carbonated = seq.elementary.concrete_carbonated(
        carbonation_depth=seq.step.carbonation_depth.value,
        cement_on_concrete=seq.step.cement_on_concrete.value,
        thick=seq.step.thickness_concrete.value,
    )

    seq.store_result(
        name="concrete_carbonated",
        value=concrete_carbonated,
        unit="kg",
        year=year,
    )

    seq.read_parameter(
        name="cao_converted_to_caco3",
        table="cao_converted_to_caco3",
        coords=[year, region],
    )

    # Option 1: global value over the full lifetime of concrete
    co2_carbonated_concrete = seq.elementary.co2_carbonated_concrete(
        cement_on_concrete=seq.step.cement_on_concrete.value,
        carbonation_rate=seq.step.carbonation_rate.value,
        clink_on_cem=seq.step.c_cl.value,
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_to_caco3=seq.step.cao_converted_to_caco3.value,
        thick=seq.step.thickness_concrete.value,
        react_time=lifetime_use_cement,
        mass_cement=seq.step.cement_prod_world.value,
        cement_distrib=seq.step.cement_distrib.value,
    )

    # co2_carbonated_concrete_global
    seq.store_result(
        name="co2_carbonated_concrete",
        value=co2_carbonated_concrete,
        unit="kg",
        year=year,
    )

    # Option 2: we want the values for each year over the cement's lifetime
    # loop over the lifetime years:

    list_co2_carbonated_concrete_per_year = []
    year_list = []
    # lifetime_use_cement = seq.step.expo_use_life.value
    for y in list(range(1, lifetime_use_cement + 1)):
        # Calculation of the CO2 absorbed for the current year
        co2_carbonated_concrete_y1 = seq.elementary.co2_carbonated_concrete(
            cement_on_concrete=seq.step.cement_on_concrete.value,
            carbonation_rate=seq.step.carbonation_rate.value,
            clink_on_cem=seq.step.c_cl.value,
            cao_in_clinker=seq.step.cao_in_clinker.value,
            cao_to_caco3=seq.step.cao_converted_to_caco3.value,
            thick=seq.step.thickness_concrete.value,
            react_time=y,
            mass_cement=seq.step.cement_prod_world.value,
            cement_distrib=seq.step.cement_distrib.value,
        )

        # Calculation of the CO2 absorbed for the previous year (so we can make the
        # difference and get the value for each year and not the accumulated value).
        co2_carbonated_concrete_y0 = seq.elementary.co2_carbonated_concrete(
            cement_on_concrete=seq.step.cement_on_concrete.value,
            carbonation_rate=seq.step.carbonation_rate.value,
            clink_on_cem=seq.step.c_cl.value,
            cao_in_clinker=seq.step.cao_in_clinker.value,
            cao_to_caco3=seq.step.cao_converted_to_caco3.value,
            thick=seq.step.thickness_concrete.value,
            react_time=y - 1,
            mass_cement=seq.step.cement_prod_world.value,
            cement_distrib=seq.step.cement_distrib.value,
        )

        list_co2_carbonated_concrete_per_year.append(
            round(co2_carbonated_concrete_y1 - co2_carbonated_concrete_y0, 2)
        )

        year_list.append(year + (y - 1))

    co2_carbonated_concrete_per_year = seq.elementary.co2_carbonated_concrete_per_year(
        df=list_co2_carbonated_concrete_per_year
    )

    seq.store_result(
        name="co2_carbonated_concrete_per_year",
        value=co2_carbonated_concrete_per_year,
        unit="kg",
        year=year_list,
        lci_flag="resource|product|co2",
    )

    logger.info("---> concrete carbonation model finished.")
    return seq.step


####################################################################################
# --------------------- Sequence on carbonation on mortar ------------------------ #
####################################################################################


def carbonation_cement_mortar(
    year=2011,
    lifetime_use_cement=10,
    region="US",
    product="portland",
    uncertainty="def",
    mortar_type="rendering",
    exposure_condition="Exposed outdoor",
    compressive_strength="16-23 Mpa",
    structure="Wall",
    cement_product="mortar",
):
    """
    This sequence function calculates the amount of carbonation that takes place in
    mortar, depending on the lifetime of use. A global result (over the whole
    lifetime) and a yearly result (for each year) is calculated in tonnes of
    CO2-absorbed.

    Parameters
    ----------
    year : integer, optional
        Year of cement production (and by assumption concrete). The default is 2011.
    lifetime_use_cement : integer, optional
        Number of years that the concrete is used. The default is 10.
    region : string, optional
        Region where the concrete is used. The default is "US".
    product : string, optional
        Type of cement that is used to later produce concrete. The default is "portland".
    uncertainty : string, optional
        Defines the type of uncertainty we want to consider. The default is "def".
    mortar_type : string, optional
        Defined the type of mortar that is considered. The default is "rendering".
    exposure_condition : string, optional
        Defines the exposure condition of mortar. The default is "Exposed outdoor".
    compressive_strength : string, optional
        Defines the compressive stremght of mortar. The default is "16-23 Mpa".
    structure : string, optional
        Defines the type of structure in which the mortar is used. The default is
        "Wall".
    cement_product : string, optional
        Defined the type of cement-product that is considered (in this case, mortar).
        The default is "mortar".

    Returns
    -------
    Python object
        The Python object contains attributes with the results mentioned in the
        description above

    """

    # Initalize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)

    logger.info("cement-carbonation-rendering-mortar sequence started --->")
    seq.store_signature(locals())

    meta_dict = locals()
    meta_dict["product"] = "cement_mortar"
    meta_dict["activity"] = "use_mortar"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="cement_prod_world",
        table="cement_prod_world",
        coords=[year, region],
    )

    seq.read_parameter(
        name="cao_in_clinker",
        table="cao_in_clinker",
        coords=[year, region],
    )

    seq.read_parameter(
        name="c_cl",
        table="c_cl",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="cement_distrib",
        table="cement_distrib",
        coords=[year, region, cement_product],
    )

    seq.read_parameter(
        name="type_mortar_use",
        table="type_mortar_use",
        coords=[year, region, mortar_type],
    )

    seq.read_parameter(
        name="carb_coeff_mortar",
        table="carb_coeff_mortar",
        coords=[year, region, product, compressive_strength, exposure_condition],
    )

    seq.read_parameter(
        name="thickness_mortar",
        table="thickness_mortar",
        coords=[year, region, mortar_type],
    )

    seq.read_parameter(
        name="cao_converted_to_caco3",
        table="cao_converted_to_caco3",
        coords=[year, region],
    )

    seq.read_parameter(
        name="expo_use_life",
        table="expo_use_life",
        coords=[year, region],
    )

    # Option 1: global value over the full lifetime of cement
    co2_carbonated_mortar = seq.elementary.co2_carbonated_mortar(
        mass_cement=seq.step.cement_prod_world.value,
        coeff_mortar_on_cement=seq.step.cement_distrib.value,
        ratio_mortar_type=seq.step.type_mortar_use.value,
        carb_coeff_mortar=seq.step.carb_coeff_mortar.value,
        react_time=lifetime_use_cement,
        thick=seq.step.thickness_mortar.value,
        clink_on_cem=seq.step.c_cl.value,
        cao_in_clinker=seq.step.cao_in_clinker.value,
        cao_to_caco3=seq.step.cao_converted_to_caco3.value,
    )

    seq.store_result(
        name="co2_carbonated_mortar",
        value=co2_carbonated_mortar,
        unit="kg",
        year=year,
        lci_flag="resource|product|co2",
    )

    # Option 2: we want the values for each year over the cement's lifetime
    # loop over the lifetime years:

    list_co2_carbonated_mortar_per_year = []
    year_list = []
    for y in list(range(1, lifetime_use_cement + 1)):
        # Calculation of the CO2 absorbed for the current year
        co2_carbonated_mortar_y1 = seq.elementary.co2_carbonated_mortar(
            mass_cement=seq.step.cement_prod_world.value,
            coeff_mortar_on_cement=seq.step.cement_distrib.value,
            ratio_mortar_type=seq.step.type_mortar_use.value,
            carb_coeff_mortar=seq.step.carb_coeff_mortar.value,
            react_time=y,
            thick=seq.step.thickness_mortar.value,
            clink_on_cem=seq.step.c_cl.value,
            cao_in_clinker=seq.step.cao_in_clinker.value,
            cao_to_caco3=seq.step.cao_converted_to_caco3.value,
        )

        # Calculation of the CO2 absorbed for the previous year (so we can make the
        # difference and get the value for each year and not the accumulated value).
        co2_carbonated_mortar_y0 = seq.elementary.co2_carbonated_mortar(
            mass_cement=seq.step.cement_prod_world.value,
            coeff_mortar_on_cement=seq.step.cement_distrib.value,
            ratio_mortar_type=seq.step.type_mortar_use.value,
            carb_coeff_mortar=seq.step.carb_coeff_mortar.value,
            react_time=y - 1,
            thick=seq.step.thickness_mortar.value,
            clink_on_cem=seq.step.c_cl.value,
            cao_in_clinker=seq.step.cao_in_clinker.value,
            cao_to_caco3=seq.step.cao_converted_to_caco3.value,
        )
        list_co2_carbonated_mortar_per_year.append(
            round(
                co2_carbonated_mortar_y1 - co2_carbonated_mortar_y0,
                2,
            )
        )
        year_list.append(year + (y - 1))

    co2_carbonated_mortar_per_year = seq.elementary.co2_carbonated_mortar_per_year(
        df=list_co2_carbonated_mortar_per_year
    )

    seq.store_result(
        name="co2_carbonated_mortar_per_year",
        value=co2_carbonated_mortar_per_year,
        unit="kg",
        year=year_list,
        lci_flag="resource|product|co2",
    )

    logger.info("---> mortar carbonation model finished.")
    return seq.step
