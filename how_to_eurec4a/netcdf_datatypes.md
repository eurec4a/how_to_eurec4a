# The issue with netCDF data types

```{admonition} TL; DR
:class: tip
If you want to be on the safe side, use only `SHORT`, `INT`, `FLOAT`, `DOUBLE`, `STRING` or array of `CHAR` as data types.
In particular, **dont't** use single byte integers, any unsigned integer and no 64 bit integer.
```

The data format netCDF which is used in many places throughout our community has evolved over time.
During this evolution, the internally representable data types have also changed.
Currently we are at netCDF version 4 with HDF5 as a storage backend, which offers a lot more flexibility as compared to previous versions of netCDF including many more [data types](https://www.unidata.ucar.edu/software/netcdf/docs/data_type.html).
One **could** assume that this is all fine and we can use these data types freely, but here we are unlucky and there is more to keep in mind.
In order to paint the full picture, we'll have to take a little detour and think about what netCDF actually is.

## What is netCDF?
NetCDF is more than only the "netCDF4 on HDF5" storage format.
This is not only a bold statement, but is actually asked and discussed by the netCDF developers ([What is netCDF?](https://github.com/Unidata/netcdf-c/issues/1590), Jan 2020).
This chapter is not exactly about the same topic in the referenced issue, but still has similar roots.
The relevant part for this discussion is that there is at least netCDF, the **data model** and netCDF, the **persistence format**.
It is also recognized that there are multiple persistence formats (netCDF3, netCDF4/HDF5, zarr) for the same data model and there are translation layers such as OPeNDAP which can be used as a transport mechanism between the computer on which data is stored and the computer on which data is analyzed.
In order to see how this might be relevant for out datasets, we have to look into these things separately.

### The data model(s)
There are actually a few different data models around, which share some general ideas.
Maybe the most illustrative way to show this model is an extended version of [xarray](http://xarray.pydata.org/)'s logo, but the underlying ideas are of course applicable independently of xarray or even Python.
```{figure} dataset-diagram.png
:alt: dataset diagram
:align: center
:width: 70%

Dataset diagram (From the [xarray documentation](http://xarray.pydata.org/en/stable/data-structures.html))
```
A dataset is a collection of _variables_ and _dimensions_.
Variables are multi-dimensional arrays and they can share dimensions (i.e. to express that `temperature` and `precipitation` are defined at the same locations, the three axes of the corresponding arrays should be identified with the same dimension label, that is `x`, `y` and `z`).
Some variables may be promoted into a _coordinate_, which does not require to store it differently, but it changed how one would interpret the data.
In the example above, `latitude` and `longitude` would likely be identified as coordinates.
One would typically use _coordinate_ values to index into some data or to label the ticks on a plot axis, while a normal _variable_ would usually be used to define a line or a color within a plot.
There may be _variables_ which should be _coordinates_ only for a specific use case and vice versa.
It is useful to distinguish between _variables_ and _coordinates_ within the metadata of a dataset, but the representation of the actual data may be the same for both, _variables_ and _coordinates_.
This high level formulation of a data model is very useful as many datasets fit very well into this general concept.

In order to be of practical use, this high level data model must be translated into a low level data model which can actually be used to store and process data.
NetCDF defines the [Classic](https://www.unidata.ucar.edu/software/netcdf/docs/netcdf_data_model.html#classic_model) and the [Enhanced](https://www.unidata.ucar.edu/software/netcdf/docs/netcdf_data_model.html#enhanced_model) model for this purpose.
Both models care about _variables_ and _dimensions_ as introduced above and add _attributes_ which may be attached to _variables_ and entire _datasets_ to carry additional metadata (e.g. to declare _coordinates_).
The classical model knows about `CHAR`, `BYTE`, `SHORT`, `INT`, `FLOAT` and `DOUBLE` data types which are all **signed**.
The enhanced model adds `INT64` and `STRING` to the mix as well as **unsigned** variants of all integral types.
Further additions of the enhanced model are groups (which are like a dataset within a dataset) and user defined types.

### The storage formats
* netCDF3
* netCDF4 / HDF5
* OPeNDAP
* zarr

## Why should we care?
Each of the formats has distinct advantages and disadvantages:

* **netCDF** is a compact format, the whole dataset can be stored in a single file which can be transferred from one place to another and everything is contained. This is great for storing data and to send around smaller datasets, but retrieving only a subset of a dataset from a remote server is not possible. Libraries which can open netCDF files usually do not handle HTTP, so the dataset needs to be stored in a local directory to use it.
* **OPeNDAP** is a network protocol based on HTTP which has been made exactly for the purpose of requesting subsets of a dataset from a remote server. As it is only a network protocol, it can not be used to store the data, so every dataset which should be provided via OPeNDAP must be stored in another format (like netCDF) or computed on the fly. Support for reading OPeNDAP is build into netCDF-c.
* **zarr** is a storage format which is spread out into several files in a defined directory structure [^zipfile_zarr]. This makes it a little harder to pass around, but this chunked structure makes remote access exceptionally simple and fast. Chelle Gentemann has prepared an [impressive demonstration](https://nbviewer.jupyter.org/github/oceanhackweek/ohw20-tutorials/blob/master/10-satellite-data-access/goes-cmp-netcdf-zarr.ipynb) on this topic.

So, depending on the use case, different formats are optimal and none of them supports everything:

| format  | for storage | sending around | for remote access      | widely supported              |
| ------- | ----------- | -------------- | ---------------------- | ----------------------------- |
| netCDF  | ✅          | ✅             | ❌, works via OPeNDAP  | ✅                            |
| OPeNDAP | no          | no             | ✅, can share netCDF   | ✅                            |
| zarr    | ✅          | moderate       | ✅, very performant    | ❌, netCDF-c is working on it |

As a result, we should take care that our datasets are convertible between those formats.

[^zipfile_zarr]: zarr can be used as a single file by using a zip file as its directory structure.
