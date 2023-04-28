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
execution:
  timeout: 600
---

# Cloud masks

Different instruments, by virtue of their differing measurement principle and footprint, see clouds in different ways. To provide an overview of the cloud fields sampled by HALO during EUREC⁴A, a cloud mask is created for each cloud sensitive instrument.  
In the following, we compare the different cloud mask products for a case study on 5 February and further provide a statistical overview for the full campaign period.

More information on the dataset can be found in Konow et al. (in preparation). If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

```{code-cell} ipython3
import eurec4a
import numpy as np
import xarray as xr
import matplotlib as mpl

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm
```

We generally don't support ignoring warnings, however, we do so in this notebook to suppress warnings originating from zero division. Unfortunately, we coudn't find another way to handle the warnings. If you have an idea, please make a pull request and change it :)

```{code-cell} ipython3
import warnings
warnings.filterwarnings("ignore")
```

## Cloud cover functions
We define some utility functions to extract (circle) cloud cover estimates from different datasets assuming that the datasets follow a certain flag meaning convention.  

In particular, we define a **minimum cloud cover** based on the cloud mask flag `most_likely_cloudy` and a **maximum cloud cover** combining the flags `most_likely_cloudy` and `probably_cloudy`. The cloud mask datasets slightly vary in their flag definition for cloud free conditions and their handling of unvalid measurements which is taken care of by the following functions.

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
    ds.CF_min.load()
    ds.CF_max.load()
    return correct_VELOX(ds)

from multiprocessing.pool import ThreadPool

def load_cloudmask_dataset(cat_item):
    # load in parallel as this function is mainly limited by the network roundtrip time
    p = ThreadPool(20)
    return ensure_cfminmax(xr.concat(list(p.map(lambda v: v.get().to_dask().chunk(),
                                                cat_item.values())),
                                     dim="time",
                                     data_vars="minimal"))
```

## Get data
We use the [eurec4a intake catalog](https://github.com/eurec4a/eurec4a-intake) to access the data files.

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog(use_ipfs="QmahMN2wgPauHYkkiTGoG2TpPBmj3p5FoYJAq9uE9iXT9N")
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

We have a look at the time periods spanned by the individual datasets: The datasets `HAMP Radar`, `HAMP Radiometer`, and `specMACS` include measurements from the transfer flights on 19 January to Barbados and on 18 February back over the Atlantic to Europe. The datasets `WALES`, `KT19`, and `VELOX` are limited to the 13 local research flights between 22 January and 15 February.

```{code-cell} ipython3
for k, v in data.items():
    print(f"{k}: {v.isel(time=0).time.values} -  {v.isel(time=-1).time.values}")
```

## Case study on February 5
We show the cloud masks from the various instruments for an 5 minute time interval around noon on February 5.

We add 2D vertical lidar and radar data, as well as 2D horizontal imager data for a better visualization of the cloud information content provided by the instruments.

+++

### Data preprocessing
#### Time interval

```{code-cell} ipython3
s = slice("2020-02-05T11:22:00", "2020-02-05T11:27:00")
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
From specMACS we include the radiances at 1.6 micron in the short-wave infrared (SWIR).  

```{note}
this dataset is only available for the following application on February 5, not for the whole campaign.
```

```{code-cell} ipython3
ds_swir = xr.open_zarr("ipfs://QmZUNCXKvKSeugVHFUsgzDnTrrPHomc5ikEhjoYH2hRq4N")
da_swir = ds_swir.sel(time=s).isel(radiation_wavelength=0).swir_radiance
```

#### VELOX broadband IR brightness temperature
Next to the SpecMACS SWIR radiance, we include broadband brightness temperatures from VELOX (7.7 - 12 μm).

```{note}
this dataset is only available for the following application on February 5, not for the whole campaign.
```

```{code-cell} ipython3
ds_bt = xr.open_zarr("ipfs://QmQEwkhhHdJkiThf4hnj9G3wgqVreBnWGrX2A5kT6CrtY7",
                     consolidated=True,
                    ).assign_coords(va=lambda x: x.va)
```

#### Preprocess cloud mask data

We copy the data dictionary and apply the time selection.

+++

For the 2D horizontal imagers we select a region in the center, derive a representative (most frequent) `cloud_mask` flag value and use that in the following intercomparison plot.
* VELOX: we select only the central 11 x 11 pixels, i.e. view angle = 0 ∓ 0.2865 (see below)
* SpecMACS: we select the central 0.6 degrees, i.e. angle = 0 ∓ 0.3

What is the angle of the 11 central pixel in accross track direction for VELOX?

```{code-cell} ipython3
xmid = ds_bt.x.size // 2
va_central = ds_bt.isel(time=0, x=slice(xmid - 5, xmid + 6)).va
(va_central.max() - va_central.min()).values
```

```{code-cell} ipython3
def most_frequent_flag(var, dims):
    flag_values = np.asarray(var.flag_values)
    flags = xr.DataArray(flag_values, dims=("__internal__flags__"))
    flag_indices = (var == flags).sum(dims).argmax("__internal__flags__")
    return xr.DataArray(flag_values[flag_indices.data],
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
    velox = ds.isel(x=slice(xmid - 5, xmid + 6), y=slice(ymid - 5, ymid + 6))
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
%matplotlib inline
import matplotlib.pyplot as plt
import pathlib
plt.style.use(pathlib.Path("./mplstyle/book"))
```

```{code-cell} ipython3
with plt.style.context("mplstyle/square"):
    fig, (ax0, ax1, ax2, ax3, axLegend, axL1, axL2, axL3, axL4, axL5, axL6) = plt.subplots(
        11, 1, sharex=True, gridspec_kw={"height_ratios": [3, 3, 3, 3, 0.5, 0.5, 0.5,
                                                           0.5, 0.5, 0.5, 0.5]}
    )

    ## 2D vertical
    # Wales backscatter ratio
    im0 = da_bsri.plot.pcolormesh(
        ax=ax0, x="time", y="height", norm=LogNorm(vmin=1, vmax=100),
        cmap="Spectral_r", rasterized=True, add_colorbar=False
    )
    cax0 = make_axes_locatable(ax0).append_axes("right", size="1%", pad=-0.05)
    fig.colorbar(im0, cax=cax0, label="backscatter ratio", extend='both')
    # cloud top height
    da_cth.plot(ax=ax0, x="time", ls="", marker=".", color="k", label="Cloud top")
    ax0.legend()

    # Radar reflectivity
    im1 = da_radar.plot(ax=ax1, x="time", rasterized=True, add_colorbar=False)
    cax1 = make_axes_locatable(ax1).append_axes("right", size="1%", pad=-0.05)
    fig.colorbar(im1, cax=cax1, label="reflectivity / dBZ")

    for ax in [ax0, ax1]:
        ax.set_yticks([0, 1000, 2000, 3000])
        ax.set_ylabel("height / m")

    ## 2D horizontal
    # SpecMACS radiance
    im2 = da_swir.plot.pcolormesh(ax=ax2, x="time", y="angle", cmap="Greys_r",
                                  vmin=0, vmax=20, rasterized=True, add_colorbar=False)
    cax2 = make_axes_locatable(ax2).append_axes("right", size="1%", pad=-0.05)
    fig.colorbar(im2, cax=cax2, label="SWIR radiance", extend='max')
    ax2.set_ylabel("view angle / deg")

    # VELOX brightness temperature
    im3 = (ds_bt.Brightness_temperature - 273.15).plot.pcolormesh(ax=ax3, x="time", y="va",
            cmap="RdYlBu_r", rasterized=True, add_colorbar=False)
    cax3 = make_axes_locatable(ax3).append_axes("right", size="1%", pad=-0.05)
    fig.colorbar(im3, cax=cax3, label="Brightness\ntemperature / °C")
    ax3.set_ylabel("view angle / deg")


    ## We leave an empty axis to put the legend here
    [s.set_visible(False) for s in axLegend.spines.values()]
    axLegend.xaxis.set_visible(False)
    axLegend.yaxis.set_visible(False)

    ## 1D
    # We plot 1D cloud masks
    # Each we annotate with a total min and max cloud cover for the scene shown and
    # remove disturbing spines
    lines = []
    plot_order = ['WALES', 'HAMP Radar', 'specMACS', 'VELOX', 'KT19', 'HAMP Radiometer']
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
    axL1.legend(lines, labels, ncol=7, bbox_to_anchor=(0.01, 1.5))
    axL3.set_ylabel("cloud flag")

    for ax in [ax0, ax1, ax2, ax3, axLegend, axL1, axL2, axL3, axL4, axL5, axL6]:
        ax.set_xlabel("")
        ax.set_title("")

    axL6.set_xlabel("UTC time")
    axL6.set_xticks(np.arange(np.datetime64('2020-02-05T11:22:00'),
                    np.datetime64('2020-02-05T11:28:00'), np.timedelta64(1, 'm')))
    ax0.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    fig.align_ylabels(axs=[ax0, ax1, ax2, ax3, axL3])
    #fig.align_ylabels(axs=[cax0, cax1, cax2])

    label_pos_x = np.datetime64('2020-02-05T11:21:35')
    for ax, label in zip([ax0, ax1, ax2, ax3, axL1], ["(a)", "(b)", "(c)", "(d)", "(e)"]):
        ax.text(label_pos_x, ax.get_ylim()[1], label, verticalalignment='bottom')
```

