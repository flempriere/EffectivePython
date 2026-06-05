# Item 125: Prefer Open-Source Projects for Bundling Python Programs
over `zipimport` and `zipapp`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Consider the process of shipping a developed application (See [Item
  120](../Item_120/item_120.qmd))
  - Can be done via Package Managers (See [Item
    116](../Item_116/item_116.qmd))
  - Or by providing the source code and dependencies directly (e.g. to a
    container or server)
- Might consider putting all code and dependencies into a directory
  - Like the `pip` `site-packages` directory (See [Item
    117](../Item_117/item_117.qmd))
- Copying many dependencies can add up
  - Especially when there are large numbers of small files
  - File transfers can also alter permissions
- An old solution was to transfer a codebase as a `zip` file archive
  - Python has native support for handling these types of projects
    through the `zipimport` built-in library
    - Programs can be decompressed and loaded from within a python
      program
    - zip files must be in the `PYTHONPATH` environment variable or
      `sys.path`

``` shell
$ cd flask-deps
$ zip -r ../flask_deps.zip *
$ cd ..
$ PYTHONPATH=flask_deps.zip python3 -m flask --app=myapp routes

Endpoint     Methods  Rules
---------------------------------------------
hello_world  GET      /
static       GET      /static/<path:filename>
```

- There’s generally negligible performance cost to loading a python
  program from a `zip` archive

  - Decompression time is dwarfed by the time to load files into memory
    via I/O
  - Modern systems can also cache most of the files into memory (See
    [Item 97](../../Chapter_11/Item_097/item_097.qmd))

- Why not always compress a python program?

  - Can do so via python’s `zipapp` built-in module

    ``` shell
      $ python3 -m zipapp flask_deps -m "flask.__main__:main" -p '/usr/bin/env python3' -c
      $ ./flask_deps.pyz --app myapp routes
      Endpoint

      Endpoint     Methods  Rules
      ---------------------------------------------
      hello_world  GET      /
      static       GET      /static/<path:filename>
    ```

  - Can break data file accesses and extension modules

- For example, trying to create a `zip` archive for Django and then run
  an application

  ``` shell
  $ python3 -m compileall django
  $ zip -r django.zip Django-5.0.3.dist-info django
  $ rm -R Django-5.0.3.dist-info django
  $ PYTHONPATH=django.zip python3 django_project/manage.py check
  Traceback (most recent call last):
  ...
  OSError: No translation files found for default language en-us
  ```

- Breaks since Django looks for a file stored with the source files

  - Ends up looking inside the `zip` archive

  - Can’t be resolved and so fails

    ``` python
    # trans_real.py
    # Copyright (c) Django Software Foundation and
    # individual contributors. All rights reserved.
    class DjangoTranslation(gettext_module.GNUTranslations):

        def _init_translation_catalog(self):
            settingsfile = sys.modules[settings.__module__].__file__
            localedir = os.path.join(
                os.path.dirname(settingsfile),
                "locale",
            )
            translation = self._new_gnu_trans(localedir)
            self.merge(translation)
    ```

- Can patch this problem via the `pkgutil` built-in module

  - Inspects modules to patch data accesses

  - Works for `zip` archives and custom module loaders

  - E.g. loading the missing Django file

    ``` python
    # django_pkgutil.py
    import pkgutil

    data = pkgutil.get_data(
        "django.conf.locale",
        "en/LC_MESSAGES/django.po",
    )
    print(data.decode("utf-8"))
    ```

- `pkgutil` is generally not used in practice

  - As shown above, even Django doesn’t use it

- More common to transfer python projects as they are with their fixed
  directory structure

  - Means resources are always at a fixed location
  - Other languages might compile resources and code into a separate
    build directory
    - By default assumption becomes to handle data accesses explicitly
    - Python can be more flexible since code should be colocated with
      data

- `zipapp` also can’t load extension modules (See [Item
  96](../../Chapter_11/Item_096/item_096.qmd))

  - This is due to the Operating System

- For example, trying to run `numpy`

  ``` shell
    $ zip -r ./numpy.zip numpy numpy-1.26.4.dist-info
    $ rm -R numpy numpy-1.26.4.dist-info
    $ PYTHONPATH=numpy.zip python -c 'import numpy'
    Traceback(most recent call last):
    ...
    ModuleNotFoundError: No module named 'numpy.core._multiarray_umath'

    During handling of the above exception, another exception occurred:

    Traceback(most recent call last):
    ...
    ImportError:

    IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!


    Importing the numpy C-extensions failed. This error can happen for many
    reasons, often due to issues with your setup or how NumPy was installed.
    ...
  ```

- Extension modules are common and popular for many python packages

  - Alleviate CPU-intensive tasks (See [Item
    96](../../Chapter_11/Item_096/item_096.qmd))
  - Thus avoid using `zipimport` and `zipapp` for anything but a trivial
    program

- Python’s open-source community has a number of better methods for
  deploying Python programs

  1.  [Pex](https://github.com/pex-tool/pex)

  2.  [Shiv](https://github.com/linkedin/shiv)

      - Provide `zipapp`-like functionality but provide solutions to
        data file sourcing and extension modules

        ``` shell
         $ pip install -e django_project
         $ pex django_project -o myapp.pex
         $ ./django_project.pex -m manage check
         System check identified no issues (0 silenced)
        ```

  3.  [PyInstaller](https://pyinstaller.org/en/stable/)

      - Bundles a python executable to create a standalone executable
        program

- These tools can take some experimentation

  - Make sure to read the docs

## Things to Remember

- Python can load and execute modules directly from `zip` archives

  - Enables applications to be deployed as single-files

- Many common open-source packages break when deployed via a `zip`
  archive, due to

  1.  Reliance on data files
  2.  Use of native extension libraries

- Use community-built alternatives to `zipapp` like `Pex` or
  `PyInstaller` to get the benefits of `zip` archives and single-file
  installs without the downsides
