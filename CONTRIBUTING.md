# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given. You can contribute in the ways listed below.

## Report Bugs

Report bugs using GitHub issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

## Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

## Write Documentation

How to EUREC⁴A could always use more documentation, whether as part of the
official How to EUREC⁴A docs, in docstrings, or even on the web in blog posts,
articles, and such.


## Get Started

Ready to contribute? Here's how to set up `How to EUREC⁴A` for local development.

1. Fork the repo on GitHub.
2. Clone your fork locally.
3. Install your local copy into a virtualenv, e.g., using `conda`.
4. Create a branch for local development and make changes locally.
5. Commit your changes and push your branch to GitHub.
6. Submit a pull request through the GitHub website.

### Note on  Enabling `jupytext`

`jupytext` is responsible to enable `MySt` formatted markdown within jupyter notebooks. It should be enabled automatically by installing `jupytext`, which is also included in the `requirements.txt`. So chances are high that you don't have to do anything special. However if that doesn't work out of the box, please have a look at their [install instructions](https://jupytext.readthedocs.io/en/latest/install.html). In particular, the command `jupyter serverextension enable jupytext` may help.

### Building the book

To check your changes locally you can build the book:

- (Recommended) Remove the existing `how_to_eurec4a/_build/` directory
- Run `jupyter-book build how_to_eurec4a/`

A fully-rendered HTML version of the book will be built in `how_to_eurec4a/_build/html/`.


## Code of Conduct

Please note that the How to EUREC⁴A project is released with a [Contributor Code of Conduct](CONDUCT.md). By contributing to this project you agree to abide by its terms.
