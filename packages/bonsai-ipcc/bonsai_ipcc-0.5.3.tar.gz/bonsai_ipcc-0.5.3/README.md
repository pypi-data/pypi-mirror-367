# bonsai_ipcc


The `bonsai_ipcc` python package enables users to calculate national greenhouse gas (GHG) inventories based on the guidelines provided by the International Panel on Climate Change.

By using `volumes` and `chapters`, the python package follows the structure of the IPCC guidelines and allows users to access individual equations and sequences of equations as `bonsai_ipcc.<volume>.<chapter>.elementary.<equation>` or `bonsai_ipcc.<volume>.<chapter>.sequence.<tier_method>`. The package allows users to access the data as Pandas dataframes in `bonsai_ipcc.<volume>.<chapter>.dimension.<table>` or `bonsai_ipcc.<volume>.<chapter>.parameter.<table>`: dimensions list valid coordinates to access parameters; parameters are values to be used in equations. When using the `bonsai_ipcc` python package, it may helpful to also use the [pdf documents](https://www.ipcc-nggip.iges.or.jp/public/2019rf/index.html) for additional information.

The package also allows uncertainty information to be taken into account. Within a sequence, the user can choose between analytical error propagation and Monte Carlo simulation. Thereby, the values of an equation are transformed into [ufloat](https://uncertainties-python-package.readthedocs.io/en/latest/) or [numpy.array](https://numpy.org/doc/stable/reference/generated/numpy.array.html), respectively.

A comrehensive documentation is available [here](https://bonsamurais.gitlab.io/bonsai/util/ipcc).

## Installation for users


You can install the package from PyPi sing `pip`:

```bash
pip install bonsai_ipcc
```

You can also download the package from gitlab.com
Replace the keyword `tag` by the specific version, e.g., `v0.3.0`.

```bash
pip install git+ssh://git@gitlab.com/bonsamurais/bonsai/util/ipcc.git@tag
```

Change `pip` to `pip3` in Linux. Note that the path may change in future versions.

## Installation for developers

### Create a python environment
The `bonsai_ipcc` package requires `python>=3.9`. If you use conda as your python package manager, you could do something like:
```
conda create --name py311 python=3.11
conda activate py311
```

### Install the package in editable mode
```bash
git clone git@gitlab.com:bonsamurais/bonsai/util/ipcc.git
cd bonsai_ipcc
pip install -e .
```

## Basic use

Inside a Python console or notebook, create an instance of the `IPCC` class like this:

```python
import bonsai_ipcc
my_ipcc = bonsai_ipcc.IPCC()
```

With `my_ipcc.<volume>.<chapter>` the `bonsai_ipcc` package follows the structure of the IPCC guidelines.
To show the elementary equations and sequences of a certain chapter in a specific volume:

```python
dir(my_ipcc.waste.swd.elementary)
# dir(my_ipcc.waste.swd.sequence)
```

To find information about a elementary equation:

```python
help(my_ipcc.waste.swd.elementary.ddoc_from_wd_data)
```

The following will print the docstring with information on the parameters and the reqiured units:

```
Help on function ddoc_from_wd_data in module bonsai_ipcc.waste.swd.elementary:

ddoc_from_wd_data_tier1(waste, doc, doc_f, mcf)
    Equation 3.2 (tier 1)

    Calculates the decomposable doc (ddocm) from waste disposal data.

    Argument
    ---------
    waste (tonnes) : float
        Amount of waste
        (either wet or dry-matter, but attention to doc!)
    doc (kg/kg) : float
        Fraction of degradable organic carbon in waste.
    doc_F (kg/kg) : float
        Fraction of doc that can decompose.
    mcf (kg/kg) : float
        CH4 correction factor for aerobic decomposition in the year of decompostion.

    Returns
    -------
    VALUE: float
        Decomposable doc (tonnes/year)
```

To show the dimensions of a certain parameter:

```python
my_ipcc.waste.swd.parameter.mcf.index.names
```
```
FrozenList(['swds_type', 'property'])
```

To find the possible values of a dimension:

```python
my_ipcc.waste.swd.dimension.swds_type.index
```
```
Index(['managed', 'managed_well_s-a', 'managed_poorly_s-a', 'managed_well_a-a',
       'managed_poorly_a-a', 'unmanaged_deep', 'unmanaged_shallow',
       'uncharacterised'],
      dtype='object', name='code')
```

To retrieve the value and the unit of a certain parameter.
```python
my_ipcc.waste.swd.parameter.mcf.loc[("managed","def")]
```
```
value      1.0
unit     kg/kg
Name: (managed, def), dtype: object
```


### Run a tier sequence

Despite the fact that various default data for parameter tables is provided within the `bonsai_ipcc` package, in most cases, the user still needs to collect data to calculate the greenhouse gas inventories.
For the `tier1_co2` sequence in the `incineration` chapter of volume `waste`, data for urban population is required.
The data can be added as a pandas DataFrame.
```python
import bonsai_ipcc
import pandas as pd

# urban population
d = {
    "year": [2010,2010,2010,2010,2010],
    "region": ["DE","DE","DE","DE","DE"],
    "property": [
        "def","min","max","abs_min","abs_max"
    ],
    "value": [
        62940432,61996325.52,63884538.48,0.0,"inf",
    ],
    "unit": [
    "cap/yr","cap/yr","cap/yr","cap/yr","cap/yr",
    ],
}
urb_pop = pd.DataFrame(d).set_index(["year", "region", "property"])

my_ipcc=bonsai_ipcc.IPCC()
my_ipcc.waste.incineration.parameter.urb_population=urb_pop
```

> **_NOTE:_** When adding own data, the user is encouraged to also specify uncertainty information. Property "def" is always required and specifies the mean value. For uncertainty analysis "min", "max", "abs_min" and "abs_max" are required ("min": 2.5 percentile, "max": 97.5 percentile, "abs_min": absolute minimum, "abs_max": absolute maximum).

To get a list of all parameters involved in the sequence, you can do:
```python
my_ipcc.inspect(my_ipcc.waste.incineration.sequence.tier1_co2)
```

To calculate the GHG inventory based on a tier method, specifiy the keywords of the sequence. The keywords are in most cases `year`, `region`, `product`, `activity` and `uncertainty`. Only in view cases more than these are required due to the complexity of the sequence.

```python
my_tier = my_ipcc.waste.incineration.sequence.tier1_co2(
          year=2010, region="DE", product="msw_plastics", activity="inc_unspecified", uncertainty="def")

# show the list of steps of the sequence
my_tier.to_dict()
```
For uncertainty calculation based on Monte Carlo use `uncertainty="monte_carlo"`, for analytical error propagation use `uncertainty="analytical"`.

To retrieve the result's value of a sequence's step, type:
```python
my_tier.co2_emissions.value
```

> **_NOTE:_** The type of `value` depends on the uncertainty assessment. For `uncertainty = "def"`: `type = float`, for `uncertainty = "analytical"`: `type = ufloat` and for `uncertainty = "monte-carlo"`: `type = numpy.array`. Furthermore, some tier sequences provide time series instead of one single value. If so, `value` is of type `numpy.array`, including the values for different years. The type of each years' value also depend on the uncertainty assessment.

### Analyze the results for a tier sequence

The signature, steps, parameter description can be retrieved as pandas DataFrame. By using the `to_frames()` method, a dictionary is provided including the dataframes for:
- signature (includes the arguments that has been used to run the sequence, e.g. `year`, `region`, `activity`, `product`)
- steps (all steps of the sequence in tabular format, including the paramters values)
- description (with the metadata of the involved paramters, including the reference to the ipcc pdf documents)

```
dfs=my_tier.to_frames(bonsai=False)

dfs["signature"]
dfs["steps"]
dfs["description"]
```


### Only for the Bonsai project

For the [Bonsai project](https://gitlab.com/bonsamurais/bonsai) additional sequences are added as so-called paramterized production functions (PPF). These sequences are based on the paramter tables and equations of the ipcc guidelines, but also include additional information required in the project.

```python
from bonsai_ipcc import PPF

my_ppf = PPF()
my_tier = my_ppf.ppf_vol.metal.sequence.coke_tier1(
          year=2010, region="DE", activity="by-product_recovery", uncertainty="def")

# show the list of steps of the sequence
my_tier.to_dict()
```

Contrary to the sequences of `IPCC()`, the sequences of `PPF()` include all greenhouse gas emissions at once.

The following tables are generated by a PPF for an `activity` in a certain `year` and `region`:
- `supply`: supply of products
- `use`: use of products
- `emission`: emissions per activity
- `resource`: resource use per activity
- `transf_coeff`: transfer coefficient, defined as the proportion of a input which is present in a reference output provided by the activity. It indicates that the input is a feedstock material for the activity, and is embodied in the reference output. The transfer coefficients for one input needs to sum up to 1 accross all outputs in which the input is embodied. The transfer coefficients can be used to calculated waste outputs, when no specific information is given, as well as to ensure mass balance.

The additional dataframes can be generated by `to_frames(bonsai=True)`. In doing so, the schemes for the supply, use and emission tables of the Bonsai project are used to create pandas DataFrames, and filled with information based on the tier sequence´s result.
```
dfs=my_tier.to_frames(bonsai=True)

dfs["bonsai"]["use"]
dfs["bonsai"]["supply"]
dfs["bonsai"]["emission"]
dfs["bonsai"]["transf_coeff"]
```

> **_NOTE:_** When using the option `bonsai=True`, only parameters and its values are used to fill the Bonsai tables, which fully correpond to the Bonsai tables. For instance, some sequences do not calculate the amount of the `product` which is genrereatd by the `activity` as a parameter. Thus, the `supply` table would be empty.
