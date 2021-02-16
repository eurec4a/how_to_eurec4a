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

# Show the intake catalog

The eurec4a intake catalog is maintained on github at [eurec4a/eurec4a-intake](https://github.com/eurec4a/eurec4a-intake). The structure of the files however does not represent the structure of the catalog. In order to get a quick overview about its contents, here's a little script which prints out the current catalog tree.

```{code-cell} ipython3
import eurec4a
```

```{code-cell} ipython3
cat = eurec4a.get_intake_catalog()
```

```{code-cell} ipython3
def tree(cat, level=0):
    prefix = " " * (3*level)
    try:
        for child in list(cat):
            print(prefix + str(child))
            tree(cat[child], level+1)
    except:
        pass
```

```{code-cell} ipython3
tree(cat)
```

There's also a graphical user interface (GUI) implemented in intake. The GUI additionally requires the `panel` python package and it interactively queries the catalog, so it doesn't work nicely in a book. This is why the following lines of code are commented out, but they can be used in an interactive notebook.

```{code-cell} ipython3
#import intake
#intake.gui.add(cat)
#intake.gui.panel
```
