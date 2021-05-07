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

# Cloud masks

Different instruments, by virtue of their differing measurement principle and footprint, see clouds in different ways. To provide an overview of the cloud fields sampled by HALO during EUREC4A, a cloud mask is created for each cloud sensitive instrument.  
In the following, we compare the different cloud mask products for a case study on 5 February and further provide a statistical overview for the full campaign period.

More information on the dataset can be found in Konow et al. (in preparation). If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

```{code-cell} ipython3
%pylab inline
```

```{code-cell} ipython3
import eurec4a
import numpy as np
import xarray as xr
import matplotlib as mpl
mpl.rcParams['font.size'] = 12

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm
```

We generally don't support ignoring warnings, however, we do so in this notebook to suppress warnings originating from zero division. Unfortunately, we coudn't find another way to handle the warnings. If you have an idea, please make a pull request and change it :)

```{code-cell} ipython3
import warnings
warnings.filterwarnings("ignore")
```

## Cloud fraction functions
We define some utility functions to extract (circle) cloud cover estimates from different datasets assuming that the datasets follow a certain flag meaning convention.  

In particular, we define a **minimum cloud fraction** based on the cloud mask flag `most_likely_cloudy` and a **maximum cloud fraction** combining the flags `most_likely_cloudy` and `probably_cloudy`. The cloud mask datasets slightly vary in their flag definition for cloud free conditions and their handling of unvalid measurements which is taken care of by the following functions.

```{code-cell} ipython3
def _isvalid(da):
    meanings = dict(zip(da.flag_meanings.split(" "), da.flag_values))
    return ~(np.isnan(da) | ("unknown" in meanings and da==meanings["unknown"]))

def _cloudy_max(da):
    meanings = dict(zip(da.flag_meanings.split(" "), da.flag_values))
    return (da==meanings["most_likely_cloudy"]) | (da==meanings["probably_cloudy"])

def _cloudy_min(da):
    meanings = dict(zip(da.flag_meanings.split(" "), da.flag_values))
    return da==meanings["most_likely_cloudy"]

def cfmin(ds):
    sumdims = [d for d in ds.cloud_mask.dims if d != "time"]
    return (_cloudy_min(ds.cloud_mask).sum(dim=sumdims)
            / _isvalid(ds.cloud_mask).sum(dim=sumdims))

def cfmax(ds):
    sumdims = [d for d in ds.cloud_mask.dims if d != "time"]
    return (_cloudy_max(ds.cloud_mask).sum(dim=sumdims)
            / _isvalid(ds.cloud_mask).sum(dim=sumdims))

def correct_VELOX(ds):
    return ds.assign(CF_min=ds.CF_min.where((ds.CF_min >=0 ) & (ds.CF_min <= 1)),
                     CF_max=ds.CF_max.where((ds.CF_max >=0 ) & (ds.CF_max <= 1)))

def ensure_cfminmax(ds):
    if "CF_min" not in ds:
        ds = ds.assign(CF_min=cfmin)
    if "CF_max" not in ds:
        ds = ds.assign(CF_max=cfmax)
    return correct_VELOX(ds)

from multiprocessing.pool import ThreadPool

def load_cloudmask_dataset(cat_item):
    # load in parallel as this function is mainly limited by the network roundtrip time
    p = ThreadPool(20)
    return ensure_cfminmax(xr.concat(list(p.map(lambda v: v.get().to_dask().chunk(), cat_item.values())),
                                     dim="time"))
```

## Get data
We use the [eurec4a intake catalog](https://github.com/eurec4a/eurec4a-intake) to access the data files.

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog()
list(cat.HALO)
```

For each instrument, we extract the data from individual flights and concatenate them to campaign-spanning datasets for the cloud mask files.

```{code-cell} ipython3
cat_cloudmask = {
    "WALES": cat.HALO.WALES.cloudparameter,
    "HAMP Radar": cat.HALO.UNIFIED.HAMPradar_cloudmask,
    "specMACS": cat.HALO.specMACS.cloudmaskSWIR,
    "HAMP Radiometer": cat.HALO.UNIFIED.HAMPradiometer_cloudmask,
    "KT19": cat.HALO.KT19.cloudmask,
    "VELOX": cat.HALO.VELOX.cloudmask,
}
```

```{code-cell} ipython3
data = {k: load_cloudmask_dataset(v) for k, v in cat_cloudmask.items()}
```

## Case study on February 5
We show the cloud masks from the various instruments for an 5 minute time interval around noon on February 5.

We add 2D vertical lidar and radar data, as well as 2D horizontal imager data for a better visualization of the cloud information content provided by the instruments.

+++

### Data preprocessing
#### Time interval

```{code-cell} ipython3
s = slice(datetime.datetime(2020, 2, 5, 11, 22, 0),
          datetime.datetime(2020, 2, 5, 11, 27, 0))
```

#### HAMP radar reflectivities

```{code-cell} ipython3
ds_radar = cat.HALO.UNIFIED.HAMPradar["HALO-0205"].to_dask()
da_radar = ds_radar.dBZ.sel(height=slice(0, 4000), time=s)
```

#### WALES lidar backscatter ratio at 1064 nm
The WALES dataset has a `range` coordinate that can be translated into a `height` coordinate by:
\begin{equation}
height = height\_above\_sea\_level[0] - range
\end{equation}

```{code-cell} ipython3
def add_height_coordinate_wales(ds):
    ds.coords["height"] = ds.height_above_sea_level[0].values - ds.range
    return ds.swap_dims({"range": "height"})
```

```{code-cell} ipython3
ds_bsri = add_height_coordinate_wales(cat.HALO.WALES.bsri["HALO-0205"].to_dask())
da_bsri = ds_bsri.backscatter_ratio.sel(height=slice(4000, 0), time=s)
```

From WALES we also include the cloud top height information

```{code-cell} ipython3
da_cth = cat.HALO.WALES.cloudparameter["HALO-0205"].to_dask().cloud_top.sel(time=s)
```

#### SpecMACS imager radiance
From specMACS we include the radiances at 1.6 micron in the short-wave infrared (SWIR). Note: this sepcMACS radiance dataset is only available for the following application on February 5, not for the whole campaign.

```{code-cell} ipython3
url = ("https://observations.ipsl.fr/thredds/dodsC/EUREC4A/PRODUCTS/SPECMACS-CLOUDMASK/"
       + "EUREC4A_HALO_specMACS_cloud_mask_20200205T100000-20200205T182359_v1.1.nc")
ds_swir = xr.open_dataset(url, engine="netcdf4")
da_swir = ds_swir.sel(time=s).isel(radiation_wavelength=0).swir_radiance
```

#### Preprocess cloud mask data

We copy the data dictionary and apply the time selection.

+++

For the 2D horizontal imagers we select a region in the center, derive a representative `cloud_mask` flag value and use that in the following intercomparison plot.
* VELOX: we select only the cetral 10 x 10 pixels
* SpecMACS: we select the central 0.6 degrees, i.e. angle = 0 ∓ 0.3

```{code-cell} ipython3
def most_frequent_flag(var, dims):
    flags = xr.DataArray(var.flag_values, dims=("__internal__flags__"))
    flag_indices = (var == flags).sum(dims).argmax("__internal__flags__")
    return xr.DataArray(var.flag_values[flag_indices.data],
                        dims=flag_indices.dims,
                        attrs=var.attrs)

def select_specmacs_cloudmask(ds):
    specmacs = ds.sel(angle=slice(.3, -.3))
    return ds.assign({"cloud_mask": most_frequent_flag(specmacs.cloud_mask, "angle"),
                      "CF_min": cfmin(specmacs),
                      "CF_max": cfmax(specmacs)})

def select_velox_cloudmask(ds):
    xmid = ds.x.size // 2
    ymid = ds.y.size // 2
    velox = ds.isel(x=slice(xmid - 5, xmid + 5), y=slice(ymid - 5, ymid + 5))
    return ds.assign({"cloud_mask": most_frequent_flag(velox.cloud_mask, ("x", "y")),
                      "CF_min": cfmin(velox),
                      "CF_max": cfmax(velox)})

cloudmask_selectors = {
    "WALES": lambda ds: ds,
    "HAMP Radar": lambda ds: ds,
    "specMACS": select_specmacs_cloudmask,
    "HAMP Radiometer": lambda ds: ds,
    "KT19": lambda ds: ds,
    "VELOX": select_velox_cloudmask,
}
```

```{code-cell} ipython3
data0205 = {k: ensure_cfminmax(v["HALO-0205"].to_dask()) for k, v in cat_cloudmask.items()}
```

```{code-cell} ipython3
%%time
data_feb5 = {k: cloudmask_selectors[k](v.sel(time=s)) for k, v in data0205.items()}
```

### Plot

```{code-cell} ipython3
colors={
    "WALES": "darkgreen",
    "HAMP Radar": "navy",
    "specMACS": "darkred",
    "HAMP Radiometer": "palevioletred",
    "KT19": "coral",
    "VELOX": "cadetblue",
       }
```

```{code-cell} ipython3
fig, (axV, axVb, axH, axP, axL1, axL2, axL3, axL4, axL5, axL6) = plt.subplots(
    10, 1, sharex=True, figsize=(18, 10),
    gridspec_kw={"height_ratios": [3, 3, 3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}
)

## 2D vertical
# Wales backscatter ratio
im0 = da_bsri.plot.pcolormesh(
    ax=axV, x="time", y="height", norm=LogNorm(vmin=1, vmax=100),
    cmap="Spectral_r", rasterized=True, add_colorbar=False
)
cax0 = make_axes_locatable(axV).append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im0, cax=cax0, label="backscatter ratio", extend='both')
# cloud top height
da_cth.plot(ax=axV, x="time", ls="", marker=".", color="k", label="Cloud top")
axV.legend()

# Radar reflectivity
im1 = da_radar.plot(ax=axVb, x="time", add_colorbar=False)
cax1 = make_axes_locatable(axVb).append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im1, cax=cax1, label="reflectivity / dBZ")

for ax in [axV, axVb]:
    ax.set_yticks([0, 1000, 2000, 3000])
    ax.set_ylabel("height / m")

## 2D horizontal
# SpecMACS radiance
im2 = da_swir.plot.pcolormesh(ax=axH, x="time", y="angle", cmap="Greys_r",
                              vmin=0, vmax=20, rasterized=True, add_colorbar=False)
cax2 = make_axes_locatable(axH).append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im2, cax=cax2, label="SWIR radiance", extend='max')
axH.set_ylabel("view angle / deg")

## We leave an empty axis to put the legend here
[s.set_visible(False) for s in axP.spines.values()]
axP.xaxis.set_visible(False)
axP.yaxis.set_visible(False)

## 1D
# We plot 1D cloud masks
# Each we annotate with a total min and max cloud fraction for the scene shown and 
# remove disturbing spines
lines = []
plot_order = ['WALES', 'HAMP Radar', 'specMACS', 'HAMP Radiometer', 'KT19', 'VELOX']
axes = dict(zip(plot_order, [axL1, axL2, axL3, axL4, axL5, axL6]))

for k in plot_order:
    ds = data_feb5[k]
    lines += ds.cloud_mask.plot.line(ax=axes[k], x="time", label=k, color=colors[k])
    if axes[k]!=axL6:
        axes[k].spines["bottom"].set_visible(False)
        axes[k].xaxis.set_visible(False)
    axes[k].set_ylabel("")
    axes[k].annotate(f"{ds.CF_min.mean().values * 100:.1f}"
                     + f" - {ds.CF_max.mean().values * 100:.1f} %",
                     (1, 0.5), color=colors[k], xycoords="axes fraction")

# We add one legend for all 1D cloud masks
labels = [l.get_label() for l in lines]
axL1.legend(lines, labels, ncol=7, bbox_to_anchor=(0.15, 1.1))
axL3.set_ylabel("cloud flag")

for ax in [axV, axVb, axH, axP, axL1, axL2, axL3, axL4, axL5, axL6]:
    if ax!=axL6:
        ax.set_xlabel("")
    ax.set_title("")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

```{raw-cell}
fig.savefig("Cloud_masks_example_scene.png", bbox_inches="tight")
```

## Statistical comparison

We will further compare cloud mask information from all HALO flights during EUREC4A on the basis of circle flight segments. Most of the time, the HALO aircraft sampled the airmass in circles east of Barbados. We use the meta data on flight segments, extract the information on start and end time of individual circles, and derive circle-average cloud fractions.

For the 2D imagers VELOX and speMACS we use the full swath. In the case study above we had selected the central measurements for a better comparison with the other instruments. However, in the following we investigate the broad statistics and therefore include as much information on the cloud field as we can get from the full footprints of each instrument.

The following statistics are based on the **maximum cloud fraction** with cloud mask flags $\in$ {`most_likely_cloudy`, `probably_cloudy`}.

```{code-cell} ipython3
def midpoint(a, b):
    return a + (b - a) / 2

def cf_circles(ds):
    return xr.concat(
        [
            xr.Dataset({
                "CF_max": ds.sel(time=slice(i["start"], i["end"])).CF_max.mean(dim="time", skipna=True),
                "CF_min": ds.sel(time=slice(i["start"], i["end"])).CF_min.mean(dim="time", skipna=True),
                "time": xr.DataArray(midpoint(i["start"], i["end"]), dims=()),
                "segment_id": xr.DataArray(i["segment_id"], dims=())
            })
            for i in segments.values()
        ], dim="time")
```

### Get meta data

```{code-cell} ipython3
meta = eurec4a.get_flight_segments()
```

We extract all flight IDs of HALO's research flights

```{code-cell} ipython3
flight_ids = [flight_id
              for platform_id, flights in meta.items()
              if platform_id=="HALO"
              for flight_id, flight in flights.items()
              ]
```

Within each flight we further extract the circle segments

```{code-cell} ipython3
segments = {s["segment_id"]: {**s, "flight_id": flight["flight_id"]}
             for platform_id, flight_id in meta.items()
             if platform_id=="HALO"
             for flight in flight_id.values()
             for s in flight["segments"]
            if "circle" in s["kinds"]
            }
print(f"In total HALO flew {len(segments)} circles during EUREC4A")
```

### Histogram of circle mean cloud fraction

```{code-cell} ipython3
binedges = np.arange(0, 1.2, .2)
binmids = (binedges[1:] + binedges[:-1]) / 2
```

```{code-cell} ipython3
fig, (ax, ax1) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for k, v in data.items():
    ax.plot(binmids, np.histogram(cf_circles(v).CF_min.values, bins=binedges)[0],
            ls="-", lw=2, marker=".", color=colors[k], label=k)
    ax1.plot(binmids, np.histogram(cf_circles(v).CF_max.values, bins=binedges)[0],
            ls="-", lw=2, marker=".", color=colors[k], label=k)


for a in [ax, ax1]:
    a.set_xlim(0, 1)
    a.set_ylim(0, 48)
    a.spines['right'].set_visible(False)
    a.spines['top'].set_visible(False)

    a.set_xlabel("Cloud fraction")
ax.set_ylabel("Frequency")
ax1.legend(title="Instruments", bbox_to_anchor=(1,1), loc="upper left")
```

```{raw-cell}
fig.savefig("Cloud_masks_distribution.png", bbox_inches="tight")
```

### Time series of circle cloud fraction
We display the daily mean of all circle cloud fraction *(marker)* and the range from minimum to maximum circle cloud fraction *(vertical line)*.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 5))
ts = np.timedelta64(2, 'h')
for k, v in data.items():
    ds = cf_circles(v)
    ds["date"] = ds.time.astype('<M8[D]')
    date = np.unique(ds.date) + ts
    ax.errorbar(x=np.unique(ds.date) + ts,
                y=ds.groupby("date").mean().CF_min.values,
                yerr=[ds.groupby("date").min().CF_min.values,
                      ds.groupby("date").max().CF_min.values],
                fmt='o', color=colors[k], label=k)
    ts += np.timedelta64(4, 'h')
ax.set_ylim(0, 1)
ax.set_xticks(np.unique(ds.date) + np.timedelta64(12, 'h'))
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d'))
fig.autofmt_xdate()

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

ax.set_ylabel("Cloud fraction")
ax.legend(title="Instruments", bbox_to_anchor=(1,1), loc="upper left")
```

```{raw-cell}
fig.savefig("Cloud_masks_timeseries.png", bbox_inches="tight")
```

## Camapign mean cloud fraction

```{code-cell} ipython3
for k, v in data.items():
    print(f"{k}: {v.CF_max.mean().values:.2f}")
```
