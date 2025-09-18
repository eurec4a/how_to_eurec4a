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
execution:
  timeout: 180
---

# How-to use EUREC⁴A-MIP output

```{note}
This section and its subsections are still under development.
```

## Setting up compute environment

The EUREC⁴A-MIP output is accessible via an Intake catalog, where its underlying zarr files are referenced. To use the catalog, the [EUREC⁴A Intake Catalog Repository](https://github.com/eurec4a/eurec4a-intake#usage) needs to be installed. Alternatively, a working python environment can also be created with e.g. uv:

```bash
uv run --with intake,xarray,intake-xarray,zarr,pydap,s3fs,requests,ipython,jinja2 ipython 
```

The catalog itself can be opened as follows:

```python
from intake import open_catalog
cat = open_catalog("https://raw.githubusercontent.com/eurec4a/eurec4a-intake/eurec4amip/main/catalog.yml")
```

Simulations that are not yet merged to the main catalog can be viewed from their respective branches, e.g.
```{code-cell} ipython3
from intake import open_catalog
cat = open_catalog("https://raw.githubusercontent.com/eurec4a/eurec4a-intake/eurec4amip/add/obc/metoffice/catalog.yml")
```
## Browsing the catalog
The catalog contains not only EUREC⁴A-MIP simulations, but also the observations of the EUREC⁴A field campaign. The catalog structure is hierarchical, so to list the EUREC⁴A-MIP simulations and setups, the following command can be used:

```python
list(cat.simulations.EUREC4A_MIP)
```

applied to on the entire hierarchy, this will list all available datasets:


```{code-cell} ipython3
:tags: [remove-input]

def get_datasets(cat, datasets=None, path=""):
    """
    Recursively finding datasets in the given catalog.
    """
    if datasets is None:
        datasets = []
    for child in list(cat):
        desc = cat[child]._entry
        if hasattr(desc, "container") and desc.container == "catalog":
            if path != "":
                reference = ".".join([path, child])
            else:
                reference = child
            datasets.extend(get_datasets(cat[child], path=reference))
        else:
            datasets.extend([path + "." + desc.name])
    return datasets

eurec4amip_cat = cat.simulations.EUREC4A_MIP
datasets = get_datasets(eurec4amip_cat)
filtered_datasets = [dataset for dataset in datasets if "setup" not in dataset]
print(f"Found {len(datasets)} datasets:")
for dataset in datasets:
    print(f" - {dataset}")
```

The simulation output covers currently the following time period:

```{code-cell} ipython3
:tags: [remove-input]

import matplotlib.pyplot as plt
import matplotlib.dates as dates
import datetime as dt

fig_height = len(filtered_datasets) * 0.5
fig, axs = plt.subplots(len(filtered_datasets), 1, figsize=(8, fig_height), sharex=True)
fig.set_constrained_layout(False)
xfmt = dates.DateFormatter('%d.%m')
for d, dataset in enumerate(filtered_datasets):
    # Load dataset
    try:
        ds = eurec4amip_cat[dataset].to_dask()
        dataset_len = len(ds.time)
        ds = ds.isel(time=slice(0,dataset_len,dataset_len//1000+1))  # select max timesteps
        axs[d].vlines(ds.time.values, 0, 1)
    except FileNotFoundError:
        pass
    axs[d].set_aspect(1.5)
    axs[d].set_ylabel(dataset.replace(".","\n"), rotation=0, ha='right')
    axs[d].set(yticklabels=[])  # remove the tick labels
    axs[d].tick_params(left=False)  # remove the ticks
axs[d].xaxis.set_major_formatter(xfmt)
axs[d].set_xlim([dt.date(2020, 1, 1), dt.date(2020, 3, 1)])
plt.tight_layout()
```

## Loading output from a specific simulation

To load the output of a specific simulation, e.g. the MetOffice open-boundary LES simulations, the respective catalog entry can be accessed as follows:

```{code-cell} ipython3
ds = cat.simulations.EUREC4A_MIP.open_boundary_LEM.unifiedmodel.tab_4_inst.to_dask()
print(ds)
```

This will load the dataset as an `xarray.Dataset` object, which can then be used for further analysis. Note that the data is loaded lazily using `dask`, so no data is actually read until it is needed.

```{code-cell} ipython3
ds.isel(time=10).q2m.plot()
```