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

# Ocean temperatures: AXBTs and SWIFT buoys

During EUREC4A/ATOMIC the P-3 deployed 165 Airborne eXpendable BathyThermographs (AXBTs)
to measure profiles of ocean temperature. (These are kind of the oceanic equivalent of
dropsondes but they don't measure salinity.) Often these were dropped around
other ocean temperature measurements - for example the autonomous
Surface Wave Instrument Floats with Tracking (SWIFT) buoys deployed from the
Ron Brown by Elizabeth Thompson of NOAA and her colleagues.

Let's take a look at some of the AXBT measurements and how they compare to the
SWIFTs.

```{code-cell} ipython3
import xarray as xr
import numpy as np
import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import colorcet as cc
%matplotlib inline

import eurec4a
cat = eurec4a.get_intake_catalog()
```
Mapping takes quite some setup. Maybe this should become part of the `eurec4a` Python module.

```{code-cell} ipython3
---
tags: [hide-cell]
---
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from   matplotlib.offsetbox import AnchoredText

import cartopy as cp
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from   cartopy.feature import LAND
from   cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from   mpl_toolkits.axes_grid1.inset_locator import inset_axes
from   mpl_toolkits.axes_grid1 import make_axes_locatable
def set_up_map(plt, lon_w = -60.5, lon_e = -49, lat_s = 10, lat_n = 16.5):
    ax  = plt.axes(projection=ccrs.PlateCarree())
    # Defining boundaries of the plot
    ax.set_extent([lon_w,lon_e,lat_s,lat_n]) # lon west, lon east, lat south, lat north
    ax.coastlines(resolution='10m',linewidth=1.5,zorder=1);
    ax.add_feature(LAND,facecolor='0.9')
    return(ax)

def ax_to_map(ax, lon_w = -60.5, lon_e = -49, lat_s = 10, lat_n = 16.5):
    # Defining boundaries of the plot
    ax.set_extent([lon_w,lon_e,lat_s,lat_n]) # lon west, lon east, lat south, lat north
    ax.coastlines(resolution='10m',linewidth=1.5,zorder=1);
    ax.add_feature(LAND,facecolor='0.9')

def add_gridlines(ax):
    # Assigning axes ticks
    xticks = np.arange(-65,0,2.5)
    yticks = np.arange(0,25,2.5)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=1, color='black', alpha=0.5, linestyle='dotted')
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10, 'color': 'k'}
    gl.ylabel_style = {'size': 10, 'color': 'k'}
    gl.right_labels = False
    gl.bottom_labels = False
    gl.xlabel = {'Latitude'}
```
Now set up colors to code each flight date during the experiment. One could choose
a categorical palette so the colors were as different from each other as possible.
Here we'll choose from a continuous set that spans the experiment so days that are
close in time are also close in color.

```{code-cell} ipython3
---
tags: [hide-cell]
---
# On what days did the P-3 fly? These are UTC.
flight_dates = [datetime.date(2020, 1, 17),
                datetime.date(2020, 1, 19),
                datetime.date(2020, 1, 23),
                datetime.date(2020, 1, 24),
                datetime.date(2020, 1, 31),
                datetime.date(2020, 2,  3),
                datetime.date(2020, 2,  4),
                datetime.date(2020, 2,  5),
                datetime.date(2020, 2,  9),
                datetime.date(2020, 2, 10),
                datetime.date(2020, 2, 11)]

# color map for things coded by flight date
#   Sample from a 255 color map running from start to end of experiment
norm = mpl.colors.Normalize(vmin=datetime.date(2020, 1, 15).toordinal(),
                            vmax=datetime.date(2020, 2, 15).toordinal())
flight_cols = [cc.m_bmy(norm(d.toordinal()), alpha=0.9) for d in flight_dates]  
flight_cols = [mpl.cm.viridis(norm(d.toordinal()), alpha=0.9) for d in flight_dates]  
```
The P-3 only deployed AXBTs on some flights, and the SWIFT buoys were only deployed
on a subset of those dates.

```{code-cell} ipython3
axbts = cat.P3.AXBT.Level_3.to_dask()
axbt_dates = [d for d in flight_dates if d.strftime("%Y-%m-%d") in np.datetime_as_string(axbts.time, unit="D")]

swifts = [cat[s].all.to_dask() for s in list(cat) if "SWIFT" in s]
#
# Dates with potential SWIFT/P-3 overlap
#
swift_dates = [d for d in
               [datetime.date(2020, 1, 19),
               datetime.date(2020, 1, 31),
               datetime.date(2020, 2,  3),
               datetime.date(2020, 2,  4),
               datetime.date(2020, 2,  5),
               datetime.date(2020, 2,  9),
               datetime.date(2020, 2, 10)]
               if d in axbt_dates]
```
Now we can make a map that shows where the AXBTs were deployed and where the SWIFTs
were on days there the two platforms overlapped

```{code-cell} ipython3
fig = plt.figure(figsize = (8.3, 9.4))
ax  = set_up_map(plt)
add_gridlines(ax)

#
# AXBT locations
#
for d in axbt_dates:
    flight = axbts.sel(time=d.strftime("%Y-%m-%d"))
    ax.scatter(flight.lon,flight.lat,
               alpha=0.5,color=flight_cols[flight_dates.index(d)],
               transform=ccrs.PlateCarree(),zorder=7,
               label="{:02d}-{:02d}".format(d.month, d.day))
#
# SWIFT locations on selected dates (where there's overlap)
#
for d in swift_dates:
    flight = axbts.sel(time=d.strftime("%Y-%m-%d"))
    for swift in swifts:
        drift = swift.sel(time = flight.time.mean(), method = "nearest")
        ax.scatter(drift.lon,drift.lat,
                   alpha=1,color=flight_cols[flight_dates.index(d)],
                   transform=ccrs.PlateCarree(),zorder=7, marker = "p")

plt.legend(ncol=2,loc=(0.0,0.0),fontsize=12,framealpha=0.8,markerscale=1, title="Flight date (MM-DD-2020)")
plt.tight_layout()
```
On 19 Jan and 3 Feb the AXBTs bracket the SWIFTs; on 23 Jan the SWIFTs are at
the southern end of the AXBT pattern.

The next plot will focus on 19 Jan.
Let's look at the profile of ocean temperature in the first 150 m from the AXBTs
and compare the near-surface temperatures to the SWIFTs they are surrounding.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=[8.3, 9.4])
axbt_1day   = axbts.sel(time="2020-01-19")
# Swift data at mean of AXBT times
swifts_1day = [s.sel(time = axbt_1day.time.mean(), method = "nearest") for s in swifts]

axbt_1day.temperature.where(axbt_1day.depth < 150).plot.line(y="depth",
                                                             add_legend=False, yincrease=False)
ax.set_xlabel("Sea water temperature (K)")
ax.set_ylabel("Depth (m)")
sns.despine()

#
# Inset plot! https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/zoom_inset_axes.html
#
axin = ax.inset_axes([0.06, 0.84, 0.6, 0.12])
axin.scatter([s.sea_water_temperature.values + 273.15 for s in swifts_1day],
             # SWIFTs 16 and 17 report water temperature at 0.5 m depth; SWIFTs 23-25 report at 0.3 m
             # See the variable long_name or  Tables 8 and 9 of Quinn et al.
             [0.5 if '0.5' in s.sea_water_temperature.long_name else 0.3 for s in swifts_1day],
             color="0.25",
             s = 1.5 * plt.rcParams['lines.markersize'] ** 2)
axbt_1day.temperature.where(axbt_1day.depth < 3).plot.line(y="depth",
                                                           add_legend=False, yincrease=False, ax = axin)
axin.set_xlabel("Sea water temperature (K)")
axin.set_ylabel("Depth (m)")
sns.despine(ax=axin)
ax.indicate_inset_zoom(axin)

plt.tight_layout()
```
