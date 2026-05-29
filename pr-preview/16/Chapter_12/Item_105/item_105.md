# Item 105 Use `datetime` Instead of `time` for Local Clocks


- [Notes](#notes)
  - [The `time` Module](#the-time-module)
  - [The `datetime` Module](#the-datetime-module)
- [Things to Remember](#things-to-remember)

## Notes

- Computers represent time through *Coordinated Universal Time* (UTC)
  - time-zone independent
- Converting between computer time-representation and a human
  understandable time is non-trivial
  - Need to consider the format e.g. hours, minutes, seconds etc.
  - time zones
- Python has two modules for time conversions
  1.  `time`
      - Old module using C conventions
  2.  `datetime`
      - More ergonomic
      - Works well with the `zoneinfo` built-in module

### The `time` Module

- `localtime` converts UNIX timestamp to local time
  - Matching host computer’s time-zone
- `strftime` is a function for formatting and presenting a time
  - Let’s us display a local time in human readable format

``` python
import time

now = 1710047865.0
local_tuple = time.localtime(now)

time_format = "%Y-%m-%d %H:%M:%S"
time_str = time.strftime(time_format, local_tuple)
print(time_str)
```

    2024-03-10 05:17:45

- Often need to convert in reverse
  - i.e. human-readable string to UTC time
- `strptime` parses a time string to a local time
- `mktime` converts a local time to a UNIX timestamp

``` python
import time

time_format = "%Y-%m-%d %H:%M:%S"
time_str = "2024-03-09 21:17:45"
time_tuple = time.strptime(time_str, time_format)
utc_now = time.mktime(time_tuple)
print(utc_now)
```

    1710019065.0

- Converting between time zones requires some effort
  - Avoid directly manipulating the `time`, `localtime`, `strftime`
    objects
  - Time zones change often
    - e.g. daylight savings
- Operating systems normally supply config files that automatically
  track time zone updates
  - `time` module can access them if available
- Windows has a more limited set of time functionality available
- For example, parsing San Franciso Time

``` python
import time

time_format = "%Y-%m-%d %H:%M:%S"
parse_format = "%Y-%m-%d %H:%M:%S %Z"
depart_sfo = "2024-03-09 21:17:45 PST"

time_tuple = time.strptime(depart_sfo, parse_format)
time_str = time.strftime(time_format, time_tuple)
print(time_str)
```

    ValueError: time data '2024-03-09 21:17:45 PST' does not match format '%Y-%m-%d %H:%M:%S %Z'
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[3], line 7
          4 parse_format = "%Y-%m-%d %H:%M:%S %Z"
          5 depart_sfo = "2024-03-09 21:17:45 PST"
    ----> 7 time_tuple = time.strptime(depart_sfo, parse_format)
          8 time_str = time.strftime(time_format, time_tuple)
          9 print(time_str)

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/_strptime.py:783, in _strptime_time(data_string, format)
        780 def _strptime_time(data_string, format="%a %b %d %H:%M:%S %Y"):
        781     """Return a time struct based on the input string and the
        782     format string."""
    --> 783     tt = _strptime(data_string, format)[0]
        784     return time.struct_time(tt[:time._STRUCT_TM_ITEMS])

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/_strptime.py:555, in _strptime(data_string, format)
        553 found = format_regex.match(data_string)
        554 if not found:
    --> 555     raise ValueError("time data %r does not match format %r" %
        556                      (data_string, format))
        557 if len(data_string) != found.end():
        558     raise ValueError("unconverted data remains: %s" %
        559                       data_string[found.end():])

    ValueError: time data '2024-03-09 21:17:45 PST' does not match format '%Y-%m-%d %H:%M:%S %Z'

- For me this throws an error that the time data does not match the
  format
  - Because `time` is platform-dependent
  - Relies on the underlying C implementation
- Since `time` is unreliable, avoid using it for converting local times
  - Only for between UTC and host local time

### The `datetime` Module

- Another built-in module like python
- Provides the `datetime` object for handling dates and times
- Can convert between UTC and host local as per `time`

``` python
from datetime import datetime, timezone

now = datetime(2024, 3, 10, 5, 17, 45)
now_utc = now.replace(tzinfo=timezone.utc)
now_local = now_utc.astimezone()
print(now_local)
```

    2024-03-10 05:17:45+00:00

- Can convert in reverse (i.e. local to UTC)

``` python
from datetime import datetime, timezone
import time

time_format = "%Y-%m-%d %H:%M:%S"
time_str = "2024-03-09 21:17:45"

now = datetime.strptime(time_str, time_format)
time_tuple = now.timetuple()
utc_now = time.mktime(time_tuple)
print(utc_now)
```

    1710019065.0

- `datetime` provides functionality for timezone conversion
  - Uses the `tzinfo` class
- Since Python 3.9 `zoneinfo` built-in module contains a time zone
  database
  - On Windows might instead need the `tzdata` community package
    - It’s officially endorsed
- Rather than convert between timezones, always better to go via UTC
  intermediate
  - Perform operations on the UTC intermediate, e.g. offsets
- For example, converting a NYC flight time to UTC
  - Then converting to San Francisco time

``` python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time


time_format = "%Y-%m-%d %H:%M:%S"

arrival_nyc = "2024-03-10 03:31:18"
nyc_dt_naive = datetime.strptime(arrival_nyc, time_format)
eastern = ZoneInfo("US/Eastern")
nyc_dt = nyc_dt_naive.replace(tzinfo=eastern)

# Converting to UTC

utc_dt = nyc_dt.astimezone(timezone.utc)
print("EDT:", nyc_dt)
print("UTC", utc_dt)

# Converting to San Fran
pacific = ZoneInfo("US/Pacific")
sf_dt = utc_dt.astimezone(pacific)
print("PST:", sf_dt)

# And to Nepal
nepal = ZoneInfo("Asia/Katmandu")
nepal_dt = utc_dt.astimezone(nepal)
print("Nepal:", nepal_dt)
```

    EDT: 2024-03-10 03:31:18-04:00
    UTC 2024-03-10 07:31:18+00:00
    PST: 2024-03-09 23:31:18-08:00
    Nepal: 2024-03-10 13:16:18+05:45

- `datetime` and `zoneinfo` makes time zone conversions consistent and
  reliable across operating systems

## Things to Remember

- Avoid using the `time` module for translating between time zones
- Use `datetime` and `zoneinfo` built-in modules to convert between
  dates and times in different time zones
- Always convert first to UTC before converting to another time zone
  - Perform any operations on the UTC intermediate
