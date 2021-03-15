# running How to EUREC4A locally

There are multiple options to run the Code examples from this book locally.
In any case, it will involve the following steps:
* install Python (we assume hat this is already done, have a look at [python.org](https://python.org) if you want to get it)
* obtain the code from the book
* install all required dependencies
* run the code

You can decide between the [quick an dirty](#quick-and-dirty) method and the method [using `git`](#via-git), which will also set you up to contribute to the book.

## quick and dirty
If you just like to run the code of a single notebook and don't care to much about the details, the quickest option might be to download the chapter you are viewing as an ipython notebook (`.ipynb`) via the download button (<i class="fas fa-download"></i>) on the top right of the page. If you don't see the `.ipynb` option here, that's because the source of the page can not be interpreted as a notebook and thus is not available for direct execution.

If you would just run the downloaded code, the chance is high that some required libraries are not yet installed on your system. You can either do try and error to find out which libraries are required for the chapter you downloaded, or you can simply installed all requirements for the entire book by running the following command on your command line:
```bash
pip install jupyter
pip install -r https://raw.githubusercontent.com/eurec4a/how_to_eurec4a/master/requirements.txt
```

Afterwards, you can start a local notebook server (either `jupyter notebook` or `jupyter lab`) and run and modify the chapter locally.

```{note}
Handling requirements in this project is not entirely straightforward, as the requirements strongly depend on which datasets are used. We use [intake catalogs](https://intake.readthedocs.io) to describe how a dataset can be accessed which simplifies a lot of things. But as a consequence the set of required libraries is not only determined by the code in this repository, but also by the entries in the catalog.
```

## via git

If you like to do it more properly, you can also clone the repository via git:

```bash
git clone git@github.com:eurec4a/how_to_eurec4a.git
```

This will create a local copy of the entire book repository in a newly created local folder `how_to_eurec4a`.
Please change into this directory.

````{admonition} Maybe use a virtual environment
:class: dropdown, tip
You might want to use a virtual environment for the book if you like to keep the required libraries in a confined place, but it is entirely optional and up to your preferences.
There are many options to do so and [virtualenv](https://virtualenv.pypa.io/) is one of them.
Using virtualenv, you could create and aktivate an environment like:
```bash
virtualenv venv
. venv/bin/activate
```
and the continue normally.
````
You'll have to install the dependencies as above, but as you already have all the files on your machine, you can also install it directly via:

```bash
pip install -r requirements.txt
```

Depending on your needs, you can continue using [interactive notebooks](#interactive) or [compile the entire book](#compile-the-book).

```{admonition} About MyST notebooks.
:class: dropdown
Internally, the book does not use the `.ipynb` file format as it is not well-suited for version control.
Instead, we use [Markedly Structured Text](https://myst-parser.readthedocs.io/) or MyST which is a variant of Markdown, optimized to contain executable code cells as in notebooks.
The extension of MyST files is `.md`.
In contrast to notebooks, these files **do not** contain generated cell outputs, so you'll actually have to run the files in order to see anything.

`jupytext` is used to convert between MyST and `ipynb` formats.
It is installed through the `requirements.txt` and should register itself with `jupyter`, so that you can open the files as if they where `ipynb` files.
If that does not work, please have a look at the [installation instructions](https://jupytext.readthedocs.io/en/latest/install.html) of `jupytext`.
```

### interactive
`jupyter` itself is not installed by the requirements file. You might want to install it as well:

```bash
pip install jupyter
```

Once everything is set up, you can either start your notebook server:
````{panels}
... either using classical notebooks
```bash
jupyter notebook
```
---
... or using jupyter lab
```bash
jupyter lab
```
````

### compile the book
You can also execute `jupyter-book` directly via:
```bash
jb build how_to_eurec4a
```
which itself will run all code cells and output the results as HTML pages in a newly created folder.
This variant is especially useful if you like to work directly on the MyST files (see note below) using a text editor and should be done every time before you submit new changes to the book.
