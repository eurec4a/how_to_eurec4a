---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Cloud Botany with DALES

## Setup

Cloud Botany is a library of idealised large-eddy simulations forced by and initialised with combinations of simplified vertical profiles, parameterised by variables which span a range of conditions corresponding to the variability observed over the EUREC<sup>4</sup>A region and winter. The following table lists the varied parameters and their ranges:

```{list-table} Variables governing Cloud Botany simulations
:header-rows: 1
:name: botany-variables

* - variable
  - min
  - max
  - unit
  - description
* - `thls`
  - 297.5
  - 299.5
  - K
  - sea surface potential temperature
* - `u0`
  - -5
  - -15
  - m/s
  - surface wind
* - `qt_lambda`
  - 1200
  - 2500
  - m
  - humidity scale height
* - `thl_Gamma`
  - 4.5
  - 5.5
  - K/m
  - lapse rate of `thl`
* - `wpamp`
  - -0.5
  - 0.18
  - cm/s
  - Amplitude of subsidence first mode
* - `dudz`
  - 0.0044
  - 0.0044
  - 1/s
  - Wind shear
```
## Availability of simulation output

Cloud Botany contains simulations at a variety of grid resolutions and domain sizes, and each set of simulations comes with its own output. Most of this output is hosted and made available through [DKRZ's Swiftbrowser](https://docs.dkrz.de/doc/datastorage/swift/swiftbrowser.html), and can be accessed through the [`eurec4a-intake`](https://github.com/eurec4a/eurec4a-intake) catalog.

```{code-cell} ipython3
 # Hauke's branch of the intake catalog - not merged yet
 from intake import open_catalog
 url = "https://raw.githubusercontent.com/observingClouds/eurec4a-intake/botany/catalog.yml"
 cat = open_catalog(url)

 # Switch to version below once Botany is fully merged into the intake catalog
 # import eurec4a
 # cat = eurec4a.get_intake_catalog()

 botany_cat = cat.simulations.DALES.botany

```{code-cell} ipython3
:tags: [remove-input]

def tree(cat, level=0):
    prefix = " " * (3*level)
    try:
        for child in list(cat):
            parameters = [p["name"] for p in cat[child].describe().get("user_parameters", [])]
            if len(parameters) > 0:
                parameter_str = " (" + ", ".join(parameters) + ")"
            else:
                parameter_str = ""
            print(prefix + str(child) + parameter_str)
            tree(cat[child], level+1)
    except:
        pass

tree(botany_cat)
```

## Output description

A combination of grid resolution and domain size, e.g. `botany_cat.dx100.nx1535`, contains its own ensemble of cases. To look at the profiles governing the environmnet in which these cases are run, load their `parameters`:

```{code-cell} ipython3
import pandas as pd
varied_parameters = ['member','thls', 'u0', 'qt_lambda', 'thl_Gamma', 'wpamp', 'dudz', 'location']
parameters = cat.simulations.DALES.botany.dx100m.nx1536.parameters.read()
pd.DataFrame.from_records(parameters)[varied_parameters]
```

The `location` column refers to locations the metaphorical hypercube spanned by the variables in {numref}`botany-variables`. For instance, a `corner` is a particular combination of variables at the extreme ends of their co-varied ranges, while the `center` sits in the middle of the cube.

Each other lowest-level data set points to a `.zarr` object that can be loaded as `xarray.Dataset`s following the regular conventions, for example:

```{code-cell} ipython3
import xarray as xr

ds_profiles = botany_cat.dx100m.nx1536['profiles'].to_dask()
ds_profiles
```

Briefly summmarised, the individual data sets contain:

| Name     | What is it? | Dimensions | Output frequency |
|----------|-------------|------------|------------------|
| `profiles` | Vertical profiles of dynamic, thermodynamic, radiation, and microphysical slab statistics | `[member, time, z]` | 5 min |
| `timeseries` | Surface and bulk statistics | `[member, time]` | 1 min |
| `2D` | Vertically integrated and surface diagnostics | `[member, time, x, y]` | 5 min |
| `3D` | Full field dumps of prognostic variables and liquid water specific humidity | `[member, time, x, y, z]` | 1 hour |
| `cross_xy` | Extracted horizontal cross-sections of prognostic variables and liquid water specific humidity | `[member, time, x, y, z]` | 5 min |
| `radiation` | Radiation model output at surface and top-of-atmosphere | `[member, time, x, y]` | 1 hour |

+++

## Visualisations

Thorough visualisations of indicative simulation output, in the form of simple overviews and movies for each simulation in the library, are separately hosted on [a personal server](http://143.178.154.95:3141/), though support for their access cannot be guaranteed. See below for two short examples of accessing and plotting data.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
plt.style.use(["./mplstyle/book", "./mplstyle/wide"])
```

### An overview over the initial profiles of Botany

```{code-cell} ipython3
# Profiles of vertical velocity, from variations in first-mode amplitude
def expsinw(z, ampwp, w0=0.0045, Hw=2500, Hwp=5300):
    '''
    Vertical profiles for imposed, large-scale subsidence velocity
    '''
    w_0 = -w0*(1-np.exp(-z/Hw))
    w_1 = ampwp*np.sin(2.*np.pi/Hwp*z)
    w_1[z>Hwp] = 0.
    return w_0 + w_1

wpamp = np.unique(pd.DataFrame.from_records(parameters)[['wpamp']].to_numpy())

ds_initial = ds_profiles.isel(time=0).sel(zt=slice(0, 5000))

kws = {'y'          : 'zt',
       'add_legend' : False,
       'linewidth'  : 0.5,
       'c'          : 'k'}

fig, axs = plt.subplots(ncols=4, sharey=True, figsize=(10,5))

ds_initial['thl'].plot.line(ax=axs[0], **kws)
ds_initial['qt'].plot.line(ax=axs[1], **kws)
ds_initial['u'].plot.line(ax=axs[2], **kws)

for i, wpampi in enumerate(wpamp):
    axs[3].plot(expsinw(ds_initial['zt'], wpampi), ds_initial['zt'], linewidth=0.5, c='k')
axs[3].set_xlabel('w [m/s]')
    
for i in range(axs.size):
    axs[i].set_title('')
    if i > 0:
        axs[i].set_ylabel('')

plt.show()
```

### Example visualisation of water vapour, clouds, rain and cold pools
For the last time (60 hours after initialisation) for the "center" of the hypercube of simulations (member 1), we might visualise the vertically integrated total specific humidity (the total water path `twp`), the cloud-top height (`cldtop`), the rain-water path (`rwp`) and an indicator for the extent of cold pools (the local mixed-layer height, `hmix`), as follows:

```{code-cell} ipython3
cb_kw = {'fraction' : 0.05}

ds_2D = botany_cat.dx100m.nx1536['2D'].to_dask().sel(member=1).isel(time=-1)
ds_2D
fig, axs = plt.subplots(ncols=3, sharex=True, sharey=True, figsize=(14.5,4))

# Total water path
ds_2D['twp'].plot(ax=axs[0], vmin=33 ,vmax=40, cbar_kwargs=cb_kw)

# Cloud-top height and rain water path
ds_2D['cldtop'].plot(ax=axs[1],cmap='Greys_r', vmin=500, vmax=2000, cbar_kwargs=cb_kw)
rwp_masked = xr.where(ds_2D['rwp'] > 1e-5, ds_2D['rwp'], np.nan)
rwp_masked.plot(ax=axs[1], cmap='Blues', vmin=0, vmax=0.2, alpha=0.8, cbar_kwargs=cb_kw)

# Mixed-layer height
ds_2D['hmix'].plot(ax=axs[2],cmap='RdBu_r', vmin=50, vmax=1000, cbar_kwargs=cb_kw)

plt.show()
```
