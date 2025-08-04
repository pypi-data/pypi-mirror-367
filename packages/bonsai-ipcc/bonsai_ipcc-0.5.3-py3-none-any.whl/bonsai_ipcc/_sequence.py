import inspect
import logging
import os
import re
from dataclasses import dataclass
from importlib.resources import open_binary
from itertools import product
from pathlib import Path

import dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty
import loguru
import numpy as np
import pandas as pd
import uncertainties as uct
import yaml
from fitter import Fitter

from . import _checks as checks
from . import log_setup
from . import uncertainties as unc

loguru.logger.remove()
log_setup.setup_logger()

logger = logging.getLogger(__name__)

from ._metadata import MetaData  # TODO

ROOT_PATH = Path(os.path.dirname(__file__)).parent


@dataclass
class Step:
    position: int
    year: int  # or list of int
    unit: str
    value: float  # ufloat, np.array or list of those
    type: str
    lci_flag: str  # helper to create the bonsai ppf tables
    parameter_flag: str  # applied to parameters in the sequence for those different equations can be used (helper to get the metadata)
    eq_name: str  # name of the eqaution; used to store parameters that are calculyted by elementary equation with multiple outputs


class Sequence:
    def __init__(self, dim, par, elem, conc, uncert):
        self.dimension = dim
        self.parameter = par
        self.elementary = elem
        self.concordance = conc
        self.uncertainty = uncert
        self.step = DataClass()
        self.order = []

    def _validate_coordinate(self, coord, dim):
        """
        Validate if the given coordinate exists in the specified dimension.

        Args:
            coord (str): Coordinate to validate.
            dim (str): Dimension name.

        Raises:
            ValueError: If the coordinate does not exist in the dimension.
        """
        try:
            df_dim = getattr(self.dimension, dim)
            checks.check_set(coord, df_dim.index, "coordinate")
        except AttributeError:
            try:
                df_dim = getattr(self.dimension, "activity")
                checks.check_set(coord, df_dim.index, "coordinate")
            except AttributeError:
                try:
                    df_dim = getattr(self.dimension, "product")
                    checks.check_set(coord, df_dim.index, "coordinate")
                except AttributeError:
                    raise

    def _read_parameter_with_concordance(self, df, _coords, name, table):
        """
        Read parameter data and uncertainty information with concordance handling.

        Args:
            df (pd.DataFrame): Parameter DataFrame.
            _coords (tuple): Coordinates for data retrieval.
            name (str): Parameter name.
            table (str): Parameter table name.

        Returns:
            tuple: Tuple containing value, unit and new coords.
        """
        conc_dim_list = []
        for _dim in df.index.names:
            if _dim in [k for k in self.concordance.__dict__]:
                conc_dim = _dim
                conc_dim_list.append(conc_dim)
        if not conc_dim_list:
            raise KeyError("No concordance data found for any dimension")

        conc_df_list = []
        for conc_dim in conc_dim_list:
            try:
                conc_df = getattr(self.concordance, conc_dim)
                conc_df_list.append(conc_df)
            except AttributeError:
                raise KeyError(f"No concordance data found for dimension '{conc_dim}'")

        tmp, u = None, None

        new_coords_list = []
        for conc_df in conc_df_list:

            for j in range(len(conc_df.columns)):
                new_coords = []
                for c in _coords:
                    if c in conc_df.index:
                        old_c = c
                        new_c = conc_df.loc[c][j]
                        new_coords.append(new_c)
                    else:
                        new_coords.append(c)
                new_coords_list.append(new_coords)

        # create all combinations of new coordinates that are possible and check if values are available
        a = np.array(new_coords_list).T.tolist()
        l = []
        for p in a:
            l.append(p)
        aa = product(*l)

        def is_number(s):
            """Convert years into integer"""
            try:
                int(float((s)))
                return int(float(s))
            except ValueError:
                return s

        new_coords_list = []
        for b in aa:
            new_coords_list.append(list([is_number(x) for x in list(b)]))
        new_coords_list = [list(x) for x in set(tuple(x) for x in new_coords_list)]

        # try reading the paramater based on the potential coordinates, stop at the first match
        for new_coords in new_coords_list:
            try:
                tmp, u = self._read_parameter_uncertainty(df, new_coords, table)
                logger.info(
                    f"'Coordinates {str(_coords)}' has been replaced by '{str(new_coords)}' during reading parameter table '{str(table)}'"
                )
                break
            except Exception:
                pass

        if tmp is None or u is None:
            raise KeyError("No data or uncertainty found using concordance")

        return tmp, u, new_coords

    def _read_parameter_uncertainty(self, df, coords, name):
        """
        Read parameter data with uncertainty information.

        Args:
            df (pd.DataFrame): Parameter DataFrame.
            coords (iterable): Coordinates for data retrieval.
            name (str): Parameter name.

        Returns:
            tuple: Tuple containing value and unit.
        """
        coords = list(coords)
        if self.uncertainty not in [
            "analytical",
            "monte_carlo",
            "def",
            "min",
            "max",
            "sample",
        ]:
            raise ValueError(f"Unsupported uncertainty type: {self.uncertainty}")

        elif (
            self.uncertainty not in ["analytical", "monte_carlo"]
            and "property" in df.index.names
        ):
            coords = coords + [self.uncertainty]
            tmp = df.loc[tuple(coords)].value
            u = df.loc[tuple(coords)].unit
        elif self.uncertainty == "monte_carlo" and "property" in df.index.names:
            d = df.loc[tuple(coords + ["def"])].value
            min_val = df.loc[tuple(coords + ["min"])].value
            max_val = df.loc[tuple(coords + ["max"])].value
            abs_min = df.loc[tuple(coords + ["abs_min"])].value
            abs_max = df.loc[tuple(coords + ["abs_max"])].value
            logger.info(
                f"Uncertainty distribution for parameter '{name}' with coords '{coords}':"
            )
            tmp = unc.monte_carlo(
                default=d,
                min95=min_val,
                max95=max_val,
                abs_min=abs_min,
                abs_max=abs_max,
                size=1000,
                distribution="check",
            )
            u = df.loc[tuple(coords + ["max"])].unit
        elif self.uncertainty == "sample" and "property" in df.index.names:
            tmp = df.loc[tuple(coords + ["sample"])].value  # .split(','))
            u = df.loc[tuple(coords + ["sample"])].unit
        elif self.uncertainty == "analytical" and "property" in df.index.names:
            min_val = df.loc[tuple(coords + ["min"])].value
            max_val = df.loc[tuple(coords + ["max"])].value
            tmp = unc.analytical(min_val, max_val)
            u = df.loc[tuple(coords + ["max"])].unit
        else:
            tmp = df.loc[tuple(coords)].value
            u = df.loc[tuple(coords)].unit

        return tmp, u

    def read_parameter(
        self, name, table, coords, lci_flag=None, parameter_flag=None, eq_name=None
    ):
        """
        Read parameter data and uncertainty information, then store it in the step.

        Args:
            name (str): Name of the parameter.
            table (str): Name of the parameter table.
            coords (iterable): Coordinates to retrieve the data.

        Raises:
            KeyError: If coordinates or their concordance are not found.
        """

        # validate parameter table exists
        checks.check_set(table, self.parameter.__dict__.keys(), "parameter table")

        # validate name does not yet exist
        checks.check_set(name, self.order, "name", include=False)

        df = getattr(self.parameter, table)

        # check for duplicates in index
        if df.index.duplicated().any():
            raise ValueError(f"Duplicated indices in parameter {name}")

        # check for negative min values
        if "property" in df.index.names and isinstance(df.index, pd.MultiIndex):
            try:
                min_values = df.xs("min", level="property", drop_level=False)
                if (min_values["value"] < 0).any():
                    raise ValueError(
                        f"Negative value found for 'min' property in parameter '{name}'."
                    )
            except KeyError:
                pass
        elif df.index.name == "property":
            if "min" in df.index and df.loc["min", "value"] < 0:
                raise ValueError(
                    f"Negative value found for 'min' property in parameter '{name}'."
                )

        _coords = tuple(coords)
        new_coords = coords
        for coord, dim in zip(_coords, df.index.names):
            self._validate_coordinate(coord, dim)

        try:
            tmp, u = self._read_parameter_uncertainty(df, _coords, table)
        except Exception:
            try:
                tmp, u, new_coords = self._read_parameter_with_concordance(
                    df, _coords, name, table
                )
            except Exception:
                raise KeyError(
                    f"Coordinate '{_coords}' or its concordance not found for parameter '{name}' with table '{table}'. If uncertainty analysis, also check required properties (e.g. max, min)."
                )

        # add year to step
        if "year" in df.index.names:
            year = [x for x in new_coords if isinstance(x, int)][0]
            # df = df.reset_index(level="year")
            # year = list(df.loc[tuple(no_integers + [self.uncertainty])]["year"])
        else:
            year = None

        position = len(self.order)
        setattr(
            self.step,
            name,
            Step(
                position=position,
                year=year,
                value=tmp,
                unit=u,
                type="data",
                lci_flag=lci_flag,
                parameter_flag=None,
                eq_name=None,
            ),
        )
        self.order.append(name)

    def store_result(
        self,
        name,
        value,
        unit,
        year=None,
        lci_flag=None,
        parameter_flag=None,
        eq_name=None,
    ):
        """
        Store a result in the step.

        Args:
            name (str): Name of the result.
            value (float): Result value.
            unit (str): Unit of the result.
            year (int, optional): Year associated with the result. Defaults to None.
            lci_flag (str, optional): used to create Bonsai ppf tables
            parameter_flag (str, optional): used for retrieving metadata in conditional DAG with multiple possible paths for a parameter
        """
        position = len(self.order)
        setattr(
            self.step,
            name,
            Step(
                position=position,
                year=year,
                value=value,
                unit=unit,
                type="elementary",
                lci_flag=lci_flag,
                parameter_flag=parameter_flag,
                eq_name=eq_name,
            ),
        )
        self.order.append(name)

    def store_signature(self, d):
        """
        Store a the signature in the step.

        Args:
            d (dict): signature dictionary (e.g. by locals())
        """
        try:
            del d["seq"]
        except:
            pass
        setattr(
            self.step,
            "signature",
            d,
        )
        self.order.append("signature")

    def get_inventory_levels(self, table, year, region):
        """
        Returns the dimensions and its unique level values in a dict, without the dimensions year and region.
        """
        df = getattr(self.parameter, table)
        try:
            df = df[df.index.get_level_values("property") == "def"]
            df1 = df.loc[year, region]
            # df1 = df1[df1["property"] == "def"]
        except Exception:
            raise KeyError(
                f"Year '{year}' and region '{region}' not found in parameter table '{table}'."
            )
        return {
            level_name: df1.index.get_level_values(level).tolist()
            for level, level_name in enumerate(df1.index.names)
        }

    def _get_new_levels(self, df, _coords):
        conc_dim_list = []
        for _dim in df.index.names:
            if _dim in [k for k in self.concordance.__dict__]:
                conc_dim = _dim
                conc_dim_list.append(conc_dim)
        if not conc_dim_list:
            raise KeyError("No concordance data found for any dimension")

        conc_df_list = []
        for conc_dim in conc_dim_list:
            try:
                conc_df = getattr(self.concordance, conc_dim)
                conc_df_list.append(conc_df)
            except AttributeError:
                raise KeyError(f"No concordance data found for dimension '{conc_dim}'")

        new_coords_list = []
        for conc_df in conc_df_list:

            for j in range(len(conc_df.columns)):
                new_coords = []
                for c in _coords:
                    if c in conc_df.index:
                        old_c = c
                        new_c = conc_df.loc[c][j]
                        new_coords.append(new_c)
                    else:
                        new_coords.append(c)
                new_coords_list.append(new_coords)

        # create all combinations of new coordinates that are possible and check if values are available
        a = np.array(new_coords_list).T.tolist()
        l = []
        for p in a:
            l.append(p)
        aa = product(*l)

        def is_number(s):
            """Convert years into integer"""
            try:
                int(float((s)))
                return int(float(s))
            except ValueError:
                return s

        new_coords_list = []
        for b in aa:
            new_coords_list.append(list([is_number(x) for x in list(b)]))
        new_coords_list = [list(x) for x in set(tuple(x) for x in new_coords_list)]

        return new_coords_list

    def get_dimension_levels(self, *coords, table, uncert):
        """
        Returns a list of dimension levels based on the coords.

        Attributes
        ----------
        *coords
            depend on the parameter
            e.g.: 2019, "DE", "silicon_metal" (for year, region, ferroalloy_type in parameter m_agent)
        table : str
            parameter table name
            e.g.: "m_agent"
        uncert : str
            type of uncertainty (property)
            e.g.: "def"

        Returns
        -------
        list
            all values of the next dimension in the dataframe
            e.g.: list of agent types (used for 2019, "DE", "silicon_metal")
        """
        df = getattr(self.parameter, table)

        new_coords_list = self._get_new_levels(df, coords)
        # try reading the paramater based on the potential coordinates, stop at the first match
        for new_coords in new_coords_list:
            try:
                df1 = df.loc[tuple(new_coords)]
                logger.info(
                    f"'Coordinates {str(coords)}' has been replaced by '{str(new_coords)}' during getting dimension levels from parameter table '{str(table)}'"
                )
                break
            except KeyError:
                pass

        df1 = df1[df1.index.get_level_values("property") == uncert]
        return list(df1.index.get_level_values(0))


@dataclass
class DataClass:
    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        """
        Convert the DataClass instance into a dictionary.

        Returns
        -------
        dict
            includes the signature (attributes to run the sequence) and parameter values calculated within the sequence
        """
        return self.__dict__

    def _metadata(self, parameter, eq_name, _external_metadata, _ext_functions):
        """Get the metadata of a parameter.
        This is done based on the ipcc.datapackage.yaml for parameter tables;
        and based on the function names in .py files for parameters calculated based on elementary equations.

        Argument
        --------
        paramater : string
            parameter name

        Returns
        -------
        VALUE: str
            metadata description of the parameter
        """

        def _remove_year_substring(input_string):
            # Define the pattern to match the substring e.g. _year2000_
            year_pattern = r"_?year\d{4}_?"
            # Replace the matched substring with an empty string
            output_string = re.sub(year_pattern, "", input_string)

            # Define the pattern to match the substring e.g. xxx_msw_paper_xxx
            tech_pattern = r"_?xxx_[\w_-]+_xxx_?"
            output_string = re.sub(tech_pattern, "", output_string)

            return output_string

        def _get_option_substring(self, name):
            par = getattr(self, name)
            return par.parameter_flag

        parameter = _remove_year_substring(parameter)

        if eq_name:
            parameter = eq_name

        # Look in the ipcc.datapackage.yaml #TODO: REPLACE the yaml import by a MetaDataObject that is imported!
        # with open_binary("bonsai_ipcc.data", "ipcc.datapackage.yaml") as fp:
        #    metadata = yaml.load(fp, Loader=yaml.Loader)
        _obj = MetaData(external_metadata=_external_metadata)
        metadata = _obj.metadata
        for k in range(len(metadata["resources"])):
            parts = metadata["resources"][k]["path"].split("/")
            p = parts[-1].split(".")[0]
            prefix = p.split("_", 1)[0]
            p = p.split("_", 1)[-1]
            if parameter == p and prefix == "par":
                try:
                    d = metadata["resources"][k]["description"]
                except KeyError:
                    raise KeyError(f"parameter {p} not found in metadata.")
        try:
            return d
        except UnboundLocalError:
            # Look in the elementary equations

            def _is_local_module(module):
                """to avoid third party modules"""
                try:
                    module_file = getattr(module, "__file__", None)
                    if module_file and module_file.startswith(str(ROOT_PATH)):
                        return True
                    return False
                except AttributeError:
                    return False

            all_members = []
            if _ext_functions:
                all_members = all_members + _ext_functions
            # Recursively traverse the directory structure
            for root, dirs, files in os.walk(ROOT_PATH):
                for file_name in files:
                    if file_name.endswith(".py"):
                        module_path = os.path.join(root, file_name)
                        module_name = os.path.splitext(
                            os.path.relpath(module_path, ROOT_PATH)
                        )[0].replace(os.path.sep, ".")
                        try:
                            module = __import__(module_name, fromlist=[""])
                            if _is_local_module(module):
                                members = inspect.getmembers(module)
                                all_members.extend(members)
                            else:
                                pass
                        except:
                            pass

            # Filter functions and extract docstrings
            function_docs = {}
            for name, obj in all_members:
                if inspect.isfunction(obj):
                    docstring = inspect.getdoc(obj)
                    if docstring:
                        function_docs[name] = docstring

            func_docstring = None
            # for name, obj in members:#TODO: check if loop is required
            #    if name == "my_func" and inspect.isfunction(obj):
            #        func_docstring = inspect.getdoc(obj)
            #        break
            if name == parameter and inspect.isfunction(obj):
                func_docstring = inspect.getdoc(obj)
            if parameter == "signature":
                pass
            if parameter != "signature":
                try:
                    func_docstring = function_docs[parameter]
                except KeyError:
                    option_string = _get_option_substring(self, name=parameter)
                    if option_string == None:
                        raise ValueError(
                            f"Can not find metadata for parameter '{parameter}'. Make sure that '{parameter}' has an equation named '{parameter}', or is mentioned in the 'ipcc.datapackage.yaml'."
                        )
                    func_docstring = function_docs[parameter + "_" + option_string]

                func_docstring = (
                    "\n".join(func_docstring.splitlines()[-1:]).rstrip().strip()
                )
            return func_docstring

    def to_frames(self, bonsai=False, external_metadata=None, external_functions=None):
        """
        Convert the DataClass instance into multiple pandas DataFrames.

        Argument
        --------
        bonsai : bool
            if True, the result is also transformed into dataframes follwowing the bonsai table schemas
        Returns
        -------
        dict of pd.DataFrame
            'signature' dataframe includes the arguments for a specific sequence
            'steps' dataframe includes the steps that are used and calculated within a sequence
            'description' dataframe includes information of the parameter codes
            'bonsai' dictionary includes 'use', 'supply', 'emission', 'resource', and 'transfer coefficient' tables in bonsai format (optional)
        """
        dict_of_df = {}

        df_steps = pd.DataFrame({})
        df_descr = pd.DataFrame({})

        if bonsai != "samples":

            for p in self.__dict__:
                # Create DataFrame for each parameter attribute
                if p == "signature":
                    df_sig = pd.DataFrame(self.__dict__[p], index=[0])
                    df_sig.index.name = "position"
                else:
                    if isinstance(
                        self.__dict__[p].value,
                        np.float64
                        | float
                        | np.float16
                        | int
                        | np.float32
                        | np.int64
                        | np.int32
                        | np.int16
                        | str,
                    ):
                        df = pd.DataFrame(
                            {
                                "parameter": p,
                                "year": [self.__dict__[p].year],
                                "unit": self.__dict__[p].unit,
                                "property": df_sig.iloc[0]["uncertainty"],
                                "value": [self.__dict__[p].value],
                                "parameter_type": [self.__dict__[p].type],
                                "lci_flag": [self.__dict__[p].lci_flag],
                            },
                            index=[self.__dict__[p].position],
                        )
                        df_steps = pd.concat([df_steps, df])
                        df_steps.index.name = "position"
                    elif isinstance(self.__dict__[p].value, np.ndarray) and not np.all(
                        self.__dict__[p].value == self.__dict__[p].value[0]
                    ):
                        f = Fitter(
                            self.__dict__[p].value,
                            distributions=[
                                "lognorm",
                                "truncnorm",
                                "uniform",
                                "norm",
                            ],
                        )
                        f.fit()
                        try:
                            r = f.get_best()
                        except KeyError:
                            logger.warning(
                                f"Fitting for parameter {p} went wrong. Lognorm distribution is chosen as default."
                            )
                        distribution = list(r.keys())[0]
                        logger.info(
                            f"Best fit for parameter '{p}' is '{distribution}' distribution."
                        )
                        prop = ["mean", "sd", "distribution"]
                        values = [
                            self.__dict__[p].value.mean(),
                            self.__dict__[p].value.std(),
                            distribution,
                        ]
                        df = pd.DataFrame(
                            {
                                "parameter": [p, p, p],
                                "year": [
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                ],
                                "unit": [
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                ],
                                "property": prop,
                                "value": values,
                                "parameter_type": [
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                ],
                                "lci_flag": [
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                ],
                            },
                            index=[
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                            ],
                        )
                        df_steps = pd.concat([df_steps, df])
                        df_steps.index.name = "position"
                        del f
                    elif isinstance(self.__dict__[p].value, np.ndarray) and np.all(
                        self.__dict__[p].value == self.__dict__[p].value[0]
                    ):
                        df = pd.DataFrame(
                            {
                                "parameter": [p, p, p],
                                "year": [
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                ],
                                "unit": [
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                ],
                                "property": ["mean", "sd", "distribution"],
                                "value": [self.__dict__[p].value[0], 0.0, "none"],
                                "parameter_type": [
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                ],
                                "lci_flag": [
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                ],
                            },
                            index=[
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                            ],
                        )
                        df_steps = pd.concat([df_steps, df])
                        df_steps.index.name = "position"
                    elif isinstance(
                        self.__dict__[p].value,
                        uct.core.Variable | uct.core.AffineScalarFunc,
                    ):
                        df = pd.DataFrame(
                            {
                                "parameter": [p, p, p],
                                "year": [
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                    self.__dict__[p].year,
                                ],
                                "unit": [
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                    self.__dict__[p].unit,
                                ],
                                "property": ["mean", "sd", "distribution"],
                                "value": [
                                    self.__dict__[p].value.nominal_value,
                                    self.__dict__[p].value.std_dev,
                                    "norm",
                                ],
                                "parameter_type": [
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                    self.__dict__[p].type,
                                ],
                                "lci_flag": [
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                    self.__dict__[p].lci_flag,
                                ],
                            },
                            index=[
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                                self.__dict__[p].position,
                            ],
                        )
                        df_steps = pd.concat([df_steps, df])
                        df_steps.index.name = "position"
                    elif isinstance(self.__dict__[p].value, list):
                        if isinstance(
                            self.__dict__[p].value[0],
                            np.float64
                            | float
                            | np.float16
                            | int
                            | np.float32
                            | np.int64
                            | np.int32
                            | np.int16
                            | str,
                        ):
                            dfs = []

                            _years = self.__dict__[p].year
                            _list_entries = list(range(len(_years)))
                            _values = self.__dict__[p].value
                            for l in _list_entries:

                                df = pd.DataFrame(
                                    {
                                        "parameter": p,
                                        "year": _years[l],
                                        "unit": self.__dict__[p].unit,
                                        "property": df_sig.iloc[0]["uncertainty"],
                                        "value": _values[l],
                                        "parameter_type": self.__dict__[p].type,
                                        "lci_flag": self.__dict__[p].lci_flag,
                                    },
                                    index=[self.__dict__[p].position],
                                )
                                dfs.append(df)
                            df = pd.concat(dfs)

                            df_steps = pd.concat([df_steps, df])
                            df_steps.index.name = "position"

                        elif isinstance(
                            self.__dict__[p].value[0], np.ndarray
                        ) and not np.all(
                            self.__dict__[p].value[0] == self.__dict__[p].value[0][0]
                        ):
                            dfs = []

                            _years = self.__dict__[p].year
                            _list_entries = list(range(len(_years)))
                            _values = self.__dict__[p].value
                            for l in _list_entries:
                                f = Fitter(
                                    self.__dict__[p].value,
                                    distributions=[
                                        "lognorm",
                                        "logistic",
                                        "truncnorm",
                                        "uniform",
                                        "norm",
                                    ],
                                )
                                f.fit()
                                r = f.get_best()
                                distribution = list(r.keys())[0]
                                logger.info(
                                    f"Best fit for parameter '{p}' is '{distribution}' distribution."
                                )
                                prop = ["mean", "sd", "distribution"]
                                values = [
                                    _values[l].mean(),
                                    _values[l].std(),
                                    distribution,
                                ]
                                df = pd.DataFrame(
                                    {
                                        "parameter": [p, p, p],
                                        "year": [
                                            _years[l],
                                            _years[l],
                                            _years[l],
                                        ],
                                        "unit": [
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                        ],
                                        "property": prop,
                                        "value": values,
                                        "parameter_type": [
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                        ],
                                        "lci_flag": [
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                        ],
                                    },
                                    index=[
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                    ],
                                )
                                dfs.append(df)
                            df = pd.concat(dfs)
                            df_steps = pd.concat([df_steps, df])
                            df_steps.index.name = "position"
                            del f
                        elif isinstance(
                            self.__dict__[p].value[0], np.ndarray
                        ) and np.all(
                            self.__dict__[p].value[0] == self.__dict__[p].value[0][0]
                        ):
                            dfs = []

                            _years = self.__dict__[p].year
                            _list_entries = list(range(len(_years)))
                            _values = self.__dict__[p].value
                            for l in _list_entries:
                                df = pd.DataFrame(
                                    {
                                        "parameter": [p, p, p],
                                        "year": [
                                            _years[l],
                                            _years[l],
                                            _years[l],
                                        ],
                                        "unit": [
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                        ],
                                        "property": ["mean", "sd", "distribution"],
                                        "value": [
                                            self.__dict__[p].value[0][0],
                                            0.0,
                                            "none",
                                        ],
                                        "parameter_type": [
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                        ],
                                        "lci_flag": [
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                        ],
                                    },
                                    index=[
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                    ],
                                )
                                dfs.append(df)
                            df = pd.concat(dfs)

                            df_steps = pd.concat([df_steps, df])
                            df_steps.index.name = "position"
                        elif isinstance(
                            self.__dict__[p].value[0],
                            uct.core.Variable | uct.core.AffineScalarFunc,
                        ):
                            dfs = []

                            _years = self.__dict__[p].year
                            _list_entries = list(range(len(_years)))
                            _values = self.__dict__[p].value
                            for l in _list_entries:
                                df = pd.DataFrame(
                                    {
                                        "parameter": [p, p, p],
                                        "year": [
                                            _years[l],
                                            _years[l],
                                            _years[l],
                                        ],
                                        "unit": [
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                            self.__dict__[p].unit,
                                        ],
                                        "property": ["mean", "sd", "distribution"],
                                        "value": [
                                            _values[l].nominal_value,
                                            _values[l].std_dev,
                                            "norm",
                                        ],
                                        "parameter_type": [
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                            self.__dict__[p].type,
                                        ],
                                        "lci_flag": [
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                            self.__dict__[p].lci_flag,
                                        ],
                                    },
                                    index=[
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                        self.__dict__[p].position,
                                    ],
                                )
                                dfs.append(df)
                            df = pd.concat(dfs)

                            df_steps = pd.concat([df_steps, df])
                            df_steps.index.name = "position"

                    else:
                        raise TypeError(
                            f"{type(self.__dict__[p].value)} is type of value for {p}"
                        )
                if p != "signature":
                    df = pd.DataFrame(
                        {
                            "description": self._metadata(
                                parameter=p,
                                eq_name=self.__dict__[p].eq_name,
                                _external_metadata=external_metadata,
                                _ext_functions=external_functions,
                            )
                        },
                        index=[p],
                    )
                    df_descr = pd.concat([df_descr, df])
                df_descr.index.name = "parameter"

            dict_bonsai = None

            if bonsai:
                df_supply = (
                    dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty.Supply_uncertainty.get_empty_dataframe()
                )
                df_use = (
                    dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty.Use_uncertainty.get_empty_dataframe()
                )
                df_emission = (
                    dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty.Emissions_uncertainty.get_empty_dataframe()
                )
                df_transf_coeff = (
                    dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty.TransferCoefficient_uncertainty.get_empty_dataframe()
                )
                df_resource = (
                    dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty.Resource_uncertainty.get_empty_dataframe()
                )
                # single value
                _year = df_sig.at[0, "year"]
                _activity = df_sig.at[0, "activity"]
                _region = df_sig.at[0, "region"]

                # dataframe with 1 or 3 columns for each entity
                _df_emission = df_steps[
                    df_steps["lci_flag"].str.startswith("emission|", na=False)
                ]
                _df_resource = df_steps[
                    df_steps["lci_flag"].str.startswith("resource|", na=False)
                ]
                _df_supply = df_steps[
                    df_steps["lci_flag"].str.startswith("supply|", na=False)
                ]
                _df_use = df_steps[
                    df_steps["lci_flag"].str.startswith("use|", na=False)
                ]
                _df_transf_coeff = df_steps[
                    df_steps["lci_flag"].str.startswith("transf_coeff|", na=False)
                ]

                # put values into bonsai frames
                for i in _df_emission.index.unique():
                    try:
                        df_emission.loc[i, "value"] = _df_emission.loc[i][
                            _df_emission.loc[i]["property"] == "mean"
                        ]["value"].values[0]
                        df_emission.loc[i, "standard_deviation"] = _df_emission.loc[i][
                            _df_emission.loc[i]["property"] == "sd"
                        ]["value"].values[0]
                        df_emission.loc[i, "distribution"] = _df_emission.loc[i][
                            _df_emission.loc[i]["property"] == "distribution"
                        ]["value"].values[0]
                        df_emission.loc[i, "emission_substance"] = (
                            _df_emission.loc[i]["lci_flag"].unique()[0].split("|")[2]
                        )
                        df_emission.loc[i, "compartment"] = (
                            _df_emission.loc[i]["lci_flag"].unique()[0].split("|")[1]
                        )
                        # df_emission.loc[i, "emission"] = _df_emission.loc[i][
                        #    "lci_flag"
                        # ].unique()[0]
                    except (IndexError, KeyError):
                        df_emission.loc[i, "value"] = _df_emission.loc[i]["value"]
                        df_emission.loc[i, "emission_substance"] = _df_emission.loc[i][
                            "lci_flag"
                        ].split("|")[2]
                        df_emission.loc[i, "compartment"] = _df_emission.loc[i][
                            "lci_flag"
                        ].split("|")[1]
                        # df_emission.loc[i, "emission"] = _df_emission.loc[i]["lci_flag"]
                    df_emission.loc[i, "time"] = _year
                    df_emission.loc[i, "location"] = _region
                    if isinstance(_df_emission.loc[i]["unit"], str):
                        df_emission.loc[i, "unit"] = _df_emission.loc[i]["unit"]
                    else:
                        df_emission.loc[i, "unit"] = _df_emission.loc[i][
                            "unit"
                        ].unique()[0]
                    df_emission.loc[i, "activity"] = _activity
                    df_emission.loc[i, "year_emission"] = _df_emission["year"].unique()[
                        0
                    ]
                for i in _df_resource.index.unique():
                    try:
                        df_resource.loc[i, "value"] = _df_resource.loc[i][
                            _df_resource.loc[i]["property"] == "mean"
                        ]["value"].values[0]
                        df_resource.loc[i, "standard_deviation"] = _df_resource.loc[i][
                            _df_resource.loc[i]["property"] == "sd"
                        ]["value"].values[0]
                        df_resource.loc[i, "distribution"] = _df_resource.loc[i][
                            _df_resource.loc[i]["property"] == "distribution"
                        ]["value"].values[0]
                        df_resource.loc[i, "emisssion_substance"] = (
                            _df_emission.loc[i]["lci_flag"].unique()[0].split("|")[2]
                        )
                        df_resource.loc[i, "compartment"] = (
                            _df_resource.loc[i]["lci_flag"].unique()[0].split("|")[1]
                        )
                        # df_emission.loc[i, "emission"] = _df_emission.loc[i][
                        #    "lci_flag"
                        # ].unique()[0]
                    except (IndexError, KeyError):
                        df_resource.loc[i, "value"] = _df_resource.loc[i]["value"]
                        df_resource.loc[i, "emission_substance"] = _df_resource.loc[i][
                            "lci_flag"
                        ].split("|")[2]
                        df_resource.loc[i, "compartment"] = _df_resource.loc[i][
                            "lci_flag"
                        ].split("|")[1]
                        # df_emission.loc[i, "emission"] = _df_emission.loc[i]["lci_flag"]
                    df_resource.loc[i, "time"] = _year
                    df_resource.loc[i, "location"] = _region
                    if isinstance(_df_resource.loc[i]["unit"], str):
                        df_resource.loc[i, "unit"] = _df_resource.loc[i]["unit"]
                    else:
                        df_resource.loc[i, "unit"] = _df_resource.loc[i][
                            "unit"
                        ].unique()[0]
                    df_resource.loc[i, "activity"] = _activity
                    df_resource.loc[i, "year_emission"] = _df_resource["year"].unique()[
                        0
                    ]
                for i in _df_supply.index:
                    try:
                        df_supply.loc[i, "value"] = _df_supply.loc[i][
                            _df_supply.loc[i]["property"] == "mean"
                        ]["value"].values[0]
                        df_supply.loc[i, "standard_deviation"] = _df_supply.loc[i][
                            _df_supply.loc[i]["property"] == "sd"
                        ]["value"].values[0]
                        df_supply.loc[i, "distribution"] = _df_supply.loc[i][
                            _df_supply.loc[i]["property"] == "distribution"
                        ]["value"].values[0]
                        df_supply.loc[i, "product"] = (
                            _df_supply.loc[i]["lci_flag"].unique()[0].split("|")[2]
                        )
                        df_supply.loc[i, "product_type"] = (
                            _df_supply.loc[i]["lci_flag"].unique()[0].split("|")[1]
                        )
                    except (IndexError, KeyError):
                        df_supply.loc[i, "value"] = _df_supply.loc[i]["value"]
                        df_supply.loc[i, "product"] = _df_supply.loc[i][
                            "lci_flag"
                        ].split("|")[2]
                        df_supply.loc[i, "product_type"] = _df_supply.loc[i][
                            "lci_flag"
                        ].split("|")[1]

                    df_supply.loc[i, "time"] = _year
                    df_supply.loc[i, "location"] = _region
                    if isinstance(_df_supply.loc[i]["unit"], str):
                        df_supply.loc[i, "unit"] = _df_supply.loc[i]["unit"]
                    else:
                        df_supply.loc[i, "unit"] = _df_supply.loc[i]["unit"].unique()[0]
                    df_supply.loc[i, "activity"] = _activity
                for i in _df_use.index:
                    try:
                        df_use.loc[i, "value"] = _df_use.loc[i][
                            _df_use.loc[i]["property"] == "mean"
                        ]["value"].values[0]
                        df_use.loc[i, "standard_deviation"] = _df_use.loc[i][
                            _df_use.loc[i]["property"] == "sd"
                        ]["value"].values[0]
                        df_use.loc[i, "distribution"] = _df_use.loc[i][
                            _df_use.loc[i]["property"] == "distribution"
                        ]["value"].values[0]
                        df_use.loc[i, "product"] = (
                            _df_use.loc[i]["lci_flag"].unique()[0].split("|")[2]
                        )
                        df_use.loc[i, "product_type"] = (
                            _df_use.loc[i]["lci_flag"].unique()[0].split("|")[1]
                        )
                    except (IndexError, KeyError):
                        df_use.loc[i, "value"] = _df_use.loc[i]["value"]
                        df_use.loc[i, "product"] = _df_use.loc[i]["lci_flag"].split(
                            "|"
                        )[2]
                        df_use.loc[i, "product_type"] = _df_use.loc[i][
                            "lci_flag"
                        ].split("|")[1]
                    df_use.loc[i, "time"] = _year
                    df_use.loc[i, "location"] = _region
                    if isinstance(_df_use.loc[i]["unit"], str):
                        df_use.loc[i, "unit"] = _df_use.loc[i]["unit"]
                    else:
                        df_use.loc[i, "unit"] = _df_use.loc[i]["unit"].unique()[0]
                    df_use.loc[i, "activity"] = _activity
                for i in _df_transf_coeff.index:
                    try:
                        df_transf_coeff.loc[
                            i, "coefficient_value"
                        ] = _df_transf_coeff.loc[i][
                            _df_transf_coeff.loc[i]["property"] == "mean"
                        ][
                            "value"
                        ].values[
                            0
                        ]

                        df_transf_coeff.loc[
                            i, "standard_deviation"
                        ] = _df_transf_coeff.loc[i][
                            _df_transf_coeff.loc[i]["property"] == "sd"
                        ][
                            "value"
                        ].values[
                            0
                        ]

                        df_transf_coeff.loc[i, "distribution"] = _df_transf_coeff.loc[
                            i
                        ][_df_transf_coeff.loc[i]["property"] == "distribution"][
                            "value"
                        ].values[
                            0
                        ]

                        df_transf_coeff.loc[i, "output_product"] = (
                            _df_transf_coeff.loc[i]["lci_flag"]
                            .unique()[0]
                            .split("|")[3]
                        )

                        df_transf_coeff.loc[i, "input_product"] = (
                            _df_transf_coeff.loc[i]["lci_flag"]
                            .unique()[0]
                            .split("|")[2]
                        )
                        df_transf_coeff.loc[i, "transfer_type"] = (
                            _df_transf_coeff.loc[i]["lci_flag"]
                            .unique()[0]
                            .split("|")[1]
                        )
                    except (IndexError, KeyError):
                        df_transf_coeff.loc[i, "coefficient_value"] = (
                            _df_transf_coeff.loc[i]["value"]
                        )

                        df_transf_coeff.loc[i, "output_product"] = _df_transf_coeff.loc[
                            i
                        ]["lci_flag"].split("|")[3]

                        df_transf_coeff.loc[i, "input_product"] = _df_transf_coeff.loc[
                            i
                        ]["lci_flag"].split("|")[2]

                        df_transf_coeff.loc[i, "transfer_type"] = _df_transf_coeff.loc[
                            i
                        ]["lci_flag"].split("|")[1]

                    df_transf_coeff.loc[i, "time"] = _year
                    df_transf_coeff.loc[i, "location"] = _region
                    if isinstance(_df_transf_coeff.loc[i]["unit"], str):
                        df_transf_coeff.loc[i, "unit"] = _df_transf_coeff.loc[i]["unit"]
                    else:
                        df_transf_coeff.loc[i, "unit"] = _df_transf_coeff.loc[i][
                            "unit"
                        ].unique()[0]
                    df_transf_coeff.loc[i, "activity"] = _activity

                df_emission.reset_index(drop=True, inplace=True)
                df_resource.reset_index(drop=True, inplace=True)
                df_supply.reset_index(drop=True, inplace=True)
                df_use.reset_index(drop=True, inplace=True)
                df_transf_coeff.reset_index(drop=True, inplace=True)

                dict_bonsai = {
                    "supply": df_supply,
                    "use": df_use,
                    "emission": df_emission,
                    "resource": df_resource,
                    "transf_coeff": df_transf_coeff,
                }

                for k, v in dict_bonsai.items():
                    if v.empty:
                        logger.info(
                            f"Bonsai '{k}' table is empty. For waste treatment activities in supply tables you might need to define a supplied product by your own."
                        )

        if bonsai == "samples":
            for p in self.__dict__:
                # Create DataFrame for each parameter attribute
                if p == "signature":
                    df_sig = pd.DataFrame(self.__dict__[p], index=[0])
                    df_sig.index.name = "position"
                else:
                    df = pd.DataFrame(
                        {
                            "parameter": p,
                            "year": [self.__dict__[p].year],
                            "unit": self.__dict__[p].unit,
                            "property": df_sig.iloc[0]["uncertainty"],
                            "value": [self.__dict__[p].value],
                            "parameter_type": [self.__dict__[p].type],
                            "lci_flag": [self.__dict__[p].lci_flag],
                        },
                        index=[self.__dict__[p].position],
                    )
                    df_steps = pd.concat([df_steps, df])
                    df_steps.index.name = "position"

                if p != "signature":
                    df = pd.DataFrame(
                        {
                            "description": self._metadata(
                                parameter=p,
                                eq_name=self.__dict__[p].eq_name,
                                _external_metadata=external_metadata,
                                _ext_functions=external_functions,
                            )
                        },
                        index=[p],
                    )
                    df_descr = pd.concat([df_descr, df])
                    df_descr.index.name = "parameter"

            # further
            df_supply = (
                dataio.schemas.bonsai_api.PPF_fact_schemas_samples.Supply_samples.get_empty_dataframe()
            )
            df_use = (
                dataio.schemas.bonsai_api.PPF_fact_schemas_samples.Use_samples.get_empty_dataframe()
            )
            df_emission = (
                dataio.schemas.bonsai_api.PPF_fact_schemas_samples.Emissions_samples.get_empty_dataframe()
            )
            df_resource = (
                dataio.schemas.bonsai_api.PPF_fact_schemas_samples.Resource_samples.get_empty_dataframe()
            )
            df_transf_coeff = (
                dataio.schemas.bonsai_api.PPF_fact_schemas_samples.TransferCoefficient_samples.get_empty_dataframe()
            )
            # single value
            _year = df_sig.at[0, "year"]
            _activity = df_sig.at[0, "activity"]
            _region = df_sig.at[0, "region"]
            # dataframe with 1 or 3 columns for each entity
            _df_emission = df_steps[
                df_steps["lci_flag"].str.startswith("emission|", na=False)
            ]
            _df_resource = df_steps[
                df_steps["lci_flag"].str.startswith("resource|", na=False)
            ]
            _df_supply = df_steps[
                df_steps["lci_flag"].str.startswith("supply|", na=False)
            ]
            _df_use = df_steps[df_steps["lci_flag"].str.startswith("use|", na=False)]
            _df_transf_coeff = df_steps[
                df_steps["lci_flag"].str.startswith("transf_coeff|", na=False)
            ]

            # df_emission = df_emission["values"].astype(object)
            # df_emission = df_emission["samples"].astype(object)

            # put values into bonsai frames
            for i in _df_emission.index.unique():
                value_type = _df_emission.loc[i]["value"]
                if isinstance(value_type, float):
                    df_emission.loc[i, "samples"] = [_df_emission.loc[i]["value"]]
                    df_emission.loc[i, "value"] = _df_emission.loc[i]["value"]
                else:
                    new_row = pd.DataFrame(
                        [[_df_emission.loc[i]["value"].tolist()]],
                        columns=["samples"],
                        index=[i],
                    )
                    df_emission = pd.concat([df_emission, new_row])
                    df_emission.loc[i, "value"] = _df_emission.loc[i]["value"].mean()

                # df_emission.loc[i, "value"] = _df_emission.loc[i]["value"].mean()
                # df_emission = pd.DataFrame([[_df_emission.loc[i]["value"].tolist()]], columns=["samples"], index=[i])
                # df_emission.loc[i, "samples"] = _df_emission.loc[i]["value"].tolist()
                df_emission.loc[i, "emission_substance"] = _df_emission.loc[i][
                    "lci_flag"
                ].split("|")[2]
                df_emission.loc[i, "compartment"] = _df_emission.loc[i][
                    "lci_flag"
                ].split("|")[1]
                df_emission.loc[i, "time"] = _year
                df_emission.loc[i, "location"] = _region
                if isinstance(_df_emission.loc[i]["unit"], str):
                    df_emission.loc[i, "unit"] = _df_emission.loc[i]["unit"]
                else:
                    df_emission.loc[i, "unit"] = _df_emission.loc[i]["unit"].unique()[0]
                df_emission.loc[i, "activity"] = _activity
                df_emission.loc[i, "year_emission"] = _df_emission["year"].unique()[0]

            for i in _df_resource.index.unique():
                value_type = _df_resource.loc[i]["value"]
                if isinstance(value_type, float):
                    df_resource.loc[i, "samples"] = [_df_resource.loc[i]["value"]]
                    df_resource.loc[i, "value"] = _df_resource.loc[i]["value"]
                else:
                    new_row = pd.DataFrame(
                        [[_df_resource.loc[i]["value"].tolist()]],
                        columns=["samples"],
                        index=[i],
                    )
                    df_resource = pd.concat([df_resource, new_row])
                    df_resource.loc[i, "value"] = _df_resource.loc[i]["value"].mean()

                # df_emission.loc[i, "value"] = _df_emission.loc[i]["value"].mean()
                # df_emission = pd.DataFrame([[_df_emission.loc[i]["value"].tolist()]], columns=["samples"], index=[i])
                # df_emission.loc[i, "samples"] = _df_emission.loc[i]["value"].tolist()
                df_resource.loc[i, "emission_substance"] = _df_resource.loc[i][
                    "lci_flag"
                ].split("|")[2]
                df_resource.loc[i, "compartment"] = _df_resource.loc[i][
                    "lci_flag"
                ].split("|")[1]
                df_resource.loc[i, "time"] = _year
                df_resource.loc[i, "location"] = _region
                if isinstance(_df_resource.loc[i]["unit"], str):
                    df_resource.loc[i, "unit"] = _df_resource.loc[i]["unit"]
                else:
                    df_resource.loc[i, "unit"] = _df_resource.loc[i]["unit"].unique()[0]
                df_resource.loc[i, "activity"] = _activity
                df_resource.loc[i, "year_emission"] = _df_resource["year"].unique()[0]

            for i in _df_supply.index:
                value_type = _df_supply.loc[i]["value"]
                if isinstance(value_type, float):
                    df_supply.loc[i, "samples"] = [_df_supply.loc[i]["value"]]
                    df_supply.loc[i, "value"] = _df_supply.loc[i]["value"]
                else:
                    new_row = pd.DataFrame(
                        [[_df_supply.loc[i]["value"].tolist()]],
                        columns=["samples"],
                        index=[i],
                    )
                    df_supply = pd.concat([df_supply, new_row])
                    df_supply.loc[i, "value"] = _df_supply.loc[i]["value"].mean()

                # df_supply.loc[i, "value"] = _df_supply.loc[i]["value"].mean()
                # df_supply = pd.DataFrame([[_df_supply.loc[i]["value"].tolist()]], columns=["samples"], index=[i])
                df_supply.loc[i, "product"] = _df_supply.loc[i]["lci_flag"].split("|")[
                    2
                ]
                df_supply.loc[i, "product_type"] = _df_supply.loc[i]["lci_flag"].split(
                    "|"
                )[1]

                df_supply.loc[i, "time"] = _year
                df_supply.loc[i, "location"] = _region
                if isinstance(_df_supply.loc[i]["unit"], str):
                    df_supply.loc[i, "unit"] = _df_supply.loc[i]["unit"]
                else:
                    df_supply.loc[i, "unit"] = _df_supply.loc[i]["unit"].unique()[0]
                df_supply.loc[i, "activity"] = _activity
            for i in _df_use.index:
                value_type = _df_use.loc[i]["value"]
                if isinstance(value_type, float):
                    df_use.loc[i, "samples"] = [_df_use.loc[i]["value"]]
                    df_use.loc[i, "value"] = _df_use.loc[i]["value"]
                else:
                    new_row = pd.DataFrame(
                        [[_df_use.loc[i]["value"].tolist()]],
                        columns=["samples"],
                        index=[i],
                    )
                    df_use = pd.concat([df_use, new_row])
                    df_use.loc[i, "value"] = _df_use.loc[i]["value"].mean()

                # df_use.loc[i, "value"] = _df_use.loc[i]["value"].mean()
                # df_use = pd.DataFrame([[_df_use.loc[i]["value"].tolist()]], columns=["samples"], index=[i])
                df_use.loc[i, "product"] = _df_use.loc[i]["lci_flag"].split("|")[2]
                df_use.loc[i, "product_type"] = _df_use.loc[i]["lci_flag"].split("|")[1]
                df_use.loc[i, "time"] = _year
                df_use.loc[i, "location"] = _region
                if isinstance(_df_use.loc[i]["unit"], str):
                    df_use.loc[i, "unit"] = _df_use.loc[i]["unit"]
                else:
                    df_use.loc[i, "unit"] = _df_use.loc[i]["unit"].unique()[0]
                df_use.loc[i, "activity"] = _activity
            for i in _df_transf_coeff.index:
                value_type = _df_transf_coeff.loc[i]["value"]
                if isinstance(value_type, float):
                    df_transf_coeff.loc[i, "samples"] = [
                        _df_transf_coeff.loc[i]["value"]
                    ]
                    df_transf_coeff.loc[i, "coefficient_value"] = _df_transf_coeff.loc[
                        i
                    ]["value"]
                else:
                    new_row = pd.DataFrame(
                        [[_df_transf_coeff.loc[i]["value"].tolist()]],
                        columns=["samples"],
                        index=[i],
                    )
                    df_transf_coeff = pd.concat([df_transf_coeff, new_row])
                    df_transf_coeff.loc[i, "coefficient_value"] = _df_transf_coeff.loc[
                        i
                    ]["value"].mean()

                df_transf_coeff.loc[i, "output_product"] = _df_transf_coeff.loc[i][
                    "lci_flag"
                ].split("|")[3]

                df_transf_coeff.loc[i, "input_product"] = _df_transf_coeff.loc[i][
                    "lci_flag"
                ].split("|")[2]

                df_transf_coeff.loc[i, "transfer_type"] = _df_transf_coeff.loc[i][
                    "lci_flag"
                ].split("|")[1]

                df_transf_coeff.loc[i, "time"] = _year
                df_transf_coeff.loc[i, "location"] = _region
                if isinstance(_df_transf_coeff.loc[i]["unit"], str):
                    df_transf_coeff.loc[i, "unit"] = _df_transf_coeff.loc[i]["unit"]
                else:
                    df_transf_coeff.loc[i, "unit"] = _df_transf_coeff.loc[i][
                        "unit"
                    ].unique()[0]
                df_transf_coeff.loc[i, "activity"] = _activity

            df_emission.reset_index(drop=True, inplace=True)
            df_resource.reset_index(drop=True, inplace=True)
            df_supply.reset_index(drop=True, inplace=True)
            df_use.reset_index(drop=True, inplace=True)
            df_transf_coeff.reset_index(drop=True, inplace=True)

            dict_bonsai = {
                "supply": df_supply,
                "use": df_use,
                "emission": df_emission,
                "resource": df_resource,
                "transf_coeff": df_transf_coeff,
            }

            for k, v in dict_bonsai.items():
                if v.empty:
                    logger.info(
                        f"Bonsai '{k}' table is empty. For waste treatment activities in supply tables you might need to define a supplied product by your own."
                    )

        dict_of_df["signature"] = df_sig
        dict_of_df["steps"] = df_steps
        dict_of_df["description"] = df_descr
        dict_of_df["bonsai"] = dict_bonsai

        return dict_of_df
