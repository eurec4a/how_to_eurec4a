---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.7.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# How to put your measurements into the meso-scale context

The meso-scale patterns of shallow convection as described by [Stevens et al. (2020)](https://doi.org/10.1002/qj.3662)
are a great way to learn more about the meso-scale variability in cloudiness in the
trades. For the time period of the EUREC<sup>4</sup>A campaign, a group of 50 participants
has identified these meso-scale patterns on satellite images. Their classifications build
the *Common Consensus on Convective OrgaNizaTionduring the EUREC4A eXperimenT* dataset, short
C<sup>3</sup>ONTEXT.

Here, a the examples show how the meso-scale patterns at a specific location in time and
space can be retrieved. More details on this dataset can be found at [Schulz (2020)](https://doi.org/10.5194/essd-2021-427)  

```{code-cell} ipython3
import datetime
import eurec4a
```

```{code-cell} ipython3
meta = eurec4a.get_flight_segments()
meta.keys()
```
