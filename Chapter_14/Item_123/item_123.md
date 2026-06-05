# Item 123: Consider `warnings` to Refactor and Migrate Usage

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- APIs evolve over time
  - Need to satisfy new requirements
- For mature APIs updating becomes a difficult choice
  - Number of callers increase and distribute over different projects
  - Unable to update API and caller’s concurrently
- Need to be able to update an API
  - Consequently notify callers to migrate
- Example, consider a basic module calculating distance travelled
- Assume,
  1. Speed is in miles per hour
  2. time is in hours

``` python
# api
def print_distance(speed, duration):
    distance = speed * duration
    print(f"{distance} miles")

# consumption
print_distance(5, 2.5)
```

    12.5 miles

- A hidden requirement of this API is the implicit units
  - E.g. if a caller passes a speed in metres per second and time in
    seconds the result is misreported

``` python
# api misuse

# api
def print_distance(speed, duration):
    distance = speed * duration
    print(f"{distance} miles")


# misuse of API
velocity_in_metres_per_second = 1000
seconds = 3
print_distance(velocity_in_metres_per_second, seconds)
```

    3000 miles

- We can patch the API by introducing additional optional arguments
  - For example using optional keyword arguments (See [Item
    37](../../Chapter_05/Item_037/item_037.qmd))

``` python
# Updated API with unit conversions

CONVERSIONS = {
    "mph": 1.60934 / 3600 * 1000,  # m/s
    "hours": 3600,  # seconds
    "miles": 1.60934 * 1000,  # m
    "meters": 1,  # m
    "m/s": 1,  # m/s
    "seconds": 1,
}


def convert(value, units):
    rate = CONVERSIONS[units]
    return rate * value


def localise(value, units):
    rate = CONVERSIONS[units]
    return value / rate


def print_distance(
    speed, duration, *, speed_units="mph", time_units="hours", distance_units="miles"
):
    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localise(norm_distance, distance_units)
    print(f"{distance} {distance_units}")


# Updated call
print_distance(1000, 3, speed_units="meters", time_units="seconds")
```

    1.8641182099494205 miles

- Using default arguments preserves backwards compatibility
- But overtime we would like users to migrate to using the keyword
  arguments
  - Forcing the change immediately would break all dependent code
- Python provides the built-in `warnings` module
  - Provides mechanism for informing consumers that code needs to be
    updated
  - Exists to be a message passing contract between programmers
  - Compare to exceptions which are for programmatic error handling (See
    [Item 81](../../Chapter_10/Item_081/item_081.qmd))
- Can use `warnings` to notify the caller when keyword arguments are not
  supplied

``` python
import warnings

# Updated API with unit conversions

CONVERSIONS = {
    "mph": 1.60934 / 3600 * 1000,  # m/s
    "hours": 3600,  # seconds
    "miles": 1.60934 * 1000,  # m
    "meters": 1,  # m
    "m/s": 1,  # m/s
    "seconds": 1,
}


def convert(value, units):
    rate = CONVERSIONS[units]
    return rate * value


def localise(value, units):
    rate = CONVERSIONS[units]
    return value / rate


def print_distance(
    speed, duration, *, speed_units=None, time_units=None, distance_units=None
):
    if speed_units is None:
        warnings.warn("speed_units required", DeprecationWarning)
        speed_units = "mph"
    if time_units is None:
        warnings.warn("time_units required", DeprecationWarning)
        time_units = "hours"
    if distance_units is None:
        warnings.warn("distance_units required", DeprecationWarning)
        distance_units = "miles"

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localise(norm_distance, distance_units)
    print(f"{distance} {distance_units}")


# old-style call
print_distance(5, 2.5)
```

    12.5 miles

    /tmp/ipykernel_14475/579820821.py:29: DeprecationWarning: speed_units required
      warnings.warn("speed_units required", DeprecationWarning)
    /tmp/ipykernel_14475/579820821.py:32: DeprecationWarning: time_units required
      warnings.warn("time_units required", DeprecationWarning)
    /tmp/ipykernel_14475/579820821.py:35: DeprecationWarning: distance_units required
      warnings.warn("distance_units required", DeprecationWarning)

- We can see the errors are reported on `stderr`
- `warnings` has some downsides
  - Had to add boilerplate
  - Had to modify the default argument behaviour to make it easy to
    identify when args weren’t supplied
    - Makes it harder to identify default values through introspection
      tools
  - By default `warnings.warn` indicates the line where it was called
    - Often more interested in *where* the call was made
- `warnings.warn` provides a `stacklevel` parameter
  - Can report where in a stack a warning originated from
  - Can help reduce boilerplate
    - Enables functions to warn on behalf of other functions
- Define a helper function `requires`
  - Warns if an optional argument is not supplied
  - Then supplies a default value

``` python
import warnings


def require(name, value, default):
    if value is not None:
        return value
    warnings.warn(
        f"{name} will be required soon, update your code",
        DeprecationWarning,
        stacklevel=3,
    )
    return default


CONVERSIONS = {
    "mph": 1.60934 / 3600 * 1000,  # m/s
    "hours": 3600,  # seconds
    "miles": 1.60934 * 1000,  # m
    "meters": 1,  # m
    "m/s": 1,  # m/s
    "seconds": 1,
}


def convert(value, units):
    rate = CONVERSIONS[units]
    return rate * value


def localise(value, units):
    rate = CONVERSIONS[units]
    return value / rate


def print_distance(
    speed, duration, *, speed_units=None, time_units=None, distance_units=None
):
    speed_units = require("speed_units", speed_units, "mph")
    time_units = require("time_units", time_units, "hours")
    distance_units = require("distance_units", distance_units, "miles")

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localise(norm_distance, distance_units)
    print(f"{distance} {distance_units}")


# old-style call
print_distance(5, 2.5)
```

    12.5 miles

    /tmp/ipykernel_14475/4080730032.py:50: DeprecationWarning: speed_units will be required soon, update your code
      print_distance(5, 2.5)
    /tmp/ipykernel_14475/4080730032.py:50: DeprecationWarning: time_units will be required soon, update your code
      print_distance(5, 2.5)
    /tmp/ipykernel_14475/4080730032.py:50: DeprecationWarning: distance_units will be required soon, update your code
      print_distance(5, 2.5)

- Can configure how to handle raised warnings, e.g.
  - Might want to treat warnings as errors
  - Warnings are converted to exceptions

``` python
import warnings

# treat warnings as errors
warnings.simplefilter("error")
try:
    warnings.warn("This usage is deprecated", DeprecationWarning)
except DeprecationWarning as e:
    print(f"Caught {e!r}")
```

    Caught DeprecationWarning('This usage is deprecated')

- Useful for testing
  - Enables detection of incoming warnings from upstream dependencies
- Can also apply at the command line level via the `-W` flag

``` shell
$ uv run python3.14 -W error warning_test.py
  File ".../EffectivePython/Chapter_14/Item_123/Example/warning_test.py", line 5, in <module>
    warnings.warn("This usage is no longer supported", DeprecationWarning)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
DeprecationWarning: This usage is no longer supported
```

- You can ignore warnings / errors via the `"ignore"` argument to
  `simplefilter`
  - E.g. once you’ve acknowledged a need to migrate
  - Or more selectively via `filterwarnings` ([Read the
    docs](https://docs.python.org/3/library/warnings.html))

``` python
import warnings

warnings.simplefilter("ignore")
warnings.warn("This will not be reported")
print("This will be")
```

    This will be

- In production, generally don’t want warnings to produce errors
  - They should be triaged during development
  - Don’t want upstream dependencies warnings to break or crash a
    program
- Instead, a better technique is to forward them to `logging`
  - Can do so via the `logging.captureWarnings` function
  - Then configure the `py.warnings` logger

``` python
import sys
import logging
import warnings

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter("(asctime)-15s WARNING] %(message)s")
handler.setFormatter(formatter)

logging.captureWarnings(True)
logger = logging.getLogger("py.warnings")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

warnings.resetwarnings()
warnings.simplefilter("default")
warnings.warn("This will go to the logs output")
```

    (asctime)-15s WARNING] /tmp/ipykernel_14475/3033121806.py:16: UserWarning: This will go to the logs output
      warnings.warn("This will go to the logs output")

- Syncing `warnings` to `logging` ensures that we don’t run two parallel
  error-reporting streams
  - Help’s catch issues not found in testing
  - Not an excuse to avoid writing tests
- Warnings should be unit tested
  - Ensure they are properly triggered (See [Item
    108](../../Chapter_13/Item_108/item_108.qmd))
  - Can use `warnings.catch_warnings` as a context manager to aid
    testing (See [Item 82](../../Chapter_10/Item_082/item_082.qmd))
    - Can be used to count the number of warnings encountered
    - Iterate over and check warnings match expected output

``` python
import warnings


def require(name, value, default):
    if value is not None:
        return value
    warnings.warn(
        f"{name} will be required soon, update your code",
        DeprecationWarning,
        stacklevel=3,
    )
    return default


# Simple test of `require`
with warnings.catch_warnings(record=True) as found_warnings:
    found = require("my_arg", None, "fake_units")
    expected = "fake_units"
    assert found == expected

assert len(found_warnings) == 1
single_warning = found_warnings[0]
assert str(single_warning.message) == (
    "my_arg will be required soon, update your code"
)
assert single_warning.category == DeprecationWarning

print("`require` passed all tests")
```

    `require` passed all tests

## Things to Remember

- `warnings` module can be used to notify API callers about deprecated
  usage
  - Encourages users to fix code before API changes are made permanent
    and breaking
- Raise warnings as errors via the `-W error` command line option or
  `warnings.simplefilter("error")` in code call
  - Useful for regression testing of dependencies in automated test
    frameworks
- Replicate warnings in production into the `logging` module
  - Ensures existing error-reporting systems capture warnings at runtime
- Write tests for warnings you generate to ensure they display the
  correct behaviour
  - i.e. Triggered at the right time when consumed
