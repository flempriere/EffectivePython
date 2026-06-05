# Item 121: Define a Root `Exception` to Insulate Callers from APIs


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Module’s API consistent of the attributes they expose as well as the
  exceptions they may raise (See [Item
  32](../../Chapter_05/Item_032/item_032.qmd))
- Python has a hierarchy of exceptions (See [Item
  86](../../Chapter_10/Item_086/item_086.qmd))
- Tempting to use built-in exceptions for errors
  - Since the external consumer might naturally try to catch these
  - Plus no need to reinvent the wheel
- For example, might raise a `ValueError` for an invalid parameter value

``` python
def determine_weight(volume, density):
    if density <= 0:
        raise ValueError("Density must be positive")


determine_weight(1, -10)
```

    ValueError: Density must be positive
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[1], line 6
          2     if density <= 0:
          3         raise ValueError("Density must be positive")
    ----> 6 determine_weight(1, -10)

    Cell In[1], line 3, in determine_weight(volume, density)
          1 def determine_weight(volume, density):
          2     if density <= 0:
    ----> 3         raise ValueError("Density must be positive")

    ValueError: Density must be positive

- For API’s typically want to define a new hierarchy of exceptions
- Typically define a root `Exception` for a given API
  - All other exceptions must then inherit from this one

``` python
class Error(Exception):
    """Base class for all exceptions raised by this module"""

    pass


class InvalidDensityError(Error):
    """There was a problem with a provided density value"""

    pass


class InvalidVolumeError(Error):
    """There was a problem with the provided weight value"""

    pass


def determine_weight(volume, density):
    if density < 0:
        raise InvalidDensityError("Density must be positive")
    if volume < 0:
        raise InvalidVolumeError("Volume must be positive")
    density / volume  # trigger a divide by zero error


# using the module
try:
    weight = determine_weight(1, -1)
except Error as e:
    print(f"Unexpected error: {repr(e)}")
```

    Unexpected error: InvalidDensityError('Density must be positive')

- The caller can then use a `try` / `except` block around our API calls
  catching the root exception

  - Prevents the API exception from propagating up the calling program
  - Provides an insulation layer

- Has three helpful effects

  1.  Root exception makes it clear when the caller is misusing an API
  2.  Distinguishes misuses of the API from the API itself having a bug
  3.  Future-proofs an API
      - Can expand to provide more exception types for specific
        situations

- For example, here we can see that the API is being misused

  - Here the insulating catch-all on the `Error` type prevents the
    exception from crashing the program
  - But is still identified to be properly handled later

``` python
import logging


class Error(Exception):
    """Base class for all exceptions raised by this module"""

    pass


class InvalidDensityError(Error):
    """There was a problem with a provided density value"""

    pass


class InvalidVolumeError(Error):
    """There was a problem with the provided weight value"""

    pass


def determine_weight(volume, density):
    if density < 0:
        raise InvalidDensityError("Density must be positive")
    if volume < 0:
        raise InvalidVolumeError("Volume must be positive")
    density / volume  # trigger a divide by zero error


# using the module
try:
    weight = determine_weight(-1, 1)
except InvalidDensityError:
    weight = 0
except Error:  # Misuse of the API
    logging.exception("Bug in the calling code")
```

    ERROR:root:Bug in the calling code
    Traceback (most recent call last):
      File "/tmp/ipykernel_14190/1234711497.py", line 32, in <module>
        weight = determine_weight(-1, 1)
      File "/tmp/ipykernel_14190/1234711497.py", line 26, in determine_weight
        raise InvalidVolumeError("Volume must be positive")
    InvalidVolumeError: Volume must be positive

- If we instead have a bug in the API itself it will bypass the
  insulation layer and propagate up
  - Or can be caught and recorded separately
  - As per below, the `determine_weight` code has a division by zero
    error since it doesn’t account for the case of volume being zero.
  - Caller needs to extend the `try/except` block that catches the
    broader Python `Exception` class to handle the error (See [Item
    85](../../Chapter_10/Item_085/item_085.qmd))

``` python
import logging


class Error(Exception):
    """Base class for all exceptions raised by this module"""

    pass


class InvalidDensityError(Error):
    """There was a problem with a provided density value"""

    pass


class InvalidVolumeError(Error):
    """There was a problem with the provided weight value"""

    pass


def determine_weight(volume, density):
    if density < 0:
        raise InvalidDensityError("Density must be positive")
    if volume < 0:
        raise InvalidVolumeError("Volume must be positive")
    density / volume  # trigger a divide by zero error


try:
    weight = determine_weight(0, 1)
except InvalidDensityError:
    weight = 0
except Error:
    logging.exception("Error in the calling code")
except Exception:  # catch anything else
    logging.exception("Bug in the API code!")
    raise  # Re-raise exception to the caller
```

    ERROR:root:Bug in the API code!
    Traceback (most recent call last):
      File "/tmp/ipykernel_14190/4162312265.py", line 31, in <module>
        weight = determine_weight(0, 1)
      File "/tmp/ipykernel_14190/4162312265.py", line 27, in determine_weight
        density / volume  # trigger a divide by zero error
        ~~~~~~~~^~~~~~~~
    ZeroDivisionError: division by zero

    ZeroDivisionError: division by zero
    ---------------------------------------------------------------------------
    ZeroDivisionError                         Traceback (most recent call last)
    Cell In[4], line 31
         27     density / volume  # trigger a divide by zero error
         30 try:
    ---> 31     weight = determine_weight(0, 1)
         32 except InvalidDensityError:
         33     weight = 0

    Cell In[4], line 27, in determine_weight(volume, density)
         25 if volume < 0:
         26     raise InvalidVolumeError("Volume must be positive")
    ---> 27 density / volume

    ZeroDivisionError: division by zero

- And for example, later we have introduced a new specific
  `NegativeDensityError`
  - As long as we expand consistently with our established hierarchy
    calling code shouldn’t need to change

``` python
import logging


class Error(Exception):
    """Base class for all exceptions raised by this module"""

    pass


class InvalidDensityError(Error):
    """There was a problem with a provided density value"""

    pass


# New exception class
class NegativeDensityError(InvalidDensityError):
    """A provided density value was negative"""

    pass


class InvalidVolumeError(Error):
    """There was a problem with the provided weight value"""

    pass


def determine_weight(volume, density):
    if density < 0:
        raise NegativeDensityError("Density must be positive")
    if volume < 0:
        raise InvalidVolumeError("Volume must be positive")
    density / volume  # trigger a divide by zero error


try:
    weight = determine_weight(1, -1)
except NegativeDensityError:
    raise ValueError("Must supply non-negative density")
except InvalidDensityError:
    weight = 0
except Error:
    logging.exception("Bug in the calling code")
except Exception:
    logging.exception("Bug in the API code!")
    raise
```

    ValueError: Must supply non-negative density
    ---------------------------------------------------------------------------
    NegativeDensityError                      Traceback (most recent call last)
    Cell In[5], line 38
         37 try:
    ---> 38     weight = determine_weight(1, -1)
         39 except NegativeDensityError:

    Cell In[5], line 31, in determine_weight(volume, density)
         30 if density < 0:
    ---> 31     raise NegativeDensityError("Density must be positive")
         32 if volume < 0:

    NegativeDensityError: Density must be positive

    During handling of the above exception, another exception occurred:

    ValueError                                Traceback (most recent call last)
    Cell In[5], line 40
         38     weight = determine_weight(1, -1)
         39 except NegativeDensityError:
    ---> 40     raise ValueError("Must supply non-negative density")
         41 except InvalidDensityError:
         42     weight = 0

    ValueError: Must supply non-negative density

- To facilitate API future-proofing consider defining a broad base set
  of exceptions just above root exception

``` python
class Error(Exception):
    """Base class for all exceptions raised by this module"""

    pass


class WeightError(Error):
    """Base class for weight calculation errors"""

    pass


class VolumeError(Error):
    """Base class for volume calculation errors"""

    pass


class DensityError(Error):
    """Base class for density error calculations"""

    pass
```

- Our specific exceptions from before can then inherit from these
  general exceptions
- These base classes can then be treated like their own root exceptions
  - Can more selectively catch against different aspects of an API
  - Reduces need to list out a long list of `Exception` subclasses

## Things to Remember

- Modules defining a root exception provides a way for API consumers to
  insulate themselves from API calls
- Catching root exceptions helps find bugs in codes consuming an API
- Catching the Python `Exception` helps identify bugs in the underlying
  API implementation itself
- Specifying intermediate base class `Exception` types building off the
  root allow the consumer to more selectively handle different exception
  types in the API code
  - Can future-proof the API usage against future derived exceptions
