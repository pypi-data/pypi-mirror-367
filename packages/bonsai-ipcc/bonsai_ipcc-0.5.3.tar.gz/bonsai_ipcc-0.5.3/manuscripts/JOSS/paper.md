---
title: bonsai_ipcc - a Python package for the calculation of national greenhouse gas inventories

tags:
  - greenhouse gases
  - life cycle assessment
  - climate change
authors:
 - name: Maik Budzinski
   orcid: 0000-0003-2879-1193
   affiliation: 1
 - name: Joao F.D. Rodrigues
   orcid: 0000-0002-1437-0059
   affiliation: 2
 - name: Mathieu Delpierre
   affiliation: 2
affiliations:
 - name: Department of Sustainability and Planning, Aalborg University, Denmark.
   index: 1
 - name: 2.-0 LCA consultants, Aalborg, Denmark.
   index: 2
date: 15 Januar 2024
bibliography: paper.bib
---

# Summary

The aim of the `bonsai_ipcc` Python package is to enable users to calculate national greenhouse gas (GHG) inventories based on the guidelines provided by the International Panel on Climate Change (IPCC) [@ipcc2019].
In implementing the equations and parameter data from these guidelines, the package adheres to the organizational structure outlined in the guidelines' PDF documents, which include volumes and chapters. The package allows users to add their own data. In addition to computing default GHG inventories, the software includes tools for error propagation calculation, such as analytical error propagation and Monte Carlo simulation, both of which are endorsed by the IPCC reports.

# Statement of need

Gathering greenhouse gas (GHG) data is an important step when developing models and scenarios in many environmental sciences.
The official guidelines for estimating national GHG inventories have been widely used in the modelling community, e.g. to create environmentally extended input-output models [@stadler2018; @merciai2018] or datasets for life cycle assessment [@schmidt2021; @nemecek2007].
The IPCC guidelines contain equations and default data that can be used to calculate country-based greenhouse gas inventories, taking into account different production and treatment activities.
However, calculating GHG inventories directly from the report is cumbersome and time consuming, requiring manual data extraction and visual inspection to identify the sequence of formulas that must be implemented.
To facilitate the compilation of GHG inventories, we developed an open-source Python package which stores the default data and implements the formulas of the IPCC report. To the best of our knowledge, `bonsai_ipcc` is the first work that aims to implement all information of the IPCC report. Presently, open-source Python packages exclusively incorporate particular equations from the IPPC reports. Furthermore, the implemented information serve merely as a component rather than the central focus of the Python package. An example is the Python package `hestia_earth.models` that includes specific equations of the volume agriculture to calculate environmental impacts for farms and food products [@hestia2024].

# Structure of the package

The structure of `bonsai_ipcc` Python package is illustrated in figure 1. The equations (in the
following elementary equations) of a chapter are used to define the sequence (tier
approach) to calculate the corresponding GHG inventory. Data for default parameter
values of the guidelines is provided within the package. We use the Python package `frictionless` to describe and validate the provided data tables [@frictionless].

As a user, you choose the sequence and specify the dimensions (e.g., year, region) of the involved parameters. The
result is a sequence of steps that store the involved parameter values and values that
are calculated by elementary equations (represented by circles and rectangles, respectively in figure 1), as well as the involved uncertainty.

![Structure of the bonsai_ipcc Python package](figure1.png)


The package structure also follows the structure of the guidelines for estimating national GHG inventories. Each of the four core `<volume>`s (i.e., energy, agriculture, energy and waste) contains `<chapter>`s with elementary equations, which can be used to define the tier 1, 2 and 3 sequences calculating the inventories for GHG emissions (e.g., CO2, CH4 and N2O).

```
bonsai_ipcc.<volume>.<chapter>.sequence
bonsai_ipcc.<volume>.<chapter>.elementary
```

To distinguish between the different tiers 1, 2 and 3 when calculating the inventories
for GHG emissions, the naming convention of the corresponding methods is as follows.

```
bonsai_ipcc.<volume>.<chapter>.sequence.tier<number>_<GHG>()
```

# Functionality

The core feature of the `bonsai_ipcc` package is to determine GHG emissions for different tiers
based on the provided data.

```
tier<number>_<ghg>(year,region,<producttype>,<activitytype>,uncertainty)
```

Since the IPCC guidelines specify tier methods for each GHG separately, we decided
to make this distinction in the name of the function instead of using an argument.
The outcome is recorded as a series of sequential steps, encompassing all input data and interim findings. Each step provides the parameter's name, along with its corresponding value and unit. This meticulous recording of data input and intermediate results enhances transparency and facilitates comprehensive analysis within the calculation of GHG inventories.

## Data handling

The IPCC guidelines also provide default data for a large amount of parameters that
are used in the elementary equations. This data is included in the Python package. When
including the data into the package, we follow the frictionless standards [@frictionlessdata]. These standards provide patterns to describe data, such as tables, files and datasets. The framework follows the five design principles - simplicity, extensibility, human-editable
and machine-usable, reusable and applicable across different technologies.
The parameter dimension and concordance tables are associated to the volume and chapter where
these data is used.

```
bonsai_ipcc.<volume>.<chapter>.parameter.<table>
bonsai_ipcc.<volume>.<chapter>.dimension.<table>
bonsai_ipcc.<volume>.<chapter>.concordance.<table>
```

The data for parameters and dimensions is stored in tabular format as csv files. To
query the values within the `bonsai_ipcc` package, we use `pandas DataFrame` [@pandas].
To automate the process of selecting the right parameter when building the tier sequences, the package uses the concept of concordance tables.
Thereby, each attribute of a dimension, e.g. country `DE` in the dimension `region`, can be associated to other more aggregated attributes (e.g., `Western Europe`). This has the advantage that parameter values can be selected from other attributes in cases where the guidelines only provide data for more aggregated ones.
When reading the values from a specific parameter table, the sequence algorithm first tries to find the dimension on the left hand side and proceeds stepwise to the right until a value is found. The same principle is used for other dimensions, including `year` and `<producttype>`.

## Uncertainty
Two methods for uncertainty analysis are implemented in the `ipcc` package: analytical error propagation and Monte Carlo method.
When running the sequence, the type of `value` in each step depends on the selected method for uncertainty calculation (`float` for `uncertainty="def"`, the `ufloat` type of the unertainies library [@uncertainties] for `uncertainty="analytical"` and a `NumPy array` [@numpy] for `uncertainty="monte_carlo"`).
Based on the provided uncertainty information for a parameter table, the algorithm chooses the proper type of uncertainty distribution. The following distribution types are implemented, `normal`, `lognormal`, `truncated normal`, `uniform`, `truncated exponential` and `beta` distribution. Truncated normal distributions are adjusted based on @rodrigues2015 so that original mean and standard deviation are perpetuated.

# Conclusion

The transformation of the IPCC guidelines for calculation greenhouse gas inventories into the `bonsai_ipcc` Python package is an important step towards reproducibility and automation of national GHG inventory results. Furthermore, users of the package can use the results when developing models and scenarios in different scientific fields.
Due to the magnitude of the IPCC guidelines, the implementation of its volumes into the Python package is an ongoing process. To this date one volume (waste) out of the four core volumes has been fully implemented. A second one (agriculture) is in progress. The implementation of a third one (industry) has been started. And a fourth (energy) is waiting to be initialized.

# Acknowledgments

This project has received funding from the KR Foundation.

# References
