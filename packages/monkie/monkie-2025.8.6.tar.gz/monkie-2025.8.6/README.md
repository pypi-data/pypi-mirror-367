[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

# [MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/) (a Marimo NotebooK Image Explorer) 

MoNkIE is a multi-dimensional image explorer built for Marimo notebooks!
MoNkIE is based off of [JuNkIE]((https://bitbucket.org/rfg_lab/junkie/src/master/), the Jupyter Notebook Image Explorer.

## Installing [MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/)

To install [MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/), type:

    $ python3 -m pip install --no-chache-dir -U monkie

## Using [MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/)

[MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/) requires that you call two simple functions in
separate cells to load the image and show the UI, respectively:

```python
# Put this in your setup cell
from src.monkie import monkie
```

```python
# First cell
monkie.load(image)
```

```python
# Second cell
monkie.show()
```

There are a few ways to open an image with [MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/):

- You can open an image with some other package (e.g. scikit-image, opencv, PIL, etc.) and pass a 
[numpy ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) to 
[MoNkIE](https://bitbucket.org/raymond_hawkins_utor/monkie/src/main/) as the parameter

- You can specify the path to the image that you want to open

- Or you can indicate a folder that contains an image sequence.

  - If there are image channels split into different files, you can also specify a tuple of strings to distinguish which files in the folder belong to which channel.

*setup_ui* (bool) specifies whether you want to create the UI elements (True) or just load the image (False). (Defaults to True)