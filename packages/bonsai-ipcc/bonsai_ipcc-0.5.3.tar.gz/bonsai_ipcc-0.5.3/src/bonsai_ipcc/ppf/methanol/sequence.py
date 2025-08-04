import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def methanol_recipe_emissions_tier1(
    year=2006,
    region="World",
    activity="csr_a_natural_gas",
    product="methanol",
    uncertainty="def",
):
    """Estimate the inputs and outputs of annual methanol production by year, region, activity, and product for specific production pathways and feedstock requirements.

    Parameters
    ----------
    year : int, optional
        Year under study (default is 2006).
    region : str, optional
        Region under study (default is "World").
    activity : str, optional
        Production activity under study (default is "csr_a_natural_gas").
    product : str, optional
        Product under study (default is "methanol").
    uncertainty : str, optional
        Uncertainty type, e.g., 'def', 'min', 'max', or 'sample' (default is "def").

    Returns
    -------
    Sequence
        Includes the results of each step of the sequence.
    """

    # Initialize sequence instance with required parameters
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Methanol sequence started --->")
    seq.store_signature(locals())

    meta_dict = locals()
    seq.store_signature(meta_dict)

    # Determine feedstocktype and key based on activity
    feedstocktype = None  # Default to None
    key = None  # Default to None

    if activity.startswith("gasify_"):
        # Special case for gasify_bio-related activities
        feedstocktype = activity.replace("gasify_", "")
        key = "gasify_bio"
        logger.debug(
            f"Matched gasify activity: {activity}, feedstocktype set to: {feedstocktype}, key set to: {key}"
        )
    elif activity == "PtM":
        # Special case for PtM
        key = activity  # Key is the same as activity
        feedstocktype = None
    elif activity == "direct_co2_electrolysis":
        # Special case for direct_co2_electrolysis
        key = activity  # Key is the same as activity
        feedstocktype = None
    elif activity.startswith("csr_w_nh3"):
        # Special case for csr_w_nh3
        key = "csr_w_nh3"
        feedstocktype = activity.replace("csr_w_nh3_", "")
    else:
        # General case: extract key and feedstocktype from activity
        parts = activity.split("_", 2)  # Split into up to three parts
        if len(parts) > 1:
            if (
                parts[0] == "csr" and len(parts) > 2
            ):  # Handle csr_a, csr_c1, csr_w cases
                key = f"{parts[0]}_{parts[1]}"  # Combine first two parts as key
                feedstocktype = "_".join(
                    parts[2:]
                )  # Remaining part is the feedstocktype
            elif parts[0] == "co2":  # Special case for co2_hydrogenation
                key = f"{parts[0]}_{parts[1]}"  # Combine first two parts as key
                feedstocktype = (
                    parts[2] if len(parts) > 2 else None
                )  # Only set if exists
            else:
                key = parts[0]  # First part is the key
                feedstocktype = "_".join(parts[1:])  # Remaining parts as feedstocktype
            logger.debug(
                f"Matched activity: {activity}, feedstocktype set to: {feedstocktype}, key set to: {key}"
            )

    if feedstocktype is None or key is None:
        logger.warning(
            f"Unable to determine feedstocktype or key for activity: {activity}"
        )

    # Read parameters from the database
    seq.read_parameter(
        name="pp_i",
        table="pp_i",
        coords=[year, region, product],
    )

    # Read feedstock and syngas consumption in process using LCI coefficients
    seq.read_parameter(
        name="pp_share_i_j",
        table="pp_share_i_j",
        coords=[year, region, product, key],
    )

    seq.read_parameter(
        name="pp_share_i_j_k",
        table="pp_share_i_j_k",
        coords=[year, region, product, key, feedstocktype],
    )

    pp_i_j_k = seq.elementary.pp_i_j_k(
        pp_i=seq.step.pp_i.value,
        pp_share_i_j=seq.step.pp_share_i_j.value,
        pp_share_i_j_k=seq.step.pp_share_i_j_k.value,
    )

    seq.store_result(
        name="pp_i_j_k",
        value=pp_i_j_k,
        unit="t/yr",
        year=year,
        lci_flag="supply|product|methanol_from_{activity}",
        eq_name="pp_i_j_k",
    )

    seq.read_parameter(
        name="syngas_use_per_meoh",
        table="syngas_use_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="electricity_use_per_meoh",
        table="electricity_use_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="steam_use_per_meoh",
        table="steam_use_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="heat_use_per_meoh",
        table="heat_use_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="co2_emissions_per_meoh",
        table="co2_emissions_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="ch4_emissions_per_meoh",
        table="ch4_emissions_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="ch4_fugitive_emissions_per_meoh",
        table="ch4_fugitive_emissions_per_meoh",
        coords=[year, region, activity],
    )

    seq.read_parameter(
        name="gaf",
        table="gaf",
        coords=[year, region],
    )

    # Check if feedstocktype is in the allowed list
    expected_feedstocktypes = {
        "natural_gas",
        "natural_gas_co2",
        "methane",
        "oil",
        "petro_oil",
        "naphtha",
        "light_naphtha",
        "full_range_naphtha",
        "fuel_oil",
        "light_fuel_oil",
        "heavy_fuel_oil",
        "coal",
        "hard_coal",
        "anthracite",
        "sub_bituminous_coal",
        "other_bituminous_coal",
        "lignite",
        "coke_oven_gas",
    }

    if feedstocktype in expected_feedstocktypes:
        seq.read_parameter(
            name="n_k", table="n_k", coords=[year, region, feedstocktype]
        )
        logger.info(f"feedstocktype: {feedstocktype} n_k: {seq.step.n_k.value}")
        seq.read_parameter(
            name="chemical_synthesis_efficiency_k",
            table="chemical_synthesis_efficiency_k",
            coords=[year, region, feedstocktype],
        )

        seq.read_parameter(
            name="syngas_production_efficiency_k",
            table="syngas_production_efficiency_k",
            coords=[year, region, feedstocktype],
        )

        if feedstocktype in {"natural_gas", "natural_gas_co2", "lng", "coke_oven_gas"}:
            seq.read_parameter(
                name="product_density",
                table="product_density",
                coords=[year, region, feedstocktype],
            )

    # Read fossil-based feedstock requirements data
    seq.read_parameter(
        name="feedstock_use_per_meoh",
        table="feedstock_use_per_meoh",
        coords=[year, region, activity],
    )

    # Calculate steam, electricity, and feedstock requirements
    lci_coefficients = {
        f"{feedstocktype}": (
            seq.step.feedstock_use_per_meoh.value
            if seq.step.feedstock_use_per_meoh.value is not None
            else 0
        ),
        "steam": (
            seq.step.steam_use_per_meoh.value
            if seq.step.steam_use_per_meoh.value is not None
            else 0
        ),
        "syngas": (
            seq.step.syngas_use_per_meoh.value
            if seq.step.syngas_use_per_meoh.value is not None
            else 0
        ),
        "heat": (
            seq.step.heat_use_per_meoh.value
            if seq.step.heat_use_per_meoh.value is not None
            else 0
        ),
        "electricity": (
            seq.step.electricity_use_per_meoh.value
            if seq.step.electricity_use_per_meoh.value is not None
            else 0
        ),
    }

    # Create a list of keys from the dictionary
    product_list = list(lci_coefficients.keys())

    #######################################################################################
    # Calculate the by-product supply from the process
    #######################################################################################
    # add all by-products to production process
    # Always continue with the rest of the code, even if by-product supply is not calculated
    if uncertainty in ["def", "min", "max", "sample"]:
        activitylist = seq.get_dimension_levels(
            year,
            region,
            table="waste_per_meoh",
            uncert=uncertainty,
        )
    else:
        activitylist = seq.get_dimension_levels(
            year,
            region,
            uncert="def",
            table="waste_per_meoh",
        )

    logger.info(f"activity list: {set(activitylist)}")

    if activity in activitylist:
        if uncertainty in ["def", "min", "max", "sample"]:
            wastetype_list = seq.get_dimension_levels(
                year,
                region,
                activity,
                uncert=uncertainty,
                table="waste_per_meoh",
            )
        else:
            wastetype_list = seq.get_dimension_levels(
                year,
                region,
                activity,
                uncert="def",
                table="waste_per_meoh",
            )

        logger.info(f"wastetype list: {set(wastetype_list)}")

        for wastetype in wastetype_list:
            # read supply coefficient
            seq.read_parameter(
                name=f"waste_per_meoh_xxx_{wastetype}_xxx",
                table="waste_per_meoh",
                coords=[year, region, activity, wastetype],
            )
            # calc supply
            value = seq.elementary.by_product_supply(
                pp_i=seq.step.pp_i_j_k.value,
                lci_coefficient=getattr(
                    getattr(seq.step, f"waste_per_meoh_xxx_{wastetype}_xxx"),
                    "value",
                ),
            )
            # store supply
            seq.store_result(
                name=f"waste_per_meoh_xxx_{wastetype}_xxx",
                value=value,
                unit="t/yr",
                lci_flag=f"supply|waste|{wastetype}",
                eq_name="by_product_supply",
            )
    else:
        logger.info(
            f"No waste supply calculation using LCI coefficients for activity: {activity}"
        )

    if activity in activitylist:
        if uncertainty in ["def", "min", "max", "sample"]:
            byproduct_list = seq.get_dimension_levels(
                year,
                region,
                activity,
                uncert=uncertainty,
                table="byproduct_supply_per_meoh",
            )
        else:
            byproduct_list = seq.get_dimension_levels(
                year,
                region,
                activity,
                uncert="def",
                table="byproduct_supply_per_meoh",
            )

        logger.info(f"byproduct list: {set(byproduct_list)}")

        for by_product in byproduct_list:
            # read supply coefficient
            seq.read_parameter(
                name=f"byproduct_supply_per_meoh_xxx_{by_product}_xxx",
                table="byproduct_supply_per_meoh",
                coords=[year, region, activity, by_product],
            )
            # calc supply
            value = seq.elementary.by_product_supply(
                pp_i=seq.step.pp_i_j_k.value,
                lci_coefficient=getattr(
                    getattr(
                        seq.step, f"byproduct_supply_per_meoh_xxx_{by_product}_xxx"
                    ),
                    "value",
                ),
            )
            # store supply
            seq.store_result(
                name=f"by_product_supply_xxx_{by_product}_xxx",
                value=value,
                unit="t/yr",
                lci_flag=f"supply|product|{by_product}",
                eq_name="by_product_supply",
            )
    else:
        logger.info(
            f"No by-product supply calculation using LCI coefficients for activity: {activity}"
        )
    # Continue with the rest of the code regardless of the above

    ######################################################################################
    # Calculate CO2 and CH4 emissions
    ######################################################################################
    # tier 1 CO2 emissions
    eco2_tier1 = seq.elementary.eco2_tier1(
        pp_i=seq.step.pp_i_j_k.value,
        ef=seq.step.co2_emissions_per_meoh.value,
        gaf=seq.step.gaf.value,
    )

    seq.store_result(
        name="co2_methanol_total_tier1_",
        value=eco2_tier1,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
        eq_name="eco2_tier1",
    )

    # Process vent CH4 emissions
    ch4_vent = seq.elementary.ech4_process_vent(
        pp_i=seq.step.pp_i_j_k.value,
        ef=seq.step.ch4_emissions_per_meoh.value,
    )

    seq.store_result(
        name="ch4_vent",
        value=ch4_vent,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
        eq_name="ech4_process_vent",
    )

    # Fugitive CH4 emissions
    ch4_fugitive = seq.elementary.ech4_fugitive(
        pp_i=seq.step.pp_i_j_k.value,
        ef=seq.step.ch4_fugitive_emissions_per_meoh.value,
    )

    seq.store_result(
        name="ch4_fugitive",
        value=ch4_fugitive,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
        eq_name="ech4_fugitive",
    )

    # tier 1 CH4 emissions
    ech4_tier1 = seq.elementary.ech4_tier1(
        ech4_fugitive=seq.step.ch4_vent.value,
        ech4_process_vent=seq.step.ch4_fugitive.value,
    )

    seq.store_result(
        name="ch4_methanol_total_tier1_",
        value=ech4_tier1,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CH4",
        eq_name="ech4_tier1",
    )

    if activity in (
        "csr_a_natural_gas",
        "csr_a_coke_oven_gas",
        "csr_w_nh3_natural_gas",
    ):
        # Conventional Steam Reforming, without primary reformer (a)

        # Get use data
        result = seq.elementary.adjusted_reverse_csr_with_TCs(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
            n=seq.step.n_k.value,
            sg_efficiency=seq.step.syngas_production_efficiency_k.value,
            ms_efficiency=seq.step.chemical_synthesis_efficiency_k.value,
        )

        logger.debug(
            f"adjusted_reverse_csr_with_TCs results: ch4_input={result[0]}, h2o_input={result[1]}, h2o_output={result[2]}, co2_input={result[3]}, TCs={result[-1]}"
        )

        seq.store_result(
            name="ch4_input",
            value=result[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        seq.store_result(
            name="h2o_input",
            value=result[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        seq.store_result(
            name="co2_input",
            value=result[3],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_dioxide",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        # Get supply data
        seq.store_result(
            name="h2o_output",
            value=result[2],
            unit="t/yr",
            year=year,
            lci_flag=f"supply|product|water_from_{activity}",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        # Transfer coefficients
        transfer_coeffs = result[-1]

        # Define mapping from coefficient keys to input products
        coeff_to_input = {
            "CHn_meoh": "methane",
            "CHn_water": "methane",
            "H2O_meoh": "water",
            "H2O_water": "water",
            "CO2_meoh": "carbon_dioxide",
            "CO2_water": "carbon_dioxide",
        }

        # Define mapping for reference outputs
        coeff_to_output = {
            "CHn_meoh": "methanol",
            "CHn_water": "water",
            "H2O_meoh": "methanol",
            "H2O_water": "water",
            "CO2_meoh": "methanol",
            "CO2_water": "water",
        }

        # Store all transfer coefficients using a loop
        for coeff_key, value in transfer_coeffs.items():
            # Skip if value is None or not in our mapping
            if value is None or coeff_key not in coeff_to_input:
                continue

            # Get input product and reference output for lci_flag
            input_product = coeff_to_input.get(coeff_key)
            reference_output = coeff_to_output.get(coeff_key)

            seq.store_result(
                name=f"product_transf_coeff_{coeff_key.lower()}",
                value=value,
                unit="%",
                year=year,
                # lci_flag=f"transf_coeff|product|{input_product}-{reference_output}",
                eq_name="adjusted_reverse_csr_with_TCs",
            )

        # Calculating syngas requirements
        (
            co_output,
            h2_output,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.syngas_from_csr(
            CHn_tonnes=seq.step.ch4_input.value,
            H2O_tonnes=seq.step.h2o_input.value,
            n=seq.step.n_k.value,
        )

        # Store results for inputs and outputs
        seq.store_result(
            name="co_output",
            value=co_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="syngas_from_csr",
        )

        seq.store_result(
            name="syngas_input",
            value=(h2_output + co_output),
            unit="t/yr",
            year=year,
            lci_flag="use|product|syngas",
            eq_name="syngas_from_csr",
        )

        # Read feedstock and syngas consumption in process using LCI coefficients
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        ng, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name=f"{feedstocktype}_input_lci",
            value=ng,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Calculating natural gas requirements in mass and volume using stoichiometric equation
        substance = "methane"
        seq.read_parameter(
            name="gas_composition",
            table="gas_composition",
            coords=[year, region, feedstocktype, substance],
        )

        ng_value_mass, _ = seq.elementary.gas_requirements(
            tons_CH4=seq.step.ch4_input.value,
            density_gas=seq.step.product_density.value,
            CH4_vol_percent=seq.step.gas_composition.value,
        )

        # Store natural gas requirements
        seq.store_result(
            name="natural_gas_input_calc",
            value=ng_value_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="gas_requirements",
        )

    elif activity in [
        "csr_b_natural_gas",
        "csr_c1_natural_gas",
        "csr_c2_natural_gas",
        "csr_c4_natural_gas",
    ]:
        # Conventional Steam Reforming, with primary reformer (b)
        # Conventional Steam Reforming, Lurgi Conventional process (c1)
        # Conventional Steam Reforming, Lurgi Low Pressure Process (c2)
        # Conventional Steam Reforming, Lurgi Mega Methanol Process (c4)

        # Calculate the inputs and outputs of methanol production via Conventional Steam Reforming (CSR)
        results = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
            n=seq.step.n_k.value,
        )

        # Store results for inputs and outputs
        seq.store_result(
            name="co_input",
            value=results[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=results[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="co_input",
            value=results[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="syngas_input",
            value=results[0] + results[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        # Calculating inputs of syngas production
        (
            co2_output,
            h2o_input,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.water_gas_shift_from_CO_H2(
            CO_tonnes=seq.step.co2_input.value,
            H2_tonnes=seq.step.h2_input.value,
            n=seq.step.n_k.value,
        )

        # Store syngas requirement results
        seq.store_result(
            name="co2_input",
            value=co2_output,
            unit="t/yr",
            year=year,
            lci_flag=f"supply|product|carbon_dioxide_from_{activity}",
            eq_name="water_gas_shift_from_CO_H2",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="water_gas_shift_from_CO_H2",
        )

        seq.store_result(
            name="limiting_reagent",
            value=limiting_reagent,
            unit="None",
            year=year,
            eq_name="water_gas_shift_from_CO_H2",
        )

        seq.store_result(
            name="excess_reagent",
            value=excess_reagent,
            unit="None",
            year=year,
            eq_name="water_gas_shift_from_CO_H2",
        )

        seq.store_result(
            name="excess_tonnes",
            value=excess_tonnes,
            unit="t/yr",
            year=year,
            eq_name="water_gas_shift_from_CO_H2",
        )

        # Calculating inputs of steam reforming
        (
            ch4_input,
            h2o_input,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.csr_input_requirements(
            CO_tonnes=seq.step.co_input.value,
            H2_tonnes=seq.step.h2_input.value,
            n=seq.step.n_k.value,
        )

        # Store syngas requirement results
        seq.store_result(
            name="ch4_input",
            value=ch4_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="csr_input_requirements",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="csr_input_requirements",
        )

        seq.store_result(
            name="limiting_reagent",
            value=limiting_reagent,
            unit="None",
            year=year,
            eq_name="csr_input_requirements",
        )

        seq.store_result(
            name="excess_reagent",
            value=excess_reagent,
            unit="None",
            year=year,
            eq_name="csr_input_requirements",
        )

        seq.store_result(
            name="excess_tonnes",
            value=excess_tonnes,
            unit="t/yr",
            year=year,
            eq_name="csr_input_requirements",
        )

        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        ng, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name=f"{feedstocktype}_input_lci",
            value=ng,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Read natural gas composition (based on stoichiometric equation)
        substance = "methane"
        seq.read_parameter(
            name="gas_composition",
            table="gas_composition",
            coords=[year, region, feedstocktype, substance],
        )

        ng_value_mass, _ = seq.elementary.gas_requirements(
            tons_CH4=seq.step.ch4_input.value,
            density_gas=seq.step.product_density.value,
            CH4_vol_percent=seq.step.gas_composition.value,
        )

        # Store natural gas requirements
        seq.store_result(
            name="natural_gas_input_calc",
            value=ng_value_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="gas_requirements",
        )

    elif activity == "csr_c1_natural_gas_co2":
        # Conventional Steam Reforming, Lurgi Conventional process (c1)

        result = seq.elementary.adjusted_reverse_csr_with_TCs(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
            n=seq.step.n_k.value,
            sg_efficiency=seq.step.syngas_production_efficiency_k.value,
            ms_efficiency=seq.step.chemical_synthesis_efficiency_k.value,
        )

        seq.store_result(
            name="ch4_input",
            value=result[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        seq.store_result(
            name="h2o_input",
            value=result[2],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        seq.store_result(
            name="h2o_output",
            value=result[3],
            unit="t/yr",
            year=year,
            lci_flag=f"supply|by_product|water_from_{activity}",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        seq.store_result(
            name="co2_input",
            value=result[4],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_dioxide",
            eq_name="adjusted_reverse_csr_with_TCs",
        )

        # Transfer coefficients
        transfer_coeffs = result[-1]

        # Define mapping from coefficient keys to input products
        coeff_to_input = {
            "CHn_meoh": "methane",
            "CHn_water": "methane",
            "H2O_meoh": "water",
            "H2O_water": "water",
            "CO2_meoh": "carbon_dioxide",
            "CO2_water": "carbon_dioxide",
        }

        # Define mapping for reference outputs
        coeff_to_output = {
            "CHn_meoh": "methanol",
            "CHn_water": "water",
            "H2O_meoh": "methanol",
            "H2O_water": "water",
            "CO2_meoh": "methanol",
            "CO2_water": "water",
        }

        # Store all transfer coefficients using a loop
        for coeff_key, value in transfer_coeffs.items():
            # Skip if value is None or not in our mapping
            if value is None or coeff_key not in coeff_to_input:
                continue

            # Get input product and reference output for lci_flag
            input_product = coeff_to_input.get(coeff_key)
            reference_output = coeff_to_output.get(coeff_key)

            seq.store_result(
                name=f"product_transf_coeff_{coeff_key.lower()}",
                value=value,
                unit="%",
                year=year,
                # lci_flag=f"transf_coeff|product|{input_product}-{reference_output}",
                eq_name="adjusted_reverse_csr_with_TCs",
            )

        # Calculating syngas requirements
        (
            co_output,
            h2_output,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.syngas_from_csr(
            CHn_tonnes=seq.step.ch4_input.value,
            H2O_tonnes=seq.step.h2o_input.value,
            n=seq.step.n_k.value,
        )

        # Store results for inputs and outputs
        seq.store_result(
            name="co_output",
            value=co_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="syngas_from_csr",
        )

        seq.store_result(
            name="syngas_input",
            value=(h2_output + co_output),
            unit="t/yr",
            year=year,
            lci_flag="use|product|syngas",
            eq_name="syngas_from_csr",
        )

        seq.read_parameter(
            name="syngas_use_per_meoh",
            table="syngas_use_per_meoh",
            coords=[year, region, activity],
        )

        seq.read_parameter(
            name="electricity_use_per_meoh",
            table="electricity_use_per_meoh",
            coords=[year, region, activity],
        )

        seq.read_parameter(
            name="steam_use_per_meoh",
            table="steam_use_per_meoh",
            coords=[year, region, activity],
        )

        # Calculate steam, electricity, and feedstock requirements
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        ng, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name="natural_gas_input_lci",
            value=ng,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        substance = "methane"
        seq.read_parameter(
            name="gas_composition",
            table="gas_composition",
            coords=[year, region, feedstocktype, substance],
        )

        ng_value_mass, _ = seq.elementary.gas_requirements(
            tons_CH4=seq.step.ch4_input.value,
            density_gas=seq.step.product_density.value,
            CH4_vol_percent=seq.step.gas_composition.value,
        )

        # Store natural gas requirements
        seq.store_result(
            name="natural_gas_input_calc",
            value=ng_value_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="gas_requirements",
        )

    elif activity in ("atr_natural_gas", "atr_naphtha", "atr_lng"):
        # Autothermal Reforming (ATR)

        # Reverse methanol synthesis route A
        co_input, h2_input = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value
        )

        # Store CO and H2 inputs
        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=h2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        # Syngas production from ATR
        ch4_input, h2o_input, o2_input = seq.elementary.syngas_production_from_atr(
            CO_tonnes=seq.step.co_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        # Store syngas inputs
        seq.store_result(
            name="ch4_input",
            value=ch4_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="syngas_production_from_atr",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="syngas_production_from_atr",
        )

        seq.store_result(
            name="o2_input",
            value=o2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|oxygen",
            eq_name="syngas_production_from_atr",
        )

        # Create a list of keys from the dictionary
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        ng, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name="natural_gas_input_lci",
            value=ng,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Read natural gas composition (based on stoichiometric equation)
        if feedstocktype == "natural_gas":
            seq.read_parameter(
                name="gas_composition",
                table="gas_composition",
                coords=[year, region, feedstocktype, "methane"],
            )

            ng_value_mass, _ = seq.elementary.gas_requirements(
                tons_CH4=seq.step.ch4_input.value,
                density_gas=seq.step.product_density.value,
                CH4_vol_percent=seq.step.gas_composition.value,
            )

            # Store natural gas requirements
            seq.store_result(
                name="natural_gas_input_calc",
                value=ng_value_mass,
                unit="t/yr",
                year=year,
                lci_flag=f"use|product|{product_list[0]}",
                eq_name="gas_requirements",
            )

    elif activity == "csr_c3_natural_gas":
        # Combined Steam Reforming, Lurgi Combined Process (c3)

        seq.read_parameter(
            name="product_density",
            table="product_density",
            coords=[year, region, activity],
        )

        # Reverse combined reforming
        (
            ch4_input,
            o2_input,
            co_input,
            h2_input,
        ) = seq.elementary.reverse_combined_reforming(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
        )

        # Store inputs
        seq.store_result(
            name="ch4_input",
            value=ch4_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="reverse_combined_reforming",
        )

        seq.store_result(
            name="o2_input",
            value=o2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|oxygen",
            eq_name="reverse_combined_reforming",
        )

        seq.store_result(
            name="co_input",
            value=co_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_combined_reforming",
        )

        seq.store_result(
            name="h2_output",
            value=h2_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_combined_reforming",
        )

        # Read feedstock consumption per tonnes of methanol parameter
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        ng, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name="natural_gas_input_lci",
            value=ng,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Calculating natural gas requirements in mass and volume using stoichiometric equation

        # Read natural gas composition (based on stoichiometric equation)
        substance = "methane"
        seq.read_parameter(
            name="gas_composition",
            table="gas_composition",
            coords=[year, region, feedstocktype, substance],
        )

        ng_value_mass, _ = seq.elementary.gas_requirements(
            tons_CH4=seq.step.ch4_input.value,
            density_gas=seq.step.product_density.value,
            CH4_vol_percent=seq.step.gas_composition.value,
        )

        # Store natural gas requirements
        seq.store_result(
            name="natural_gas_input_calc",
            value=ng_value_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="gas_requirements",
        )

    elif activity in [
        "pox_anthracite",
        "pox_oil",
        "pox_lignite",
        "pox_light_fuel_oil",
        "pox_heavy_fuel_oil",
    ]:
        # Partial oxidation process (d)
        result = seq.elementary.adjusted_reverse_pox_with_TCs(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
            n=seq.step.n_k.value,
            sg_efficiency=seq.step.syngas_production_efficiency_k.value,
            ms_efficiency=seq.step.chemical_synthesis_efficiency_k.value,
        )

        seq.store_result(
            name="ch4_input",
            value=result[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="adjusted_reverse_pox_with_TCs",
        )

        seq.store_result(
            name="o2_input",
            value=result[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|oxygen",
            eq_name="adjusted_reverse_pox_with_TCs",
        )

        seq.store_result(
            name="h2o_input",
            value=result[2],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="adjusted_reverse_pox_with_TCs",
        )

        seq.store_result(
            name="co2_output",
            value=result[3],
            unit="t/yr",
            year=year,
            lci_flag=f"supply|product|carbon_dioxide_from_{activity}",
            eq_name="adjusted_reverse_pox_with_TCs",
        )

        # Calculating syngas requirements
        (
            co_output,
            h2_output,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.syngas_from_pox(
            CHn_tonnes=seq.step.ch4_input.value,
            O2_tonnes=seq.step.o2_input.value,
            n=seq.step.n_k.value,
        )

        seq.store_result(
            name="co_input",
            value=co_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="syngas_from_pox",
        )

        seq.store_result(
            name="h2_input",
            value=h2_output,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="syngas_from_pox",
        )

        seq.store_result(
            name="syngas",
            value=(co_output + h2_output),
            unit="t/yr",
            year=year,
            lci_flag="use|product|syngas",
            eq_name="syngas_from_pox",
        )

        seq.store_result(
            name="limiting_reagent",
            value=limiting_reagent,
            unit="None",
            year=year,
            eq_name="syngas_from_pox",
        )

        seq.store_result(
            name="excess_reagent",
            value=excess_reagent,
            unit="None",
            year=year,
            eq_name="syngas_from_pox",
        )

        seq.store_result(
            name="excess_tonnes",
            value=excess_tonnes,
            unit="t/yr",
            year=year,
            eq_name="syngas_from_pox",
        )

        # Transfer coefficients
        transfer_coeffs = result[-1]

        # Define mapping from coefficient keys to input products
        coeff_to_input = {
            "CHn_meoh": "methane",
            "CHn_co2": "methane",
            "CHn_unreacted": "methane",
            "O2_meoh": "oxygen",
            "O2_co2": "oxygen",
            "O2_unreacted": "oxygen",
            "H2O_meoh": "water",
            "H2O_co2": "water",
            "H2O_unreacted": "water",
        }

        # Define mapping for reference outputs
        coeff_to_output = {
            "CHn_meoh": "methanol",
            "CHn_co2": "carbon_dioxide",
            "CHn_unreacted": "unreacted_feed",
            "O2_meoh": "methanol",
            "O2_co2": "carbon_dioxide",
            "O2_unreacted": "unreacted_feed",
            "H2O_meoh": "methanol",
            "H2O_co2": "carbon_dioxide",
            "H2O_unreacted": "unreacted_feed",
        }

        # Store all transfer coefficients using a loop
        for coeff_key, value in transfer_coeffs.items():
            # Skip if value is None or not in our mapping
            if value is None or coeff_key not in coeff_to_input:
                continue

            # Get input product and reference output for lci_flag
            input_product = coeff_to_input.get(coeff_key)
            reference_output = coeff_to_output.get(coeff_key)

            seq.store_result(
                name=f"product_transf_coeff_{coeff_key.lower()}",
                value=value,
                unit="%",
                year=year,
                # lci_flag=f"transf_coeff|product|{input_product}-{reference_output}",
                eq_name="adjusted_reverse_pox_with_TCs",
            )

        # Calculate steam, electricity, and feedstock requirements
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        anthracite, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name=f"{activity}_input",
            value=anthracite,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[0]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Read coal gas composition (based on stoichiometric equation)
        # Only run this calculation if feedstocktype is any of the coal types and coal
        coal_types = {
            "coal",
            "anthracite",
            "sub_bituminous_coal",
            "other_bituminous_coal",
            "lignite",
        }
        if feedstocktype in coal_types:
            seq.read_parameter(
                name="coal_composition",
                table="coal_composition",
                coords=[year, region, feedstocktype, "carbon"],
            )

            coal_mass = seq.elementary.coal_requirements(
                tons_CH4=seq.step.ch4_input.value,
                carbon_fraction_coal=seq.step.coal_composition.value,
            )

            # Store natural gas requirements
            seq.store_result(
                name=f"{activity}_input_calc",
                value=coal_mass,
                unit="t/yr",
                year=year,
                lci_flag=f"use|product|{activity}",
                eq_name="coal_requirements",
            )

    elif activity == "cgt_anthracite":
        # Coal gasification technology

        # Get use data
        co_input, h2a_input = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value
        )

        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        co2_input, h2b_input = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value
        )

        seq.store_result(
            name="co2_input",
            value=co2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_doixide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=h2a_input + h2b_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        (
            co_input,
            h2o_input,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.reverse_water_gas_shift(
            CO2_tonnes=seq.step.co2_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_water_gas_shift",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="reverse_water_gas_shift",
        )

        (
            carbon_input,
            o2_input,
            h2o_input,
        ) = seq.elementary.required_inputs_for_gasification(
            CO_tonnes=seq.step.co_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        seq.store_result(
            name="carbon_input",
            value=carbon_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon",
            eq_name="required_inputs_for_gasification",
        )

        seq.store_result(
            name="o2_input",
            value=o2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|resource|oxygen",
            eq_name="required_inputs_for_gasification",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="required_inputs_for_gasification",
        )

        result = seq.elementary.csr_input_requirements(
            CO_tonnes=seq.step.co_input.value, H2_tonnes=seq.step.h2_input.value
        )

        seq.store_result(
            name="ch4_input",
            value=result[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="csr_input_requirements",
        )

        # Calculate steam, electricity, and feedstock requirements
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        coal, steam, syngas, heat, elec = requirements.values()

        seq.store_result(
            name=f"{activity}_input",
            value=coal,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{activity}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Read coal gas composition (based on stoichiometric equation)
        seq.read_parameter(
            name="coal_composition",
            table="coal_composition",
            coords=[year, region, feedstocktype, "carbon"],
        )

        coal_mass = seq.elementary.coal_requirements(
            tons_CH4=seq.step.ch4_input.value,
            carbon_fraction_coal=seq.step.coal_composition.value,
        )

        # Store natural gas requirements
        seq.store_result(
            name=f"{activity}_input_calc",
            value=coal_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{activity}",
            eq_name="coal_requirements",
        )

    elif activity == "cct_coke_oven_gas":
        # Coal coking technology (CCT)

        # Get use data
        co_input, h2_input = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value
        )

        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=h2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="syngas_input",
            value=co_input + h2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|syngas",
            eq_name="reverse_co_hydrogenation",
        )

        result = seq.elementary.csr_input_requirements(
            CO_tonnes=seq.step.co_input.value, H2_tonnes=seq.step.h2_input.value
        )

        seq.store_result(
            name="ch4_input",
            value=result[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|methane",
            eq_name="csr_input_requirements",
        )

        seq.store_result(
            name="h2o_input",
            value=result[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="csr_input_requirements",
        )

        # Calculate steam, heat, electricity, and feedstock requirements
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        cog, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name=f"{feedstocktype}_input_lci",
            value=cog,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{activity}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

        # Calculating coke oven gas requirements in mass and volume using stoichiometric equation

        # Read coke oven gas composition (based on stoichiometric equation)
        seq.read_parameter(
            name="gas_composition",
            table="gas_composition",
            coords=[year, region, feedstocktype, "methane"],
        )

        cog_value_mass, _ = seq.elementary.gas_requirements(
            tons_CH4=seq.step.ch4_input.value,
            density_gas=seq.step.product_density.value,
            CH4_vol_percent=seq.step.gas_composition.value,
        )

        # Store coke oven gas requirements
        seq.store_result(
            name=f"{activity}_input_calc",
            value=cog_value_mass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{activity}",
            eq_name="gas_requirements",
        )

    elif activity in [
        "gasify_agric_residues",
        "gasify_forest_residues",
        "gasify_msw",
    ]:
        # TODO: check if this is correct, apply more suitable stoichiometric equations for different  biomass feedstocks
        # Biomass gasification technology

        # Get use data
        co2_input, h2_input = seq.elementary.reverse_co_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value
        )

        seq.store_result(
            name="co2_input",
            value=co2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_dioxide",
            eq_name="reverse_co_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=h2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co_hydrogenation",
        )

        (
            co_input,
            h2o_input,
            limiting_reagent,
            excess_reagent,
            excess_tonnes,
        ) = seq.elementary.reverse_water_gas_shift(
            CO2_tonnes=seq.step.co2_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        seq.store_result(
            name="co_input",
            value=co_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_water_gas_shift",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="reverse_water_gas_shift",
        )

        (
            carbon_input,
            o2_input,
            h2o_input,
        ) = seq.elementary.required_inputs_for_gasification(
            CO_tonnes=seq.step.co_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        seq.store_result(
            name="carbon_input",
            value=carbon_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon",
            eq_name="required_inputs_for_gasification",
        )

        seq.store_result(
            name="o2_input",
            value=o2_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|oxygen",
            eq_name="required_inputs_for_gasification",
        )

        seq.store_result(
            name="h2o_input",
            value=h2o_input,
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="required_inputs_for_gasification",
        )

        # Create a list of keys from the dictionary
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        biomass, steam, syngas, heat, elec = requirements.values()

        # Store inputs for the use table
        seq.store_result(
            name=f"{feedstocktype}_input_lci",
            value=biomass,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{activity}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

    elif activity == "co2_hydrogenation":
        # Methanol production via CO2 hydrogenation]:

        # Calculate the inputs and outputs of methanol production via Conventional Steam Reforming (CSR)
        output = seq.elementary.reverse_co2_hydrogenation(
            CH4O_tonnes=seq.step.pp_i_j_k.value,
        )

        # Store results for inputs and outputs
        seq.store_result(
            name="co2_input",
            value=output[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_dioxide",
            eq_name="reverse_co2_hydrogenation",
        )

        seq.store_result(
            name="h2_input",
            value=output[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_co2_hydrogenation",
        )

        seq.store_result(
            name="h2o_input",
            value=output[2],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="reverse_co2_hydrogenation",
        )

        results = seq.elementary.reverse_water_gas_shift(
            CO2_tonnes=seq.step.co2_input.value,
            H2_tonnes=seq.step.h2_input.value,
        )

        # Reverse water gas shift reaction
        seq.store_result(
            name="co_input",
            value=results[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|carbon_monoxide",
            eq_name="reverse_water_gas_shift",
        )

        seq.store_result(
            name="h2o_input",
            value=results[1],
            unit="t/yr",
            year=year,
            lci_flag="use|product|water",
            eq_name="reverse_water_gas_shift",
        )

        seq.store_result(
            name="syngas_input",
            value=output[1] + results[0],
            unit="t/yr",
            year=year,
            lci_flag="use|product|hydrogen",
            eq_name="reverse_water_gas_shift",
        )

        # Store results for inputs and outputs
        requirements = seq.elementary.calculate_feedstock_requirements(
            pp_meoh=seq.step.pp_i_j_k.value,
            lci_coefficients=lci_coefficients,
        )

        _, steam, syngas, heat, elec = requirements.values()

        seq.store_result(
            name="steam_input",
            value=steam,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[1]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="syngas_input_lci",
            value=syngas,
            unit="t/yr",
            year=year,
            lci_flag=f"use|product|{product_list[2]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="heat_input",
            value=heat,
            unit="MJ/yr",
            year=year,
            lci_flag=f"use|product|{product_list[3]}",
            eq_name="calculate_feedstock_requirements",
        )

        seq.store_result(
            name="electricity_input",
            value=elec,
            unit="kWh/yr",
            year=year,
            lci_flag=f"use|product|{product_list[4]}",
            eq_name="calculate_feedstock_requirements",
        )

    else:
        logger.error(
            f"Unsupported combination of activity '{activity}' and feedstocktype '{ch4_input}'."
        )
        return None

    logger.info(
        f"---> Methanol recipe and emissions calculation for activity: {activity} and feedstocktype: {feedstocktype} completed successfully."
    )
    return seq.step
