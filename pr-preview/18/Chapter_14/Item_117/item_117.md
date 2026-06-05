# Item 117: Use Viirtual Environments for Isolated and Reproducible
Dependencies


- [Notes](#notes)
  - [Using `venv` on the Command Line](#using-venv-on-the-command-line)
  - [Reproducing Dependencies](#reproducing-dependencies)
- [Things to Remember](#things-to-remember)

## Notes

- By default `pip` installs packages into a global environment

  - Means every python program is impacted by installed modules (See
    [Item 116](../Item_116/item_116.qmd))
  - `pip` needs to resolve a consistent set of package versions across
    all of your programs

- Many fundamental packages are used by multiple different projects

- For example, we can see the dependencies of `Sphinx` after installing
  it as,

  ``` shell
    $ python3 -m pip show Sphinx
    Name: Sphinx
    Version: 7.4.6
    Summary: Python documentation generator
    Location: /usr/local/lib/python3.13/site-packages
    Requires: alabaster, babel, docutils, imagesize, Jinja2,
        - packaging, Pygments, requests, snowballstemmer,
        - sphinxcontrib-applehelp, sphinxcontrib-devhelp,
        - sphinxcontrib-htmlhelp, sphinxcontrib-jsmath,
        - sphinxcontrib-qthelp, sphinxcontrib-serializinghtml
  ```

- We might then install `flask`, which shares a similar dependency
  `Jinja2`

  ``` shell
    python3 -m pip show flask
    Name: Flask
    Version: 3.0.3
    Summary: A simple framework for building complex web applications.
    Location: /usr/local/lib/python3.13/site-packages
    Requires: blinker, click, itsdangerous, Jinja2, Werkzeug
  ```

- As `Sphinx` and `flask` diverge over time, they might require have
  different requirements on `Jinja2`

  - Upgrading `Jinja2` directly might break both of them!

    ``` shell
      python3 -m pip install --upgrade Jinja2
    ```

- This occurs because the global state can only have *one* version of a
  package at time

  - In the worst case this can result in breaking the system
    dependencies that an OS needs to run core programs
  - This situation is often referred to as *dependency hell* (See [Item
    119](../Item_119/item_119.qmd))

- Furthermore, when collaborating using the global state means that
  people’s development environments are likely to vary significantly
  from each other

- Solution is to use a *virtual environment*

  - `venv` is bundled with python since Python 3.4

    ``` shell
      python3 -m venv
    ```

- Virtual environments let you create isolated environments for each
  python project

  - Each environment can have different versions of packages installed

- `venv` sets up each virtual environment as it’s own directory
  structure

### Using `venv` on the Command Line

- A new virtual environment is created with `venv`

  ``` shell
    $ python3 -m venv myproject # name of the virtual environment
    $ cd myproject
    $ ls
    bin include lib pyvenv.cfg
  ```

- To start a virtual environment you need to run the activation script

  - This changes depending on the terminal

  - For a standard `bash` shell

    ``` shell
      $ source bin/activate
      (myproject) $
    ```

  - For Windows with `batch` files

    ``` shell
      C:\>myproject\Scripts\activate.bat
      (myproject) C:>
    ```

  - Observe that the name of the virtual environment is prepended to
    head of the shell prompt

- The python path should update to be within the virtual environment

  ``` shell
     (myproject)$ which python3
     /tmp/myproject/bin/python3
     (myproject)$ ls -l /tmp/myproject/bin/python3
     ... -> /usr/local/bin/python3
  ```

- Virtual environment and the global environment are now isolated from
  each other

- By default a virtual environment should come with the `pip` and
  `setuptools` packages

  - Will not carry across other globally installed packages

- Packages installed while the virtual environment is active will use
  the virtual environment’s `pip`

  - They are then installed into the virtual environment

  ``` shell
    python3 -m pip install numpy
    Collecting numpy
        Downloading...
    Installed collected packages: numpy
    Successfully installed numpy-2.0.0
  ```

- To deactivate the virtual environment just call the `deactivate`
  command

  ``` shell
    (myproject)$ which python3
    /tmp/myproject/bin/python3
    $ which python3
    /usr/local/bin/python3
  ```

### Reproducing Dependencies

- Once we have a virtual environment set-up you might naturally want to
  copy it somewhere else

  - Often to let someone else replicate your environment
  - Or to replicate theirs

- We can use `python -m pip freeze` to save a list of the dependencies

  ``` shell
    (myproject)$ python3 -m pip freeze > requirements.txt
    (myproject)$ cat requirements.txt

    certifi==2024.7.4
    charset-normalizer==3.3.2
    idna==3.7
    numpy==2.0.0
    requests==2.32.3
    urllib3==2.2.2
  ```

- We can then ingest this requirements.txt file into a new virtual
  environment

  - We use the `-r` flag on `pip install` to tell `pip` to read a
    requirements.txt file

  ``` shell
    $ python3 -m venv otherproject # create a new virtual environment
    $ cd otherproject
    $ source bin/activate
    (otherproject)$ python3 -m pip install -r /tmp/myproject/requirements.txt
  ```

- requirements.txt don’t provide all the details about an environment

  - But should work for most cases
  - Doesn’t specify the python version (this has to be handled
    separately)

- More advanced tools like `uv` and `poetry` act as higher level
  interfaces over the top of a virtual environment

  - They also provide more advanced mechanisms for dependency management
    and environment synchronisation than requirements.txt
  - Often taking advantage of the new `pyproject.toml` file format

## Things to Remember

- Virtual environments help you create isolated development environments
  for different projects
- Virtual environments are created with `python -m venv`
  - Enabled with `bin/activate`
  - Disabled with `deactivate`
- You can dump requirements of an environment into a requirements.txt
  with
  - `python -m pip freeze`
- You can ingest requirements of an environment into another to
  reproduce it with
  - `python -m pip install -r requirements.txt`
