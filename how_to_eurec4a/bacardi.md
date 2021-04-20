---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.8.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# BACARDI dataset

The following script exemplifies the access and usage of the Broadband AirCrAft RaDiometer Instrumentation (BACARDI), that combines two sets of Kipp and Zonen broadband radiometer measuring upward and downward irradiance in the solar (pyranometer model CMP-22, 0.2 - 3.6 μm) and terrestrial (pyrgeometer model CGR-4, 4.5 - 42 μm) spectral range.

The dataset is published under [Ehrlich et al. (2021)](https://doi.org/10.25326/160). If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

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
list(cat.HALO.BACARDI)
```

* We can further specify the platform, instrument, if applicable dataset level or variable name, and pass it on to dask.

*Note: have a look at the attributes of the xarray dataset `ds` for all relevant information on the dataset, such as author, contact, or citation infromation.*

```{code-cell} ipython3
ds = cat.HALO.BACARDI.irradiances['HALO-0205'].to_dask()
ds
```

The data from EUREC4A is of 10 Hz measurement frequency and corrected for dynamic temperature effects. For the downward solar irradiance, data are provided with and without aircraft attitude correction corresponding to cloud-free and cloudy conditions above HALO.

+++

## Plots

+++

We plot the upward and downward irradiances in two panels.

```{code-cell} ipython3
mpl.rcParams['font.size'] = 12

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(16,6))
ax1.set_prop_cycle(color=['darkblue', 'red'])
for var in ['F_up_solar', 'F_up_terrestrial']:
    ds[var].plot(ax=ax1,label= var)
ax1.legend()
ax1.set_ylabel('upward solar and terrestrial irradiance')

ax2.set_prop_cycle(color=['grey', 'darkblue', 'skyblue'])
for var in ['F_down_solar_sim', 'F_down_solar', 'F_down_solar_diff']:
    ds[var].plot(ax=ax2, label= var)
ax2.legend()
ax2.set_ylabel('downward solar irradiance')

for ax in [ax1, ax2]:
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

The right plot shows in blue the downward solar irradiance for two different assumptions about conditions above HALO: a 100% diffuse radiation field due to clouds or cloud-free conditions. Whenever the sensor is tilted which is almost always the case within the circles, the measurement is translated to a horizontal plane and within the hemispheric integral of radiance reaching the sensor a small part has to be added based on the assumption of the sky aloft. 

+++

Striking are some spikes. These correspond to the sharp turns of HALO with large roll angles. The stabilizing platform can only correct for a few degrees and if the sensor is tilted towards (away from) the sun, we see a high (low) peak. 

+++

The wiggles originate from the about 200km change in location  and therewith solar zenith angle within one circle / hour as can be seen in a plot.

```{code-cell} ipython3
fig, ax = plt.subplots()
ds.F_down_solar.plot(ax=ax, color = 'darkblue')
ax.set_ylabel('downward solar irradiance \n corrected for cloud-free conditions', color = 'darkblue')
ax2=ax.twinx()
ds.sza.plot(ax=ax2, color = 'black')
ax2.set_ylim(110,28)
```
