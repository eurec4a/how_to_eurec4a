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

# HALO UNIFIED dataset

The HALO UNIFEID dataset is a combination of [HAMP](https://amt.copernicus.org/articles/7/4539/2014/) radar and radiometer measurements, [BAHAMAS](http://www.halo.dlr.de/instrumentation/basis.html) aircraft position data and [dropsonde](https://github.com/Geet-George/JOANNE#joanne---the-eurec4a-dropsonde-dataset) measurements, all on a unified temporal and spatial grid. 

More information on the dataset can be found at `?`. If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

```{code-cell} ipython3
%pylab inline
```

## Get data
* To load the data we first load the EUREC4A meta data catalogue. More information on the catalog can be found [here](https://github.com/eurec4a/eurec4a-intake#eurec4a-intake-catalogue).

```{code-cell} ipython3
import eurec4a
```

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog()
list(cat.HALO.UNIFIED)
```

* We can funrther specify the platform, instrument, if applicable dataset level or variable name, and pass it on to dask.

*Note: have a look at the attributes of the xarray dataset `ds` for all relevant information on the dataset, such as author, contact, or citation infromation.*

```{code-cell} ipython3
ds = cat.HALO.UNIFIED.HAMPradar["HALO-0205"].to_dask()
ds
```

## Load HALO flight phase information
All HALO flights were split up into flight phases or segments to allow for a precise selection in time and space of a circle or calibration pattern. For more information have a look at the respective [github repository](https://github.com/eurec4a/halo-flight-phase-separation).

```{code-cell} ipython3
meta = eurec4a.get_flight_segments()
```
