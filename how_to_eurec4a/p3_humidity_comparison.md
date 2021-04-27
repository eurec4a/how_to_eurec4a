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

# Humidity comparison: Hygrometer and isotope analyzer on the P3

There are

```{code-cell} ipython3
import xarray as xr
import matplotlib.pyplot as plt
%pylab inline

import eurec4a
cat = eurec4a.get_intake_catalog()
```

Create a combined data with relative humidity from the aircraft hygrometer ("fl" means "flight level") and
the water vapor isotope analyzer ("iso"). Drop times when the aircraft is on the ground

```{code-cell} ipython3
fl = cat.P3.flight_level["P3-0119"].to_dask()
pi = cat.P3.isotope_analyzer.water_vapor_1hz["P3-0119"].to_dask()
rhs = xr.Dataset({"press" :fl["press"],
                  "alt"   :fl["alt"],
                  "rh_p3" :fl["RH"],
                  "rh_iso":pi["rh_iso"]})
rhs = rhs.where(rhs.alt > 80., drop = True)
```

Adriana Bailey from NCAR, who was responsible for the isotope analyzer, finds that while the two instruments agree most of the time,
the hygrometer is subject to both overshooting  
(e.g. when the measured signal surpasses the expected value following a rapid rise in environmental water vapor concentration) and
ringing (i.e. rapid oscillations around the expected value) during rapid and large changes in water vapor concentration. This figure
illustrates the problem and shows why you'd want to use the water vapor measurements from the isotope analyzer then they're available.

```{code-cell} ipython3
fig, (ax1, ax2) = plt.subplots(nrows=2, sharex = True, figsize = (8.3, 16.6))
#
# One time window
#
profiles = rhs.sel(time = slice(np.datetime64("2020-01-19T15:36:00"),np.datetime64("2020-01-19T16:07:40")))
marker = "."
ax1.scatter(profiles["rh_p3" ], profiles["press"],
           color=cc.glasbey[3], marker = marker, label = "Hygrometer")
ax1.scatter(profiles["rh_iso"], profiles["press"],
           color="0.5",         marker = marker, label = "Isotope analyzer")
#
# A second time window, shown as squares of roughly the same size
#
profiles = rhs.sel(time = slice(np.datetime64("2020-01-19T20:31:12"),np.datetime64("2020-01-19T20:41:16")))
marker = "s"
ax1.scatter(profiles["rh_p3" ], profiles["press"],
           color=cc.glasbey[3], marker = marker, s = .2 * plt.rcParams['lines.markersize']**2)
ax1.scatter(profiles["rh_iso"], profiles["press"],
           color="0.5",         marker = marker, s = .2 * plt.rcParams['lines.markersize']**2)


ax1.invert_yaxis()
ax1.legend(markerscale = 2)
ax1.set_xlim(0, 100)
ax1.set_ylabel("pressure (hPa)")

ax1.annotate('Ringing',     ( 5,890), fontsize="large")
ax1.annotate('Overshooting',(45,700), fontsize="large")
#
# Picarro vs. hygrometer RH - they mostly agree
#
ax2.scatter(rhs["rh_p3"],rhs["rh_iso"], s=3)
# 1:1 line
ax2.plot([0,102], [0,102], 'k-', color = 'black')
ax2.set_xlim(0, 102)
ax2.set_xlabel("Hygrometer relative humidity (%)")
ax2.set_ylabel("Picarro relative humidity (%)")

plt.tight_layout()
```
