# Introduction

Welcome to the world of EUREC⁴A data!
This is a collection of python code examples to get you started with the data.

## Idea
The book chapters show datasets that are accessible online, i.e. you don't have to download anything. Most datasets are accessed via the [EUREC⁴A intake catalog](https://github.com/eurec4a/eurec4a-intake), which simply said takes care of the links to datasets in their most recent version.
The scripts typically contain at minimum how to get a specific dataset and some simple plots of basic quantities. Most chapters include additional information from aircraft flight segments or further EUREC⁴A meta data, sometimes more sophisticated plots, or also a combination of variables from different datasets.

## How can you run the code?
If you want to try out the code on your machine, you'll need a few libraries to access the referenced data.
The easiest way to set this up would be to install the `eurec4a` package with the `data` option, e.g.:
```
pip install eurec4a[data]
```
afterwards, you should have everything installed to access the data. For some examples, you may have to install additional libraries for some specialized plotting methods.
If you are looking for detailed instructions to set up the entire book project including all dependencies, please refer to {doc}`running_locally`.

```{admonition} use of IPFS
:class: tip
We use [IPFS](https://ipfs.tech) to access data in a reliable way.
In principle, this works with or without a local IPFS node (e.g. [Desktop](https://docs.ipfs.tech/install/ipfs-desktop/) or [CLI](https://docs.ipfs.tech/install/command-line/)).
We recommend to **run a local node**: this will result in data access performance generally better than more classical ways of access (e.g. OPeNDAP, HTTP), whereas without a local node, access performance can be really poor.

See {doc}`data_on_ipfs` for details on this topic, and options to bypass IPFS.
```

If you want to give the chapters a really quick try and don't want to set up anything yourself, you'll find a rocket icon (<i class="fas fa-rocket"></i>) in the top bar to the right of each chapter. The icon provides two interactive ways to run the code: `Binder` and `LiveCode`. In both cases a virtual environment is created for you in the background by a click on the respective link and you don't have to take care of any requirements locally on your machine.

In principle, we anticipate to have at minimum one example script per instrument and we are very happy about contributions by you :)
If you miss some information that could be valuable, feel free to check the link on [how to contribute](https://github.com/eurec4a/how_to_eurec4a/blob/master/CONTRIBUTING.md) to this book and make a pull request or open an issue on github if you are short on time. Thanks!

## Useful links
A list of links to general information about EUREC⁴A:
* [official EUREC⁴A webpage](http://eurec4a.eu/)
* EUREC⁴A overview papers: {cite:t}`Bony:2017` and {cite:t}`Stevens:2021`
* [EUREC⁴A GitHub repository](https://github.com/eurec4a)
* [AERIS data server](https://observations.ipsl.fr/aeris/eurec4a-data/)
* [AERIS leaflet](https://observations.ipsl.fr/aeris/eurec4a/Leaflet/index.html)(data visualization)

## License

The how to EUREC⁴A book is licensed under:

```{include} LICENSE
```
