---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.8
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"tags": []}

# Botany

## Setup

The following table lists the varied parameters and their ranges.

| variable  | min    | max    | unit  | description                       |
|-----------|--------|--------|-------|-----------------------------------|
|  thls     | 297.5  | 299.5  |  K    | sea surface potential temperature |
|   u0      |  -5    |  -15   | m/s   | surface wind                      |
|  qt0      | 0.0135 |        | kg/kg | surface humidity                  |   
| qt_lambda |  1200  |  2500  | m     | humidity length scale             |
| thl_Gamma |   4.5  |   5.5  | K/m   | lapse rate                        |
| wpamp     | -0.0035| 0.0018 | cm/s  | subsidence parameter              |
| dudz      | 0.0022 | 0.0022 | m/s^2 | wind shear *                      |


## Availability of simulation output

Currently, 2D output is available for ensemble members 1...40.

+++

## Accessing the data with Python


```{code-cell} ipython3
import matplotlib.pyplot as plt
import eurec4a
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
plt.style.use(["./mplstyle/book", "./mplstyle/wide"])
cat = eurec4a.get_intake_catalog()
```

+++ {"tags": []}


### The parameters of the ensemble members

```{code-cell} ipython3
:tags: []

parameters = cat.simulations.DALES.botany.dx100m.nx768.parameters.read()
df = pd.DataFrame.from_records(parameters)
df[["member", "thls", "u0", "qt0", "qt_lambda", "thl_Gamma", "wpamp", "dudz", "location"]][10:20]

```

## Open the simulation dataset

```{code-cell} ipython3
ds = cat.simulations.DALES.botany.dx100m.nx768['2D'].to_dask()
ds.sel(member=10).isel(time=200).lwp.plot()
#plt.axes().set_aspect(1)
plt.gca().set_aspect(1)
```

```{code-cell} ipython3

```
