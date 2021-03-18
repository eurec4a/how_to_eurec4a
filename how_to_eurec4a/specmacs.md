---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.9.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# specMACS cloudmask

The following script exemplifies the access and usage of specMACS data measured 
during EUREC4A.  

More information on the dataset can be found at https://macsserver.physik.uni-muenchen.de/campaigns/EUREC4A/products/cloudmask/. If you have questions or if you would like to use the data for a publication, please don't hesitate to get in contact with the dataset authors as stated in the dataset attributes `contact` and `author` list.

```{code-cell} ipython3
%pylab inline
```

## Get data
To load the data we first load the EUREC4A meta data catalogue. More information on the catalog can be found [here](https://github.com/eurec4a/eurec4a-intake#eurec4a-intake-catalogue).

```{code-cell} ipython3
import eurec4a
import xarray as xr
import numpy as np
import dask.array as da
import cartopy.crs as ccrs
from matplotlib import pyplot as plt
```

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog()
```

```{code-cell} ipython3
ds = xr.open_dataset("/project/meteo/work/Veronika.Poertge/PhD/specMACS/products_essd_paper/cloudmask/EUREC4A_HALO_specMACS-SWIR_cloudmask_20200205_v2.1.nc")
```

We can further specify the platform, instrument, if applicable dataset level or variable name, and pass it on to dask.

*Note: have a look at the attributes of the xarray dataset `ds` for all relevant information on the dataset, such as author, contact, or citation infromation.*

+++

## Load HALO flight phase information
All HALO flights were split up into flight phases or segments to allow for a precise selection in time and space of a circle or calibration pattern. For more information have a look at the respective [github repository](https://github.com/eurec4a/halo-flight-phase-separation).

```{code-cell} ipython3
meta = eurec4a.get_flight_segments()
```

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

We want to extract the id of the first dropsonde of the second HALO circle on February 5 (HALO-0205_c2). By the way: In the [VELOX example](https://eurec4a.pages.gwdg.de/how_to_eurec4a/velox.html) the measurement of this time is shown as well.

```{code-cell} ipython3
segments_by_segment_id = {s["segment_id"]: s for s in segments}
first_dropsonde = segments_by_segment_id["HALO-0205_c2"]["dropsondes"]["GOOD"][0]
first_dropsonde
```

Now we would like to know when this sonde was launched. The JOANNE dataset contains this information. We load it using the intake catalog. We then select the correct dropsonde by its sonde_id to find out the launch time of the dropsonde.

```{code-cell} ipython3
dropsondes = cat.dropsondes.JOANNE.level3.to_dask().load()
sonde_dt = dropsondes.swap_dims({"sounding": "sonde_id"}).sel(sonde_id=first_dropsonde).launch_time.values
sonde_dt
```

We transfer the information from our flight segment selection to the specMACS data in the xarray dataset and select a two minute long measurement sequence of specMACS data around the dropsonde launch.

```{code-cell} ipython3
ds_selection = ds.sel(time=slice(sonde_dt-np.timedelta64(60, "s"), sonde_dt+np.timedelta64(60, "s")))
ds_selection
```

## Plots
Figure 1: shows the SWIR camera cloud mask product along the flight track (x axis) for all observations in accross track directions (y axis).  

You can get a list of available variables in the dataset from `ds_selection.variables.keys()`  
*Note: fetching the data and displaying it might take a few seconds*

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(16,4))
cax = ds_selection.cloud_mask.T.plot(ax=ax,
                                     cmap=plt.get_cmap('Greys_r', lut=3),
                                     vmin=-0.5, vmax=2.5,
                                     add_colorbar=False)
cbar = fig.colorbar(cax, ticks=ds_selection.cloud_mask.flag_values)
cbar.ax.set_yticklabels(ds_selection.cloud_mask.flag_meanings.split(" "));
start_time_rounded = np.array(ds_selection.time.isel(time=0).values, dtype='datetime64[s]')
end_time_rounded = np.array(ds_selection.time.isel(time=-1).values, dtype='datetime64[s]')
ax.set_title("specMACS cloud mask ({} - {})".format(start_time_rounded, end_time_rounded));
```

The dataset also contains the minimal and maximal cloud fractions which are calculated for each temporal measurement. The minimal cloud fraction is derived from the ratio between the number of pixels classified as "most likely cloudy" and the total number of pixels in one measurement. The maximal cloud fraction additionally includes the number of pixels classified as "probably cloudy".

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 4))
ds_selection.CF_max.plot(color="lightgrey",label="maximal cloud_fraction:\nmost likely cloudy and probably cloudy")
ds_selection.CF_min.plot(color="grey", label="minimal cloud fraction:\nmost_likely_cloudy")
ax.axvline(sonde_dt, color="C3", label="sonde launch time")
ax.set_ylim(0, 1)
ax.set_ylabel("Cloud fraction")
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_title("Second circle on February 5")
ax.legend(bbox_to_anchor=(1,1), loc="upper left")
```

## Conversion from camera view angles to latitude and longitude

+++

The cloud mask is given on a `time x angle` grid where `angles` are the internal camera angles. Sometimes it could be helpful to project the data onto a map. This means that we would like to know the corresponding **latitude** and **longitude** coordinates of the cloud mask.
We need five variables for this:
* position of the airplane: latitude, longitude and altitude (`ds.lat, ds.lon, ds.alt`)
* viewing directions of the camera pixels: viewing zenith angle and viewing azimuth angle (`ds.vza, ds.vaa`)

Let's have a look a these variables

```{code-cell} ipython3
for key in ["lat", "lon", "alt", "vza", "vaa"]:
    print(key, ds_selection[key].attrs)
```

* The position of the HALO is saved in ellipsoidal coordinates. It is defined by the lat/lon/height coordinates with respect to the WGS-84 ellipsoid.
* The viewing zenith and azimuth angles are given with respect to the local horizon (lh) coordinate system at the position of the HALO. This system has its center at the lat/lon/height position of the HALO and the x/y/z axis point into North, East and down directions.

A convenient way to work with such kind of data is to transform it into the Earth-Centered, Earth-Fixed (ECEF) coordinate system. The origin of this coordinate system is the center of the Earth. The z-axis passes through true north, the x-axis through the Equator and the prime meridian at 0° longitude. The y-axis is orthogonal to x and z. This cartesian system makes computations of distances and angles very easy. 

In a first step we want to transform the position of the HALO into the ECEF coordinate system. We use the method presented here: https://gssc.esa.int/navipedia/index.php/Ellipsoidal_and_Cartesian_Coordinates_Conversion

```{code-cell} ipython3
def ellipsoidal_to_ecef(lat, lon, height):
    '''Transform ellipsoidal coordinates into the ECEF coordinate system according to:
    https://gssc.esa.int/navipedia/index.php/Ellipsoidal_and_Cartesian_Coordinates_Conversion

    Parameters:
    lat: latitude of ellipsoid [rad]
    lon: longitude of ellipsoid [rad]
    height: height above ellipsoid [m]
    
    Returns:
    coordinates in ECEF coordinate system.
    '''
    
    WGS_84_dict = {"axes": (6378137.0, 6356752.314245)} #m semi-minor and semi-major axis of WGS-84 geoid
    a, b = WGS_84_dict["axes"] #values come from: https://en.wikipedia.org/wiki/World_Geodetic_System#WGS84
    
    e_squared = e2(a, b)
    N = calc_N(a, e_squared, lat)

    x = (N + height) * np.cos(lat) * np.cos(lon)
    y = (N + height) * np.cos(lat) * np.sin(lon)
    z = ((1 - e_squared)*N + height) * np.sin(lat)
    return np.array([x,y,z])

def calc_N(a, e_squared, lat):
    '''Calculate the radius of curvature (N) in the prime vertical.
    
    Parameters:
    e_squared: eccentricity
    lat: latitude [rad]
    
    Returns:
    Radius of curvature in prime vertical.
    
    '''
    return a/np.sqrt(1 - e_squared*(np.sin(lat))**2)

def e2(a, b):
    '''This function calculates the squared eccentricity.
    
    Parameters:
    a: semi-major axis
    b: the semi-minor axis b 
    f: flattening factor f=1−ba
    
    Returns:
    Squared eccentricity.
    '''
    f = 1 - (b/a)
    e_squared = 2*f - f**2
    return e_squared
```

With these functions it is easy to transform the lat/lon/height position of the HALO into the ECEF-coordinate system:

```{code-cell} ipython3
HALO_ecef = ellipsoidal_to_ecef(np.deg2rad(ds_selection["lat"]), 
                                np.deg2rad(ds_selection["lon"]), 
                                ds_selection["alt"])

HALO_ecef = xr.Dataset({"time": ds_selection.time.drop(labels=("lon", "lat")),
                        "HALO_ecef": xr.DataArray(HALO_ecef, dims = ["direction", "time"])
                       })
```

As a next step we want to set up the vector of the viewing direction. We will need the rotation matrices Rx, Ry and Rz for this.

```{code-cell} ipython3
def Rx(alpha):
    return np.array([[np.ones(alpha.shape), np.zeros(alpha.shape), np.zeros(alpha.shape)],
                     [np.zeros(alpha.shape), np.cos(alpha), np.sin(alpha)],
                     [np.zeros(alpha.shape), -np.sin(alpha), np.cos(alpha)]])
def Ry(alpha):
    return np.array([[np.cos(alpha), np.zeros(alpha.shape), -np.sin(alpha)],
                     [np.zeros(alpha.shape), np.ones(alpha.shape), np.zeros(alpha.shape)],
                     [np.sin(alpha), np.zeros(alpha.shape),  np.cos(alpha)]])
def Rz(alpha):
    return np.array([[ np.cos(alpha),  np.sin(alpha), np.zeros(alpha.shape)],
                     [-np.sin(alpha),  np.cos(alpha), np.zeros(alpha.shape)],
                     [ np.zeros(alpha.shape), np.zeros(alpha.shape), np.ones(alpha.shape)]])
```

Now we can calculate the viewing direction relative to the local horizon coordinate system.

```{code-cell} ipython3
def vector_lh(ds):
    '''Calculate the viewing direction relative to the local horizon coordinate system.
    The viewing direction is defined by the viewing zenith and azimuth angles which 
    are part of the dataset. Two rotations are carried out to rotate the vector 
    pointing into the downward direction into the viewing direction:
    1. Rotation around the y-axis with the viewing zenith angle
    2. Rotation around the z-axis with the viewinzg azimuth angle.
    '''
    down = xr.DataArray(np.array([0,0,1]), dims = ["direction"])
    rot_view_lh = xr.Dataset({"time": ds.time.drop(labels=("lon", "lat")),
                              "angle": ds.angle,
                              "rot_vza": xr.DataArray(Ry(np.deg2rad(-ds["vza"])), dims = ["i", "direction", "time", "angle"]),
                              "rot_vaa": xr.DataArray(Rz(np.deg2rad(-ds["vaa"])), dims = ["i", "direction", "time", "angle"])})

    view_lh = xr.dot(rot_view_lh.rot_vza, down, dims="direction")
    view_lh = xr.dot(rot_view_lh.rot_vaa.rename({"direction": "i", "i": "direction"}),view_lh, dims="i").transpose("direction", "angle", "time")
    return view_lh/np.linalg.norm(view_lh, axis = 0)

view_lh = vector_lh(ds_selection)
```

We need an approximation of the cloud top height and will use 1000 m as a first guess. First create an array of the cloudheight which has the same dimensions as the cloud mask. If you have better cloudheight data just put in your data.

```{code-cell} ipython3
height_guess = 1000 #m
cth = xr.Dataset({"time": ds_selection.time.drop(labels=("lon", "lat")),
                  "angle": ds_selection.angle, 
                  "cloudheight": xr.DataArray(da.ones_like(ds_selection.cloud_mask)*height_guess, dims=("time", "angle"))})
print(cth)
```

Now let's calculate the length of the vector connecting HALO and the cloud. We need the height of the HALO, the cloudheight and the viewing direction for this.

```{code-cell} ipython3
viewpath_lh = (view_lh * np.abs(ds_selection["alt"] - cth.cloudheight)/view_lh.isel(direction=2))
viewpath_lh = viewpath_lh.transpose("direction", "angle", "time")
```

Now we would like to transform this viewpath also into the ECEF coordinate system. We will stick to the method described here: https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates

```{code-cell} ipython3
def lh_to_ecef(enu_vector, lat, lon):
    '''Transform vector of coordinates/directions with respect to the local horizon coordinate system into the ECEF system.
    see: https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates adjusted to NED coordinate system
    
    Parameters:
    enu_vector: coordinates as expressed in local horizon coordinates/ENU coordinates
    lat: latitude of HALO position [degree]
    lon: longitude of HALO position [degree]
    
    Returns:
    Vector expressed in ECEF coordinates.
    '''
    rot_matrix_inv =  np.einsum('lm...,mn...,nd...->ld...', Ry(np.deg2rad(np.ones(lon.shape)*90)), Rx(-np.deg2rad(lon)),Ry(np.deg2rad(lat)))
    ecef_vector = np.einsum('mn...,nd...->md...',rot_matrix_inv, enu_vector)
    return ecef_vector

viewpath_ecef = lh_to_ecef(viewpath_lh, ds_selection["lat"].values, 
                           ds_selection["lon"].values)
viewpath_ecef = xr.Dataset({"time": ds_selection.time.drop(labels=("lon", "lat")),
                            "angle": ds_selection.angle,
                            "viewpath_ecef": xr.DataArray(viewpath_ecef, dims = ["direction","angle", "time"])
                           })
```

If we add the viewpath to the position of the HALO the resulting point gives us the ECEF coordinates of the point on the cloud.

```{code-cell} ipython3
cloudpoint_ecef = HALO_ecef.HALO_ecef + viewpath_ecef.viewpath_ecef
x_cloud, y_cloud, z_cloud = cloudpoint_ecef
```

The last step is to transform these coordinates into ellipsoidal coordinates. Again we stick to the description here: https://gssc.esa.int/navipedia/index.php/Ellipsoidal_and_Cartesian_Coordinates_Conversion

```{code-cell} ipython3
def ecef_to_ellipsoidal(x, y, z, iterations=10):
    '''Transformation from ECEF coordinates to ellipsoidal coordinates according to:
    https://gssc.esa.int/navipedia/index.php/Ellipsoidal_and_Cartesian_Coordinates_Conversion
    
    Parameters:
    x, y, z: cartesian coordinates (ECEF)
    iterations: increase this value if the change between two successive values 
                of latitude is larger than the precision required.
    Returns:
    Vector expressed in ellipsoidal coordinates.
    '''
    WGS_84_dict = {"axes": (6378137.0, 6356752.314245)} #m
    a, b = WGS_84_dict["axes"] #semi-major and semi-minor axis a and b of the WGS-84 ellipsoid
        
    lon = np.arctan2(y,x) #radians    
    e_squared = e2(a, b)    
    p = np.sqrt(x**2 + y**2)     
    lat = np.arctan2(z, (1 - e_squared)*p)    
    
    for i in range(iterations):
        N = calc_N(a, e_squared, lat)
        height = p / np.cos(lat) - N
        lat = np.arctan2(z, (1-e_squared * (N/(N+height)))*p)
    return [np.rad2deg(lat), np.rad2deg(lon), height]

cloudlat, cloudlon, cloudheight = ecef_to_ellipsoidal(x_cloud, y_cloud, z_cloud, iterations=10)
ds_selection.coords["cloudlon"] = (("time", "angle"), cloudlon, {'units': 'degree east'})
ds_selection.coords["cloudlat"] = (("time", "angle"), cloudlat, {'units': 'degree north'})
```

`ds.cloudlon` and `ds.cloudlat` are the projected longitude and latitude coordinates of the cloud. Now it is possible to plot the cloudmask on a map!

```{code-cell} ipython3
plt.figure(figsize=(14,6))
ax = plt.axes(projection=ccrs.PlateCarree())

fig_img = ds_selection.cloud_mask.plot.contourf(ax=ax, transform=ccrs.PlateCarree(),
                                      x='cloudlon', y='cloudlat',
                                      cmap=plt.get_cmap('Greys_r', lut=3),
                                      levels = [-0.5, 0.5, 1.5, 2.5],
                                      add_colorbar=True,
                                      cbar_kwargs={"ticks": ds_selection.cloud_mask.flag_values, })
fig_img.colorbar.set_ticklabels(ds_selection.cloud_mask.flag_meanings.split(" "))
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
```

In this two-minute long sequence we can see the curvature of the HALO circle. By the way: you could also calculate the swath width of the measurements projected onto the cloud height that you specified. The haversine formula is such an approximation. It calculates the great-circle distance between two points on a sphere (https://en.wikipedia.org/wiki/Haversine_formula). We just need the respective latitudes and longitudes of the points. We will use the coordinates of the two edge pixels of the first measurement. 

```{code-cell} ipython3
def haversine_distance(lat1, lat2, lon1, lon2, R = 6371):
    '''This formula calculates the great-circle distance between two points on a sphere with radius R in km.
    (https://en.wikipedia.org/wiki/Haversine_formula)
    
    Parameters:
    lat1: latitude of first point in radians
    lat2: latitude of second point in radians
    lon1: longitude of first point in radians
    lon2: longitude of second point in radians
    R   : Radius of sphere in km
    
    Returns: 
    Great-circle distance in km.
    '''
    dlon = lon2-lon1
    dlat = lat2-lat1
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    distance_haversine_formula = R * 2 * np.arcsin(np.sqrt(a))
    return distance_haversine_formula


lat1 = np.deg2rad(ds_selection.isel(time=0).isel(angle=0).cloudlat)
lat2 = np.deg2rad(ds_selection.isel(time=0).isel(angle=-1).cloudlat)

lon1 = np.deg2rad(ds_selection.isel(time=0).isel(angle=0).cloudlon)
lon2 = np.deg2rad(ds_selection.isel(time=0).isel(angle=-1).cloudlon)

distance_haversine_formula = haversine_distance(lat1, lat2, lon1, lon2, R = 6371)
print('The across track swath width of the measurements is about {} km'.format(np.round(distance_haversine_formula.values,2)))
```
