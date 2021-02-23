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

# HAMP comparison


```{code-cell} ipython3
import xarray
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
import glob

import eurec4a

#from wgs64_geoid import wgs84_height
#import MagnifyLinearScale

cat = eurec4a.get_intake_catalog()
```

We'll define a helper-function to approximately convert cell centers to edges:
```{code-cell} ipython3
---
tags: [hide-cell]
---
def center_to_edge(center):
    center = np.asarray(center)
    edge =  np.empty(center.shape[0]+1, dtype=center.dtype)
    # the strange notation in the following lines is used to make the calculations datetime compatible
    edge[1:-1] = center[1:] + (center[:-1] - center[1:])/2.
    edge[0] = edge[1] + (edge[1] - edge[2])
    edge[-1] = edge[-2] + (edge[-2] - edge[-3])
    return edge
```

## Collect datasets
We want to look at data from several sensors within a spacific timeframe on flight `HALO-0205`:

```{code-cell} ipython3
flight_id = 'HALO-0205'
timeslice = slice('2020-02-05T13:07', '2020-02-05T13:11')

#radar_cm = xarray.open_dataset(f'./out/netcdf/EUREC4A_HALO_HAMP-Radar_cloud_mask_{date}_v{cloud_mask_version}.nc').sel(time=timeslice)
#radiometer_cm = xarray.open_dataset(f'./out/netcdf/EUREC4A_HALO_HAMP-MWR_cloud_mask_{date}_v{cloud_mask_version}.nc').sel(time=timeslice)
#retrieval_file = glob.glob(f'{retrieval_data_dir}/EUREC4A_HALO_HAMP_lwpiwv_l2_any_v0.8_{date}[0-9][0-9][0-9][0-9][0-9][0-9].nc')[0]
#retrieval = xarray.open_dataset(retrieval_file).sel(time=timeslice)

radar = cat.HALO.UNIFIED.HAMPradar[flight_id].to_dask().sel(time=timeslice)
wales = cat.HALO.WALES.cloudparameter[flight_id].to_dask().sel(time=timeslice)
specMACS = cat.HALO.specMACS.cloudmaskSWIR[flight_id].to_dask().sel(time=timeslice)
```

Ideally, we'd be handling the cloud flag meanings properly, but for now, let's just check if they are defined exactly as we expect them to be:

```{code-cell} ipython3
#assert np.all(radar_cm.cloud_mask.flag_values == radiometer_cm.cloud_mask.flag_values)
#assert np.all(radar_cm.cloud_mask.flag_values == wales.cloud_mask.flag_values)
#assert radar_cm.cloud_mask.flag_meanings == 'unknown no_cloud_detectable probably_cloudy most_likely_cloudy'
#assert radiometer_cm.cloud_mask.flag_meanings == 'unknown no_cloud_detectable probably_cloudy most_likely_cloudy'
assert wales.cloud_mask.flag_meanings == 'unknown cloud_free probably_cloudy most_likely_cloudy'
```


## Plot timeseries
```{code-cell} ipython3
fig, (ax3, ax2, ax1, ax,) = plt.subplots(
    nrows=4, figsize=(10, 8), sharex=True,
    gridspec_kw=dict(height_ratios=[1, 1, .75, 0.5]),
    constrained_layout=True
)

ax.plot(wales.time, wales.cloud_mask + 0.2, '.', label='WALES', markersize=3)
#ax.plot(radar_cm.time, radar_cm.cloud_mask, '.', label='Radar')
#ax.plot(radiometer_cm.time, radiometer_cm.cloud_mask + 0.1, '.', label='Radiometer')

# Make nice labels
#ax.set_yticks(radar_cm.cloud_mask.flag_values)
#ax.set_yticklabels(radar_cm.cloud_mask.flag_meanings.split())
ax.legend(ncol=3, loc='lower right')
ax.grid()

# Plot Radar Curtain
ax2.set_title('HAMP Cloud Radar')
dBZ = radar.dBZ.transpose('height', 'time').values
x = center_to_edge(radar.time)
y = center_to_edge(radar.height)
ax2.pcolormesh(x, y, dBZ, vmin=-30, vmax=35, cmap='gray', rasterized=True)

ax2.plot(
     wales.time,  wales.cloud_top, # + wgs84_height(wales.lon, wales.lat),
    '.', markersize=3,
    label='WALES cloud top'
)
#ax2.plot(
#    radar_cm.time, radar_cm.cloud_top + wgs84_height(radar_cm.lon, radar_cm.lat),
#    '.', markersize=3,
#    label='Radar Cloud top'
#)
ax2.set_ylabel('Height above WGS84 (m)') # if geoid is enabled, this will be Height above geoid
ax2.set_ylim(0, 2500)
ax2.grid()
ax2.legend(ncol=3)
ax2.minorticks_on()

# specMACS
specMACS.cloud_mask.T.plot.contour(ax=ax3, cmap="gray", add_colorbar=False)
ax3.set_title('specMACS')

# Plot MWR Retrievals
ax1.set_title('HAMP Microwave Radiometer')
#ax1.plot(retrieval.time, retrieval.lwp*1000, label='Total Liquid Water Path')
#ax1.plot(retrieval.time, retrieval.rwp*1000, label='Rain Water Path')
ax1.set_ylim(-10, 911)

ax1.axhline(20, color='k', linewidth=1, linestyle=':', zorder=0)
#ax1.set_yscale('magnifylinear', magnify_segments=[[-20., 20., 10.]])
ax1.set_yticks([-20, 0, 20, 300, 600, 900])
ax1.set_ylabel('Condensate (g/m²)')

#ax.set_xlim(np.datetime64(start), np.datetime64(end))
None
```
