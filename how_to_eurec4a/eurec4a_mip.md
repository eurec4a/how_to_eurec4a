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

# EUREC⁴A-MIP

The EUREC⁴A-Model intercomparison project (EUREC⁴A-MIP) is an ongoing effort to test the ability of a variety of simulations to capture the observed variability of the trade-winds.

```{note}
This section and its subsections are still under development.
```

## Setup
### Boundary conditions
The boundary conditions and warming tendencies are provided on the DKRZ-SWIFT storage. The entire files can be accessed
- via the [EUREC⁴A Intake Catalog](https://github.com/eurec4a/eurec4a-intake)
  ```python
  import xarray as xr
  from intake import open_catalog
  from pandas import date_range

  dates_of_interest = date_range('2020-01-01','2020-03-01', freq='1H')

  cat = open_catalog("https://raw.githubusercontent.com/eurec4a/eurec4a-intake/master/catalog.yml")

  for experiment in ['control', 'warming']:
    bc_cat = cat.simulations.EUREC4A_MIP[experiment].setup.boundary_conditions
    ds = xr.concat([bc_cat(date=d).to_dask() for d in dates_of_interest], dim='time')
    ds.to_netcdf(f"EUREC4A-MIP_boundaryConditions_{experiment}.nc")
  ```

  In addition to the boundary conditions already applied to the ERA5 simulations, the monthly mean climate deltas are also available separately. They are computed from the CMIP6 output of the GFDL-CM4 model {cite:p}`Held:2019` as the difference between the AMIP with patterned 4K SST increase experiment (AMIP-future 4K) and the AMIP historical (AMIP) simulation. Variables available are temperature, relative humidity, surface pressure, horizontal wind and sea and land surface temperature. These monthly mean climate deltas are available as two products.

  - at original GFDL-CM4 resolution
    ```python
    delta_gfdl = cat.simulations.EUREC4A_MIP.warming.setup.boundary_conditions.deltas.GFDL_CM4.to_dask()
    ```
  - at ERA5 horizontal and vertical resolution (interpolated)
    ```python
    delta_era5 = cat.simulations.EUREC4A_MIP.warming.setup.boundary_conditions.deltas.ERA5.to_dask()
    ```

  Instructions on how to install the mandatory packages can be found at the [EUREC⁴A Intake Catalog Repository](https://github.com/eurec4a/eurec4a-intake#usage)
- from the browser interface 
  - [Boundary conditions Control](https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/CTRL_ERA5/)
  - [Boundary conditions Warming+4K](https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/PGW+4K/)
  - [Boundary conditions Warming+4K Deltas on GFDL-CM4 grid](https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/DELTAS_ORI/)
  - [Boundary conditions Warming+4K Deltas interpolated to ERA5 grid](https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/DELTAS_INT/)
- or command line:
  ```bash
  wget -r -H -N --cut-dirs=3 --include-directories="/v1/" "https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/PGW+4K/?show_all"
  wget -r -H -N --cut-dirs=3 --include-directories="/v1/" "https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/CTRL_ERA5/?show_all"
  wget -r -H -N --cut-dirs=3 --include-directories="/v1/" "https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/DELTAS_ORI/?show_all"
  wget -r -H -N --cut-dirs=3 --include-directories="/v1/" "https://swiftbrowser.dkrz.de/public/dkrz_0913c8f3-e7b6-4f94-9221-06880d4ccfea/DELTAS_INT/?show_all"
  ```

## Further references
- [eurec4a.eu](https://eurec4a.eu/motivation)
