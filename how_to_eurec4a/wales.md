---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.8.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# WALES Lidar

The water vapour differential absorption lidar WALES.
WALES operates at four wave-lengths near 935 nm to measure water-vapor mixing ratio profiles covering the whole atmosphere below the aircraft.
The system also contains additional aerosol channels at 532 nm and 1064 nm with depolarization.  WALES uses a high-spectral resolution technique, which distinguishes molecular from particle backscatter.

At typical flight speeds of 200 m/s the backscatter product from the HSRL has a resolution of 200m in the horizontal and 15m in the vertical, while the water vapor product has approximately 3km horizontal and 250m vertical. The PIs during EUREC4A were Martin Wirth and Heike Gross (DLR).

More information on the instrument can be found in [Wirth et al., 2009](https://elib.dlr.de/58175/). If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

*Note: due to safety regulations the Lidar can only be operated above 6 km which leads to data gaps in about the first and last 30 minutes of each flight.*

```{code-cell} ipython3
%pylab inline
```

```{code-cell} ipython3
import eurec4a

import matplotlib as mpl
mpl.rcParams['font.size'] = 12
```

## Get data
To load the data we first load the EUREC4A meta data catalog and list the available datasets from WALES. 

More information on the catalog can be found [here](https://github.com/eurec4a/eurec4a-intake#eurec4a-intake-catalogue).

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog()
print(cat.HALO.WALES.cloudparameter.description)
```

## Cloud parameter

```{code-cell} ipython3
ds_cloud = cat.HALO.WALES.cloudparameter["HALO-0205"].to_dask().load()
ds_cloud
```

We select 1min of flight `time`. You can freely change the times or put `None` instead of the slice start and/or end to get up to the full flight data.

```{code-cell} ipython3
ds_cloud_sel = ds_cloud.sel(time=slice(datetime.datetime(2020, 2, 5, 13, 6, 30),
                                       datetime.datetime(2020, 2, 5, 13, 7, 30)))
```

```{code-cell} ipython3
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True,
                                    constrained_layout=True)

ds_cloud_sel.cloud_mask.sel(time=ds_cloud_sel.cloud_mask==0).plot(ax=ax1, x="time", ls="",
                                                             marker=".", color="C0",
                                                             label="no cloud")
ds_cloud_sel.cloud_mask.sel(time=ds_cloud_sel.cloud_ot<=3).plot(ax=ax1, x="time", ls="", marker=".",
                                                  color="grey", label="cloud with OT <= 3")
ds_cloud_sel.cloud_mask.sel(time=ds_cloud_sel.cloud_ot>3).plot(ax=ax1, x="time", ls="", marker=".",
                                                  color="k", label="cloud with OT > 3")
ax1.set_ylabel(f"{ds_cloud_sel.cloud_mask.long_name}")
ax1.legend()

ds_cloud_sel.cloud_ot.sel(time=ds_cloud_sel.cloud_ot<=3).plot(ax=ax2, x="time", ls="", marker=".",
                                                  color="grey", label="cloud (OT <= 3)")
ds_cloud_sel.cloud_ot.sel(time=ds_cloud_sel.cloud_ot>3).plot(ax=ax2, x="time", ls="", marker=".",
                                                  color="k", label="cloud (OT > 3)")
ax2.set_ylabel(f"{ds_cloud_sel.cloud_ot.long_name}")
ax2.legend()

ds_cloud_sel.pbl_top.plot(ax=ax3, x="time", ls="", marker=".", color="C0", label="boundary layer top")
ds_cloud_sel.cloud_top.sel(time=ds_cloud_sel.cloud_ot<=3).plot(ax=ax3, x="time", ls="", marker=".",
                                                  color="grey", label="cloud top (OT <= 3)")
ds_cloud_sel.cloud_top.sel(time=ds_cloud_sel.cloud_ot>3).plot(ax=ax3, x="time", ls="", marker=".",
                                                  color="k", label="cloud top (OT > 3)")
ax3.set_ylim(0, 2000)
ax3.set_ylabel("height above sea level [m]")
ax3.legend()

ax1.set_xlabel('')
ax2.set_xlabel('')
ax3.set_xlabel('time in UTC')
for ax in [ax1, ax2, ax3]:
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

## Cloud fraction

```{code-cell} ipython3
cf = (((ds_cloud.cloud_mask==1) | (ds_cloud.cloud_mask==2)).sum()
      / (ds_cloud.cloud_mask.size - ((ds_cloud.cloud_mask < 0)
                                     | (ds_cloud.cloud_mask > 2)).sum()))
cf_ot_gt3 = ((ds_cloud.cloud_ot.values > 3).sum()
             / (ds_cloud.cloud_mask.size - ((ds_cloud.cloud_mask < 0)
                                            | (ds_cloud.cloud_mask > 2)).sum()))
print(f"Total cloud fraction on Feb 5: {cf.values * 100:.2f} %")
print(f"Fraction of clouds with optical thickness greater than 3: {cf_ot_gt3.values * 100:.2f} %")
```

We can use a time averaging window to derive a cloud fraction from the `cloud_mask` variable and see how it varies over the course of the flight. We further combine the two cloud flags `probably_cloudy` and `most_likely_cloudy` to a binary cloud mask.

```{code-cell} ipython3
ds_cloud["cloud_mask_binary"] = (ds_cloud.cloud_mask==1) | (ds_cloud.cloud_mask==2)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 4))

ax.set_prop_cycle(color=plt.get_cmap("magma")(np.linspace(0, 1, 4)))
for ind, t in enumerate([1, 5, 10]):
    ds_cloud.cloud_mask_binary.resample(time=f"{t}min",
                                        loffset=f"{t/2}min").mean().plot(lw=ind + 1,
                                                                         label=f"{t} min")

ax.set_ylim(0, 1)
ax.set_ylabel("Cloud fraction")
ax.set_xlabel("date: MM-DD HH")
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend(title="averaging period", bbox_to_anchor=(1,1), loc="upper left")
```
