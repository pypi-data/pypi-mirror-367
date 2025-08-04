import logging

from ..._sequence import Sequence
from . import elementary as elem
from ._data import concordance as conc
from ._data import dimension as dim
from ._data import parameter as par

logger = logging.getLogger(__name__)


def tier1_co2_pp(
    year=2006,
    region="GB",
    product="methanol",
    activity="csr_a",
    feedstocktype="natural_gas",
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

    logger.info("---> Chemical sequence finalized.")
    return seq.step


def tier1_co2_fa(
    year=2006,
    region="GB",
    product="methanol",
    activity="csr_a",
    uncertainty="def",
):
    """Tier 1 method CO2 Emissions.
    Starting with data input for parameter fa (annual consumption of feedstock)

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
        Includes the results of each step of the sequence.
    """
    # Initialize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Chemical sequence started --->")
    meta_dict = locals()
    meta_dict["activity"] = "petrochem"
    seq.store_signature(meta_dict)

    # loop (sum over all feedstock types)
    d = seq.get_dimension_levels(
        year, region, activity, product, uncert="def", table="fa_i_k"
    )
    value = 0.0
    for feedstocktype in d:
        # Reading the fa_i_k and spp_j_k parameters for each feedstock type
        seq.read_parameter(
            name=f"fa_i_k_xxx_{feedstocktype}_xxx",
            table="fa_i_k",
            coords=[year, region, activity, product, feedstocktype],
            lci_flag=f"use|product|{feedstocktype}",
        )
        seq.read_parameter(
            name=f"spp_j_k_xxx_{feedstocktype}_xxx",
            table="spp_j_k",
            coords=[year, region, product, feedstocktype],
            lci_flag=f"transf_coeff|product|{feedstocktype}|{product}",
        )

        # Compute production for each feedstock
        fa_value = getattr(
            getattr(seq.step, f"fa_i_k_xxx_{feedstocktype}_xxx"), "value"
        )
        spp_value = getattr(
            getattr(seq.step, f"spp_j_k_xxx_{feedstocktype}_xxx"), "value"
        )
        value += seq.elementary.pp_i(fa=fa_value, spp=spp_value)

    # Store the total production result
    seq.store_result(
        name="pp_i",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag=f"supply|product|{product}",
    )

    # Reading other parameters for emission calculation
    seq.read_parameter(
        name="pp_share_i_j",
        table="pp_share_i_j",
        coords=[year, region, product, activity],
    )

    seq.read_parameter(
        name="pp_share_i_j_k",
        table="pp_share_i_j_k",
        coords=[year, region, product, activity, feedstocktype],
    )

    seq.read_parameter(
        name="ef_co2_i_k",
        table="ef_co2_i_k",
        coords=[year, region, product, activity, feedstocktype],
    )

    seq.read_parameter(
        name="gaf",
        table="gaf",
        coords=[year, region],
    )

    # Calculate production by activity and feedstock
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

    # Calculate CO2 emissions
    value = seq.elementary.eco2_tier1(
        pp_i=seq.step.pp_i_j_k.value,
        ef=seq.step.ef_co2_i_k.value,
        gaf=seq.step.gaf.value,
    )

    # Store CO2 emissions result
    seq.store_result(
        name="eco2_tier1",
        value=value,
        unit="t/year",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Chemical sequence finalized.")
    return seq.step


def tier2_co2(
    year=2006,
    region="GB",
    product="methanol",
    activity="csr_a",
    feedstocktype="natural_gas",
    uncertainty="def",
):
    """Tier 2 method CO2 Emissions.

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

    # Reading other parameters for emission calculation
    seq.read_parameter(
        name="pp_share_i_j",
        table="pp_share_i_j",
        coords=[year, region, product, activity],
    )

    seq.read_parameter(
        name="pp_share_i_j_k",
        table="pp_share_i_j_k",
        coords=[year, region, product, activity, feedstocktype],
    )

    seq.read_parameter(
        name="ef_co2_i_k",
        table="ef_co2_i_k",
        coords=[year, region, product, activity, feedstocktype],
    )

    seq.read_parameter(
        name="gaf",
        table="gaf",
        coords=[year, region],
    )

    # Calculate production by activity and feedstock
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

    seq.read_parameter(
        name="pc_i",
        table="pc_i",
        coords=[year, region, product],
    )

    value = seq.step.pp_pc(pp_i=seq.step.pp_i_j_k.value, pc=seq.step.pc_i.value)
    seq.store_result(name="pp_pc", value=value, unit="t/yr", year=year)

    if product in [
        "methanol",
        "ethylene dichloride",
        "ethylene oxide",
        "carbon black",
    ]:
        value = 0.0
        seq.store_result(
            name="sp_i_j",
            value=value,
            unit="t/year",
            year=year,
        )
        seq.store_result(
            name="sc_j",
            value=value,
            unit="t/t",
            year=year,
        )
    else:
        # loop (sum over all secondary types)
        d = seq.get_dimension_levels(
            year, region, product, uncert="def", table="sp_i_j"
        )
        value = 0.0
        seq.read_parameter(
            name="sc_j",
            table="sc_j",
            coords=[year, region, product],
        )
        for secondarytype in d:
            seq.read_parameter(
                name=f"sp_i_j_xxx_{secondarytype}_xxx",
                table="sp_i_j",
                coords=[year, region, product, secondarytype],
                lci_flag=f"supply|by-product|{secondarytype}",
            )

            value += seq.elementary.sp_cs(
                sp=getattr(
                    getattr(seq.step, f"sp_i_j_xxx_{feedstocktype}_xxx"), "value"
                ),
                sc=seq.step.sc_j.value,
            )

        seq.store_result(name="sp_sc", value=value, unit="t/year", year=year)

    # loop (sum over all feedstock types)
    d = seq.get_dimension_levels(
        year, region, activity, product, uncert="def", table="fa_i_k"
    )
    value = 0.0
    for feedstocktype in d:
        seq.read_parameter(
            name=f"fa_i_k_xxx_{feedstocktype}_xxx",
            table="fa_i_k",
            coords=[year, region, activity, product, feedstocktype],
            lci_flag=f"use|product|{feedstocktype}",
        )
        seq.read_parameter(
            name=f"fc_k_xxx_{feedstocktype}_xxx",
            table="fc_k",
            coords=[year, region, feedstocktype],
        )

        value += seq.elementary.fa_fc(
            fa=getattr(getattr(seq.step, f"fa_i_k_xxx_{feedstocktype}_xxx"), "value"),
            fc=getattr(getattr(seq.step, f"fc_k_xxx_{feedstocktype}_xxx"), "value"),
        )
    seq.store_result(name="fa_fc", value=value, unit="t/yr", year=year)

    value = seq.elementary.eco2_tier2(
        fa_fc=seq.step.fa_fc.value,
        pp_pc=seq.step.pp_pc.value,
        sp_sc=seq.step.sp_sc.value,
    )
    seq.store_result(
        name="eco2_tier2",
        value=value,
        unit="t/yr",
        year=year,
        lci_flag="emission|air|CO2",
    )

    logger.info("---> Chemical sequence finalized.")
    return seq.step


def tier1_ch4_pp(
    year=2006,
    region="GB",
    product="methanol",
    activity="csr_a",
    feedstocktype="natural_gas",
    uncertainty="def",
):
    """Tier 1 method total CH4 emissions calculations.
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
            feedstocktype,
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
        ],
    )

    pp_i_j_k = seq.elementary.pp_i_j_k(
        pp_i=seq.step.pp_i_j_k.value,
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

    seq.read_parameter(
        name="ef_ch4_i_k",
        table="ef_ch4_i_k",
        coords=[
            year,
            region,
            product,
            activity,
            feedstocktype,
        ],
    )

    seq.read_parameter(
        name="eff_i",
        table="eff_i",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="efp_i",
        table="efp_i",
        coords=[year, region, product],
    )

    fug_value = seq.elementary.ech4_fugitive(
        pp_i=seq.step.pp_i_j_k.value, ef=seq.step.eff_i.value
    )

    seq.store_result(
        name="ech4_fugitive",
        value=fug_value,
        unit="kg/year",
        year=year,
    )

    vent_value = seq.elementary.ech4_process_vent(
        pp_i=seq.step.pp_i_j_k.value, ef=seq.step.efp_i.value
    )

    seq.store_result(
        name="ech4_process_vent",
        value=vent_value,
        unit="kg/year",
        year=year,
    )

    value = seq.elementary.ech4_process_vent(
        ech4_fugitive=seq.step.ech4_fugitive.value,
        ech4_process_vent=seq.step.ech4_process_vent.value,
    )

    seq.store_result(
        name="ech4_process_vent",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|CH4",
    )

    logger.info("---> Tier 1 method total CH4 emissions sequence finalized.")
    return seq.step


def tier1_e_hfc23(
    year=2006,
    region="GB",
    uncertainty="def",
):
    """Tier 1 method HFC-23 emissions based on default IPCC emission factors (Equation 3.30).

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
    logger.info("Chemical sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "petrochem"
    meta_dict["product"] = "HCFC22"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="ef_hfc23",
        table="ef_hfc23",
        coords=[year, region],
    )

    seq.read_parameter(
        name="p_hcfc22",
        table="p_hcfc22",
        coords=[year, region],
        lci_flag="supply|product|HCFC22",
    )

    value = seq.elementary.tier1_e_hfc_23(
        ef_default=seq.step.ef_hfc23.value,
        p_hcfc_22=seq.step.p_hcfc22.value,
    )

    seq.store_result(
        name="tier1_e_hfc_23",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|HFC23",
    )

    logger.info("---> Tier 1 method HFC-23 emissions sequence finalized.")
    return seq.step


def tier2_e_hfc23(
    year=2006,
    region="GB",
    uncertainty="def",
):
    """Tier 2 method HFC-23 emissions based on calculated emission factors via carbon or fluorine balance eficiency methods (Equation 3.31).

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
        Includes the results of each step of the sequence.
    """
    # Initialize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Chemical sequence started --->")

    meta_dict = locals()
    meta_dict["activity"] = "petrochem"
    meta_dict["product"] = "HCFC22"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="ef_hfc23",
        table="ef_hfc23",
        coords=[year, region],
    )

    seq.read_parameter(
        name="p_hcfc22",
        table="p_hcfc22",
        coords=[year, region],
        lci_flag="supply|product|HCFC22",
    )

    seq.read_parameter(
        name="f_released",
        table="f_released",
        coords=[year, region],
    )

    seq.read_parameter(
        name="f_efficiency_loss",
        table="f_efficiency_loss",
        coords=[year, region],
    )

    seq.read_parameter(
        name="fcc",
        table="fcc",
        coords=[year, region],
    )

    seq.read_parameter(
        name="cbe",
        table="cbe",
        coords=[year, region],
    )
    ef_carb_balance = seq.elementary.ef_carbon_balance(
        cbe=seq.step.cbe.value,
        f_efficiency_loss=seq.step.f_efficiency_loss.value,
        fcc=seq.step.fcc.value,
    )
    seq.store_result(
        name="ef_carbon_balance",
        value=ef_carb_balance,
        unit="kg/kg",
        year=year,
    )

    seq.read_parameter(
        name="fbe",
        table="fbe",
        coords=[year, region],
    )
    ef_flurine_balance = seq.elementary.ef_fluorine_balance(
        fbe=seq.step.fbe.value,
        f_efficiency_loss=seq.step.f_efficiency_loss.value,
        fcc=seq.step.fcc.value,
    )

    seq.store_result(
        name="ef_flurine_balance",
        value=ef_flurine_balance,
        unit="kg/kg",
        year=year,
    )

    value = seq.elementary.ef_hfc23_average(
        carbon=seq.step.ef_carbon_balance.value,
        flurine=seq.step.ef_flurine_balance.value,
    )

    seq.store_result(
        name="ef_hfc23_average",
        value=value,
        unit="kg/kg",
        year=year,
    )

    value = seq.elementary.tier1_e_hfc_23(
        ef_default=seq.step.ef_hfc23_average.value,
        p_hcfc_22=seq.step.p_hcfc22.value,
        f_released=seq.step.f_released.value,
    )

    seq.store_result(
        name="tier1_e_hfc_23",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag="emission|air|HFC23",
    )

    logger.info("---> Tier 2 method HFC-23 emissions sequence finalized.")
    return seq.step


def tier1_fgas(
    year=2006,
    region="GB",
    product="hfc-32",
    uncertainty="def",
):
    """Tier 1 method F-GAS emissions calculations.
    Starting with data input for parameter ef_default_k (production-related emissions of fluorinated greenhouse gas) and p_k (total production of fluorinated greenhouse gas k, kg)

    Argument
    ---------
    year : int
        year under study
    region : str
        region under study
    product : str
        type of fluorinated greenhouse gas
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
        name="ef_default_k",
        table="ef_default_k",
        coords=[year, region, product],
    )

    seq.read_parameter(
        name="p_k",
        table="p_k",
        coords=[year, region, product],
        lci_flag=f"supply|product|{product}",
    )

    value = seq.elementary.eco2_tier1(
        ef_default_k=seq.step.ef_default_k.value, p_k=seq.step.p_k.value
    )

    seq.store_result(
        name="eco2_tier1",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag=f"emission|air|{product}",
    )

    logger.info("---> Tier 1 method F-GAS emissions calculations sequence finalized.")
    return seq.step


def tier3_fgas(
    year: int = 2006,
    region: str = "a specific plant",
    fgas: str = "pfc-14",
    uncertainty: str = "def",
):
    """
    Tier 3 direct calculation of production related emissions for fluorinated greenhouse gases.

    Based on data input for parameter c_ij (concentration of F-GAS 'k' in the gas stream vented from process stream 'j' at plant 'i')
    and f_ij (mass flow of the gas stream for F-GAS 'k' from process stream 'j' at plant 'i').

    Arguments
    ---------
    year : int
        Year under study.
    region : str
        Region under study. For tier 3, this can be a specific plant.
    fgas : str
        Type of fluorinated greenhouse gas.
    uncertainty : str
        Uncertainty definition for calculations.

    Returns
    -------
    VALUE: float
        Total production-related emissions for the given product and region in the specified year.
    """
    # Initialize variable instance
    seq = Sequence(dim, par, elem, conc, uncert=uncertainty)
    logger.info("Tier 3 production-related emissions calculation started --->")
    meta_dict = locals()
    meta_dict["activity"] = "petrochem"
    seq.store_signature(meta_dict)

    seq.read_parameter(
        name="c_ijk",
        table="c_ijk",
        coords=[year, region, fgas],
    )
    seq.read_parameter(
        name="f_ijk",
        table="f_ijk",
        coords=[year, region, fgas],
    )
    # Call the function to calculate emissions for each plant
    value = seq.elementary.tier3_e_k_direct(
        c_ij=seq.step.c_ijk.value,
        f_ij=seq.step.f_ijk.value,
    )

    # Store and log the calculated total emissions
    seq.store_result(
        name="tier3_e_k_direct",
        value=value,
        unit="kg/year",
        year=year,
        lci_flag=f"emission|air|{fgas}",
    )

    logger.info("Tier 3 production-related emissions sequence finalized.")
    return seq.step
