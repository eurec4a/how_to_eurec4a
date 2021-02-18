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

### HALO flight phase segmentation
For a quicklook plot we select a small subset of the flight. All HALO flights were split up into flight phases or segments to allow for a precise selection in time and space of a circle or calibration pattern. For more information have a look at the respective [github repository](https://github.com/eurec4a/halo-flight-phase-separation).

In the following, we select a Lidar calibration leg that was flown on the 5th of February and schow further variables only duing that flight segment.

```{code-cell} ipython3
meta = eurec4a.get_flight_segments()
```

* get `segment_id` for all Lidar legs on February 5

```{code-cell} ipython3
segments = [{**s,
             "platform_id": platform_id,
             "flight_id": flight_id
            }
            for platform_id, flights in meta.items()
            for flight_id, flight in flights.items()
            for s in flight["segments"]
           ]
```

```{code-cell} ipython3
segments_by_segment_id = {s["segment_id"]: s for s in segments}
segments_ordered_by_start_time = list(sorted(segments, key=lambda s: s["start"]))
```

```{code-cell} ipython3
lidar_legs = [s["segment_id"]
                 for s in segments_ordered_by_start_time
                 if "lidar_leg" in s["kinds"]
                 and s["start"].date() == datetime.date(2020,2,5)
                 and s["platform_id"] == "HALO"
                ]
lidar_legs
```

* extract data for the Lidar leg 1 segment `HALO-0205_ll1`

```{code-cell} ipython3
segments = {s["segment_id"]: {**s, "flight_id": flight["flight_id"]}
             for platform in meta.values()
             for flight in platform.values()
             for s in flight["segments"]
            }
ll1 = segments["HALO-0205_sl1"]
```

## Cloud parameter

```{code-cell} ipython3
ds_cloud = cat.HALO.WALES.cloudparameter["HALO-0205"].to_dask().load()
ds_cloud
```

Some comments:

* The `cloud_flag` values have the meaning 0 - clear and 1 - cloudy. A backscatter threshold of 10 was used to distinguish between clear and cloudy.

* The cloud optical thickness `cloud_ot` is derived from the HSRL channel following a standard [HSRL method](http://lidar.ssec.wisc.edu/syst/hsrl/node2.htm) that relates the Lidar signal *S* depending on the distance to the aircraft *r* to the optical thickness *OT* by $OT = -1/2 * ln(S(r)/S(0))$.
In clouds with OT greater than about 3.5 the signal to noise ratio is too small meaning that the clouds are intransparent to the Lidar beam, which results in an OT of about 12 in the WALES dataset.

* the cloud or boundary layer top height above sea level `cloud_top` defines a sharp gradient in the backscatter signal. The cloud flag can be used to distinguish between cloud and boundary layer top height.

We select the Lidar leg segment in `time` and you can use the slice to "zoom" a bit more into the measurements.

```{code-cell} ipython3
ds_cloud_ll1 = ds_cloud.sel(time=slice(datetime.datetime(2020, 2, 5, 13, 6, 30),
                                       datetime.datetime(2020, 2, 5, 13, 7, 30)))
```

```{code-cell} ipython3
mask_cloud = np.array(ds_cloud_ll1.cloud_flag, dtype=bool)
cloudtop = ds_cloud_ll1.cloud_top.sel(time=np.array(ds_cloud_ll1.cloud_flag,
                                                    dtype=bool))
BLtop = ds_cloud_ll1.cloud_top.sel(time=np.invert(np.array(ds_cloud_ll1.cloud_flag,
                                                           dtype=bool)))
```

```{code-cell} ipython3
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True,
                                    constrained_layout=True)

ds_cloud_ll1.cloud_flag.sel(time=np.invert(mask_cloud)).plot(ax=ax1, x="time", ls="",
                                                             marker=".", color="C1",
                                                             label="no cloud")
ds_cloud_ll1.cloud_flag.sel(time=mask_cloud).plot(ax=ax1, x="time", ls="", marker=".",
                                                  color="C0", label="cloud")
ax1.set_ylabel(f"{ds_cloud_ll1.cloud_flag.long_name}")
ax1.legend()

ds_cloud_ll1.cloud_ot.plot(ax=ax2, x="time", color="grey")
ax2.set_ylabel(f"{ds_cloud_ll1.cloud_ot.long_name}")

ds_cloud_ll1.cloud_top.sel(time=np.invert(mask_cloud)).plot(ax=ax3, x="time", ls="",
                                                            marker=".", color="C1",
                                                            label="boundary layer")
ds_cloud_ll1.cloud_top.sel(time=mask_cloud).plot(ax=ax3, x="time", ls="", marker=".",
                                                 color="C0", label="cloud")
ax3.set_ylim(0, 2000)
ax3.set_ylabel("cloud or boundary layer top\nheight above sea level [m]")
ax3.legend()

ax1.set_xlabel('')
ax2.set_xlabel('')
ax3.set_xlabel('time in UTC')
for ax in [ax1, ax2, ax3]:
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### Cloud fraction

```{code-cell} ipython3
cf = np.sum(ds_cloud.cloud_flag.values==1) / ds_cloud.cloud_flag.size
cf_ot_gt_3 = np.sum(ds_cloud.cloud_ot.values > 3) / ds_cloud.cloud_flag.size
print(f"Total cloud fraction on Feb 5: {cf*100:.2f} %")
print(f"Fraction of clouds with optical thickness greater than 3: {cf_ot_gt_3*100:.2f} %")
```

We can use a time averaging window to derive a cloud fraction from the `cloud_flag` variable and see how it varies over the course of the flight.

```{code-cell} ipython3
def fraction_from_flag(ds, timedelta):
    return ds.groupby_bins(group=ds.time,
                           bins=np.arange(ds.time.values[0],
                                          ds.time.values[-1],
                                          np.timedelta64(timedelta, "m"))
                          ).mean()
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 4))

for ind, t in enumerate([1, 5, 10]):
    fraction_from_flag(ds_cloud.cloud_flag, t).plot(lw=ind + 1, label=f"{t} min")

ax.set_ylim(0, 1)
ax.set_ylabel("Cloud fraction")
ax.set_xlabel("date: MM-DD HH")
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend(title="averaging period", bbox_to_anchor=(1,1), loc="upper left")
```
