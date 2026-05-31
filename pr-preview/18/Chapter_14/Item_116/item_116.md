# Item 116: Know Where to Find Community-Built Modules


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- [PyPI](https://pypi.org/) is the official python package repository

- Packages are installed by `pip` or a higher level management tool like
  `uv`

  - `pip` can be run standalone or as a python module

    ``` shell
      python3 -m pip
    ```

  - Running as a module ensures modules are installed for the correct
    python version (See [Item
    1](../../Chapter_01/Item_001/item_001.qmd))

- For example to install `numpy`

  ``` shell
    $ python3 -m pip install numpy
    Collecting numpy
    Downloading...
    Installing collected packages: numpy
    Successfully installed numpy-2.0.0
  ```

- `pip` is best paired with the `venv` built-in to create a consistent
  development environment (See [Item 117](../Item_117/item_117.qmd))

- You can create and upload your own packages to PyPI

  - Or configure `pip` to use your own private repositories

- Modules in PyPI are typically provided with a license

  - Most packages are free or open-source (See [Item
    125](../Item_125/item_125.qmd))
  - Depending on your use-case you might need to review the license in
    more detail

## Things to Remember

- Python Package Index (PyPI) contains packages built and maintained by
  the python community
- `pip` is the command-line tool for installing packages
  - By default uses PyP
- Most PyPI projects have free or open-source licenses
