# Changelog


## Version 0.5.2
- remove steam from coke ppf
- fix integer issue in year concordance
- revert changelog
- add more `plastics`
- fix steam in `coke` ppf

## Version 0.5.1

-  add ppf task `methanol`

## Version 0.5.0

- add property `sample` to allow pre-sampled values for parameters (only for tables as pandas.dataframe, not for csv)
- PPF() instance for ppf tasks used in Bonsai
- add ppf tasks: `steel`, `coke`, `cement`
- fixes

## Version 0.4.2

-  use BONSAI color schema for sphinx documentation website
- add `bonsai_dataio` dependency

## Version 0.4.1

- add option `to_frames(bonsai=True)` to create supply, use and emission tables using the Bonsai schemes (for ppf)
- revision of tiere sequences (fixes, metadata)

## Version 0.4.0

- add functions to transform sequence result (dataclass) into dict `to_dict()` and pd.DataFrames `to_frames()`
- use of fitter package to determine the best fit of distribution type in case of MC simulation when calling `to_frames()`
- revision of dimension tables and sequences based on `product` and `activity`
- mapping of `product` and `activity` to "cpc 2.1" and "isic rev 4" classifications
- revision for publication in JOSS (accepted version)
- several fixes (add contributors, fix `metadata()`, add docstrings for sequences)

## Version 0.3.2

- Chapter `Metal` o Volume `Industry` implemented
- new util function for getting dimension levels (only for developers), incl. tests

## Version 0.3.1

- correct for url link to documentation and repo on pypi
- fix country bugs (`NaN` bug for Namibia; Kosovo)

## Version 0.3.0

- change package name to `bonsai_ipcc` (revision for publication in JOSS)

## Version 0.2.1

- revision for publication in JOSS

## Version 0.2.0

- Chapter `Mineral` of Volume `Industry` initilialized
- Concept of `concordance` generalized to other parameters
- update documentation
- update tests

## Version 0.1.11

- Chapter `Soil` of Volume `Agriculture` initialized
- ubdate tutorials
- renaming of functions

## Version 0.1.10

- clean namespaces
- add test for agri-livestock_manure
- renaming of chapters and modules

## Version 0.1.9

- fix path for data when installing package
- fix CI pipeline

## Version 0.1.5

- Chapter `Livestock` of Volume `Agriculture` implemented
- test for frictionless validation of datapackages
- refactoring of bonsai_ipcc/sequence.py
- signature of tier function added as first steps of the sequence
- pdf documention

## Version 0.1.4

- update documentation
- add tutorials
- add test for swd (comparison with IPCC excel result)
- remove non-IPCC related data

## Version 0.1.3

- Adding PPF cement model
- implement all required parameter, dimension tables in the package, even though the IPCC guidelines do not provide data
- add sequences with higher tiers (2 and 3) for volume waste
- fix bugs in csv tables by using frictionless python package
- update folder structure of parameter, concordance and dimension tables
- add metadata for volume waste (ipcc.datapackage.yaml)