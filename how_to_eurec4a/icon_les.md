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

# ICON-LES

## Setup

These ICON Large-eddy simulations (LES) presented here are consists of three different domains that have different spatial and temporal extends depending on their horizontal grid-spacing. {numref}`icon_domains` shows the extend of the different simulations.

```{figure} figures/icon_les_domains.jpg
:name: icon_domains
:alt: ICON-LES domain overview
:width: 800px
:align: center

Overview of simulation domains. The location of the Barbados Cloud Observatory (BCO) and the NTAS buoy are marked with a red star at the western and eastern part of the domain, respectively. For a sense of scale, the MODIS image of February 12 is shown with landmasses colored in green to brown depending on height. Satellite image source: NASA Worldview.
```

{numref}`icon_domains` illustrates further the extend of the ICON Storm-resolving simulation (SRM) that provides the boundary conditions for the ICON-624m run. ICON-312m and ICON-156m are both one-way nested in the respective coarser resolution run.

## Availability of simulation output

```{note}
Please note that this section is still under development and might change. Please revisit this page regularly for updates or changes.
```

```{code-cell} ipython3
import numpy as np
import datetime as dt
import dask
import matplotlib.pyplot as plt
import intake
from zarr.errors import PathNotFoundError
from matplotlib import dates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
plt.style.use(["./mplstyle/book", "./mplstyle/wide"])
cat = intake.open_catalog("https://raw.githubusercontent.com/observingClouds/eurec4a-intake/simulations/catalog.yml")
```

```{code-cell} ipython3
:tags: [remove-cell]

def get_datasets(cat, datasets=None, path=""):
    """
    Recursively finding datasets in the given catalog.
    """
    if datasets is None:
        datasets = []
    for child in list(cat):
        desc = cat[child].describe()
        if desc["container"] == "catalog":
            if path != "":
                reference = ".".join(path, child)
            else:
                reference = child
            datasets.extend(get_datasets(cat[child], path=reference))
        else:
            datasets.extend([path + "." + desc["name"]])
    return datasets

icon_les_cat = cat.simulations.ICON
datasets = get_datasets(icon_les_cat)
```

The currently available ICON-LES output is shown in the following:

```{code-cell} ipython3
:tags: [remove-input]

fig, axs = plt.subplots(len(datasets), 1, sharex=True)
fig.set_constrained_layout(False)
xfmt = dates.DateFormatter('%d.%m')
for d, dataset in enumerate(datasets):
    # Load dataset
    try:
        ds = icon_les_cat[dataset].to_dask()
    except PathNotFoundError:
        pass
    axs[d].vlines(ds.time.values, 0, 1)
    axs[d].set_ylabel(dataset.replace(".","\n"), rotation=0, ha='right')
    axs[d].set(yticklabels=[])  # remove the tick labels
    axs[d].tick_params(left=False)  # remove the ticks
axs[d].xaxis.set_major_formatter(xfmt)
plt.tight_layout()
```
