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

# Cloudmasks

Different instruments, by virtue of their differing measurement principle and footprint, see clouds in different ways. To provide an overview of the cloud fields sampled by HALO during EUREC4A, a cloud mask is created for each cloud sensitive instrument. 

More information on the dataset can be found in .... If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` or `author`.

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
list(cat.HALO.VELOX)
```

* We can further specify the platform, instrument, if applicable dataset level or variable name, and pass it on to dask.

*Note: have a look at the attributes of the xarray dataset `ds` for all relevant information on the dataset, such as author, contact, or citation infromation.*

```{code-cell} ipython3
kt19 = cat.HALO.KT19.cloudmask["HALO-0205"].to_dask()
specMACS = cat.HALO.specMACS.cloudmaskSWIR["HALO-0205"].to_dask()
Velox = cat.HALO.VELOX.cloudmask["HALO-0205"].to_dask()
HAMPradar = cat.HALO.UNIFIED.HAMPradar["HALO-0205"].to_dask()
HAMPradar_cloudmask = cat.HALO.UNIFIED.HAMPradar_cloudmask["HALO-0205"].to_dask()
HAMPradiometer = cat.HALO.UNIFIED.HAMPradiometer_cloudmask["HALO-0205"].to_dask()
```

The measurements are identified in the cloudmask as either: `cloud free`, `probably cloudy` or `most likely cloudy`. 

+++

### Wales Lidar

```{code-cell} ipython3
list(cat.HALO.WALES)
```

#### Backscatter ratios
The backscatter ratios `bsrg` and `bsri` for flight on the 5th of February 2020, `HALO-0205`

+++

Next, we translate the `range` coordinate to a `height` coordinate. The data is already corrected for the aircraft motion (`instrument_elevantion_angle` is constant at 90 degree, looking down), interpolated to a regular height grid and saved relative to a constant height declaration stated in the variable `height_above_sea_level`. We therefore get a `height` coordinate by:
\begin{equation}
height = height\_above\_sea\_level[0] - range
\end{equation}

```{code-cell} ipython3
def add_height_coordinate(ds):
    ds.coords["height"] = ds.height_above_sea_level[0].values - ds.range
    return ds
```

```{code-cell} ipython3
ds_bsrg = add_height_coordinate(cat.HALO.WALES.bsrg["HALO-0205"].to_dask().load())
ds_bsri = add_height_coordinate(cat.HALO.WALES.bsri["HALO-0205"].to_dask().load())
```

#### Cloud top height

```{code-cell} ipython3
ds_cloud = cat.HALO.WALES.cloudparameter["HALO-0205"].to_dask().load()
```

## Plots

```{code-cell} ipython3
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm
```

We choose an example time interval

```{code-cell} ipython3
s = slice(datetime.datetime(2020, 2, 5, 11, 22, 0), datetime.datetime(2020, 2, 5, 11, 27, 0))
```

```{code-cell} ipython3
fig, (axV, axVb, axH, axP, axL1, axL2, axL3, axL4, axL5, axLE) = plt.subplots(10,1,sharex=True,figsize=(18, 10),
                                                                              gridspec_kw={"height_ratios": [3, 3, 3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]})

## 2D vertical
# backscatter ratio from Wales
im = ds_bsri.backscatter_ratio.sel(time=s).plot.pcolormesh(ax=axV,x="time",y="height",
                                               norm=LogNorm(vmin=1, vmax=100),cmap="Spectral_r",
                                               rasterized=True,add_colorbar=False)
divider = make_axes_locatable(axV)
cax = divider.append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im, cax=cax, label="backscatter ratio", extend='both')
# cloud top height
ds_cloud.cloud_top.sel(time=s).plot(ax=axV, x="time", ls="", marker=".", 
                        color="k", label="WALES cloud top")

axV.set_ylim(0, 4000)
axV.set_ylabel("height / m")
axV.legend()


# Radar reflectivity
im = HAMPradar.dBZ.sel(height=slice(0, 4000),time=s).plot(ax=axVb, x="time", add_colorbar=False)
divider = make_axes_locatable(axVb)
cax = divider.append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im, cax=cax, label="dBZ")
axVb.set_ylabel("height / m")

## 2D horizontal
# SpecMACS radiance
im = specMACS.swir_radiance.sel(time=s).squeeze(drop=True).plot.pcolormesh(ax=axH,x="time",y="angle",
                                                               cmap="Greys_r",vmin=0,vmax=20,
                                                               rasterized=True,add_colorbar=False)
divider = make_axes_locatable(axH)
cax = divider.append_axes("right", size="1%", pad=-0.05)
fig.colorbar(im, cax=cax, label="SWIR radiance", extend='max')
axH.set_ylabel("view angle /deg")


## We leave an empty axis to put the legend here
[s.set_visible(False) for s in axP.spines.values()]
axP.xaxis.set_visible(False)
axP.yaxis.set_visible(False)

## 1D
# We plot 1D cloud masks
# Each we annotate with a total min and max cloud fraction for the scene shown and remove disturbing spines

# For SpecMACS we select the cloudmaks near angle 0, thus the nadir pixels
specMACS0 = specMACS.sel(angle=0, method="nearest")

# For Velox we selcet the max cloud flag in the central 10x10 pixels
Velox10x10=Velox.isel(x=slice(int(Velox.cloud_mask.x.size/2-10), int(Velox.cloud_mask.x.size/2+10)), y=slice(int(Velox.cloud_mask.y.size/2-10), int(Velox.cloud_mask.y.size/2+10)))
Velox10x10['cloud_mask']=Velox10x10.cloud_mask.max(dim=('x', 'y'))
Velox10x10['cloud_mask'].attrs=Velox.cloud_mask.attrs

lines = []

for ax, ds, l, c in zip(
    [axL1, axL2, axL3, axL4, axL5, axLE],
    [ds_cloud, HAMPradar_cloudmask, specMACS0, kt19, HAMPradiometer, Velox10x10],
    ["Wales", "HAMP Radar", "SpecMACS", "KT19", "HAMP Radiometer","Velox"],
    ["darkgreen", "navy", "darkred", "coral", "palevioletred", "cadetblue"],
):
    lines += ds.cloud_mask.sel(time=s).plot.line(ax=ax, x="time", label=l, color=c)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_ylabel("")
    ax.set_title("")
    meanings = dict(zip(ds.cloud_mask.sel(time=s).flag_meanings.split(" "), ds.cloud_mask.flag_values))
    min=100*(ds.cloud_mask==meanings["most_likely_cloudy"]).sum().values / len(ds.cloud_mask)
    max=100*((ds.cloud_mask==meanings["most_likely_cloudy"]).sum().values + (ds.cloud_mask==meanings["probably_cloudy"]).sum().values)/ len(ds.cloud_mask)
    ax.annotate(f"{min:.1f} - {max:.1f} %",
                (1, 0.5),xycoords="axes fraction")


# We add one legend for all 1D cloud masks
labels = [l.get_label() for l in lines]
axL1.legend(lines, labels, ncol=7, bbox_to_anchor=(0.45, 1.1))
axL3.set_ylabel("cloud flag")

for ax in [axV, axVb, axH, axP, axL1, axL2, axL3, axL4, axL5]:
    ax.set_xlabel("")
    
axLE.spines["bottom"].set_visible(True)
axLE.xaxis.set_visible(True)

fig.savefig("Cloud_masks_example_scene.pdf", bbox_inches='tight')
```
