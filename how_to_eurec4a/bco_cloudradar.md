---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Cloud radar data collected at the Barbados Cloud Observatory (BCO)

+++

## General information

+++

### Getting the data catalog

The python code below allows you to browse through the days avaiable

```{code-cell} ipython3
from datetime import datetime
import matplotlib.pyplot as plt
plt.style.use(["./mplstyle/book", "./mplstyle/wide"])
import numpy as np
import eurec4a
cat = eurec4a.get_intake_catalog()
```

### Getting the data from the BCO Ka-band radar
To get a list of BCO datasets that are available within the catalog, type:

```{code-cell} ipython3
list(cat['barbados.bco'])
```

### Loading the radar dataset
The entire radar dataset of the BCO Ka-band radar can be loaded lazy, i.e. only loading the metadata and not the data such like radar reflectivity itself, by typing:

```{code-cell} ipython3
ds = cat.barbados.bco.radar_reflectivity.to_dask()
```

The variables that this dataset contains can be shown by typing:

```{code-cell} ipython3
ds
```

### Plot some radar quantities
To create time/height plots for radar moments, pick a variable name having dimension `(time, height)` from the list of data variables and type the name in the code below. Common quantities that are used from the radar are radar reflectivity and doppler velocity. The radar reflectivity that is corrected for "rabbit ears" is saved in `Zf`.

In the following an example timeseries for both of these quantities is shown:
to select the entire day :
```{code-cell} ipython3
time_min = np.datetime64('2020-02-12T00:00:00')
time_max = np.datetime64('2020-02-12T23:59:59')

# selecting subset of data
ds_sliced = ds.sel(time=slice(time_min, time_max))
```

```{code-cell} ipython3
fig, axs = plt.subplots(2,1, sharex=True)
# set here the variable from ds to plot, its color map and its min and max values
ds_sliced.Zf.plot(x='time', y='range', cmap="seismic", ax=axs[0])
ds_sliced.VEL.plot(x='time', y='range', cmap="seismic", ax=axs[1])
axs[1].set_xlim(time_min, time_max)
axs[0].set_ylim(0, 4500);
axs[1].set_ylim(0, 4500);
```

### Retrieving cloud fraction profile
The cloud fraction profile provides information about the variability of cloudiness at different height levels. The radar is often used so retrieve such a profile but it should be noted that cloud quantities are not easy to define (see also the section about the [HALO cloud mask product]()). To be precise the following examples shows the hydrometeor fraction (cloud droplets and rain droplets and to some extend moistend sea-salt aerosols) and not the cloud fraction.

```{code-cell} ipython3
fig, ax = plt.subplots()
# calculate the mean cloud fraction profile
(~np.isnan(ds_sliced.Zf.sel(range=slice(0,4500)))).mean(dim='time').plot(y='range', label='no threshold')
# reduce sensitivity
threshold = -50
(ds_sliced.Zf > threshold).sel(range=slice(0,4500)).mean(dim='time').plot(y='range', label=f'{threshold} dBZ')
plt.title("Mean echo fraction")
plt.xlabel('echo fraction')
plt.legend()
```

