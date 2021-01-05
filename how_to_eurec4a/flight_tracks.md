---
jupytext:
  formats: md:myst
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

# Show flight tracks of the HALO aircraft

This notebook shows how to plot the flight tracks of the HALO aircraft.

First, we'll import pylab and the EUREC4A data catalog.

```{code-cell} ipython3
%pylab inline
import eurec4a
cat = eurec4a.get_intake_catalog()
```

## Preparations
When inspecting the contents of the currently available BAHAMAS quicklook dataset, we see that it does not handle coordinates according to the ideas of [CF conventions](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html), which makes using the data a lot more difficult.

```{code-cell} ipython3
ds = cat.HALO.BAHAMAS.QL['HALO-0122'].to_dask()
ds
```

In order to fix that a bit, we could come up with a little function which transforms the dataset we get into a dataset we would like to have. Of course the proper way of handling this would be to actually fix the dataset, but this way of doing it may still be illustrative.

```{code-cell} ipython3
def fix_halo_ql(ds):
    import xarray as xr
    ds = ds.rename({"tid":"time"})
    ds["time"] = ds.TIME
    ds["lat"] = ds.IRS_LAT
    ds["lon"] = ds.IRS_LON
    ds["alt"] = ds.IRS_ALT
    del ds["TIME"]
    return ds
```

This at least has a `time` coordinate.

```{code-cell} ipython3
fix_halo_ql(ds)
```

We'll use this fix subsequently to prepare all retrieved datasets.

## Actual ploting

In order to plot things properly on a map, we can use the `cartopy` library.

```{code-cell} ipython3
import cartopy
import cartopy.crs as ccrs
```

First, we'll have a look at the first three flights. We could also display all of them, but that would likely become too crowded quickly. Feel free to change the selected flights.

```{code-cell} ipython3
fig = plt.figure(figsize=(15,8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-60, -52, 12, 15], crs=ccrs.PlateCarree())
ax.coastlines()
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

for flight_id, ds in list(cat.HALO.BAHAMAS.QL.items())[:3]:
    ds = fix_halo_ql(ds.get().to_dask())
    plt.plot(ds.lon, ds.lat, transform=ccrs.Geodetic(), label=flight_id)
plt.legend()
plt.show()
```

Another way to look at the flights would be a timeline of flight altitude. But in order to put all flights into a single plot, it is useful to define an additional coordinate which contains hours since midnight in stead of the absolute time. We'll do this with a little helper function:

```{code-cell} ipython3
def hours_since_first_midnight(time_variable):
    # by reducing the precision to one day, we can pick out midnight of the first time stamp
    first_midnight = time_variable[0].astype("datetime64[D]")
    hour = np.timedelta64(60 * 60, "s")
    return (time_variable - first_midnight) / hour
```

```{code-cell} ipython3
fig = plt.figure(figsize=(15,5))
for flight_id, ds in cat.HALO.BAHAMAS.QL.items():
    ds = fix_halo_ql(ds.get().to_dask())
    ds.time.load()
    ds.alt.load()
    ds.coords["hours_since_midnight"] = hours_since_first_midnight(ds.time)
    ds.alt.plot(x="hours_since_midnight", label=flight_id)
plt.xlabel("hours since midnight")
plt.legend(loc=1)
plt.show()
```
