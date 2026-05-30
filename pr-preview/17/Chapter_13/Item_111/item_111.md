# Item 111: Use Mocks to Test Code with Complex Dependencies


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Mocks are used to simulate behaviours in tests (See [Item
  108](../Item_108/item_108.qmd)) when using the actual function or
  class would be to difficult or slow to use directly
- For this example we’ll consider a program to record the feeding
  schedule for a zoo
  - The real data for this is stored in a database
  - We might then query a database for animals of a certain species and
    when they ate

``` python
# Database connection model
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


database = DatabaseConnection("localhost", "4444")
get_animals(database, "Meerkat")
```

    DatabaseConnectionError: Not Connected
    ---------------------------------------------------------------------------
    DatabaseConnectionError                   Traceback (most recent call last)
    Cell In[1], line 21
         17     raise DatabaseConnectionError("Not Connected")
         20 database = DatabaseConnection("localhost", "4444")
    ---> 21 get_animals(database, "Meerkat")

    Cell In[1], line 17, in get_animals(database, species)
         12 def get_animals(database, species):
         13     """Query the database
         14 
         15     Return a list of (name, last_mealtime) tuples
         16     """
    ---> 17     raise DatabaseConnectionError("Not Connected")

    DatabaseConnectionError: Not Connected

- The above fails because we don’t actually have a database running
- So how we to actually use one in tests?
  - If we were doing a *systems test* we might have an actual test
    database that we connect to
- For an *integration* or *unit* test this is extreme overkill
  - Plus has an overhead for running the tests which makes them harder
    to maintain (See [Item 110](../Item_110/item_110.qmd))
- Alternatively we should consider *mocking* the database
  - A *mock* acts like an object
  - Let’s us provide expected responses for behaviour calls
- A *mock* is distinct from a *fake*
  - A *fake* is a simpler implementation providing most functionality
    - e.g. An in-memory simple database
  - A *mock* simulates the responses of an object
- `unittest` provides the `unittest.mock` module for testing with mocks
  - A `Mock` is a class-based implementation of a mock
    - Constructor takes a `spec` keyword which provides the object to
      simulate
    - Here we pass the function `get_animals`
    - A mock will error if used in a way that is incompatible with the
      spec
      - See below
- We can create a mock that simulates the `get_animals` function

``` python
from datetime import datetime
from unittest.mock import Mock


# Function definitions
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


# Testing implementation

mock = Mock(spec=get_animals)
expected = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]

mock.return_value = expected

# Using a mock in a way incompatible with the spec
mock.attribute_that_does_not_exist
```

    AttributeError: Mock object has no attribute 'attribute_that_does_not_exist'
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[2], line 36
         33 mock.return_value = expected
         35 # Using a mock in a way incompatible with the spec
    ---> 36 mock.attribute_that_does_not_exist

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:697, in NonCallableMock.__getattr__(self, name)
        695 elif self._mock_methods is not None:
        696     if name not in self._mock_methods or name in _all_magics:
    --> 697         raise AttributeError("Mock object has no attribute %r" % name)
        698 elif _is_magic(name):
        699     raise AttributeError(name)

    AttributeError: Mock object has no attribute 'attribute_that_does_not_exist'

- The `.return_value` attribute on a `Mock` indicates what should
  returned when the `Mock` is called

``` python
from datetime import datetime
from unittest.mock import Mock


# Function definitions
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


# Testing implementation

mock = Mock(spec=get_animals)
expected = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]

mock.return_value = expected

# Simulate the `get_animals` function
database = object()
result = mock(database, "Meerkat")
assert result == expected
print("Result matched expectations")
```

    Result matched expectations

- `database` above is an `object` since we don’t use it’s behaviour
  - Just need to match the interface
- Can then check that the returned result matches expectations
- What happens if we want to verify that a mock was called with the
  correct arguments?
  - Can use the `assert_called_once_with()` method
  - Verifies a method is called *once* with the supplied parameters
- If only care about some parameters, can use `unittest.mock.ANY` to
  accept any value
  - For example, might only care that we use the *correct* database

``` python
from datetime import datetime
from unittest.mock import Mock, ANY


# Function definitions
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


# Testing implementation

mock = Mock(spec=get_animals)
expected = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]

mock.return_value = expected

# Simulate the `get_animals` function, this time verifying call
database = object()
result = mock(database, "Meerkat")
mock.assert_called_once_with(database, "Meerkat")
print("Supplied correct parameters - Passed")

# Simulate only checking mock calls the right database
print("Simulating only checking the database parameter")
mock3 = Mock(spec=get_animals)
result = mock3(database, "Eagle")
mock3.assert_called_once_with(database, ANY)
print("Supplied correct database - Passed")

# Simulate incorrect parameter
print("Passing incorrect parameters...")
mock2 = Mock(spec=get_animals)
result = mock2(database, "Eagle")
mock2.assert_called_once_with(database, "Meerkat")
```

    Supplied correct parameters - Passed
    Simulating only checking the database parameter
    Supplied correct database - Passed
    Passing incorrect parameters...

    AssertionError: expected call not found.
    Expected: mock(<object object at 0x7fad74b41860>, 'Meerkat')
      Actual: mock(<object object at 0x7fad74b41860>, 'Eagle')
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[4], line 52
         50 mock2 = Mock(spec=get_animals)
         51 result = mock2(database, "Eagle")
    ---> 52 mock2.assert_called_once_with(database, "Meerkat")

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:998, in NonCallableMock.assert_called_once_with(self, *args, **kwargs)
        993     msg = ("Expected '%s' to be called once. Called %s times.%s"
        994            % (self._mock_name or 'mock',
        995               self.call_count,
        996               self._calls_repr()))
        997     raise AssertionError(msg)
    --> 998 return self.assert_called_with(*args, **kwargs)

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:986, in NonCallableMock.assert_called_with(self, *args, **kwargs)
        984 if actual != expected:
        985     cause = expected if isinstance(expected, Exception) else None
    --> 986     raise AssertionError(_error_message()) from cause

    AssertionError: expected call not found.
    Expected: mock(<object object at 0x7fad74b41860>, 'Meerkat')
      Actual: mock(<object object at 0x7fad74b41860>, 'Eagle')

- `ANY` useful when a parameter is not critical to the behaviour being
  tested
  - Prefer under-specifying tests with `ANY`
  - Makes them easier to use and less brittle
- `Mock` can be used to model exceptions
  - Use the `side_effect` method

``` python
from unittest.mock import Mock


class MyError(Exception):
    pass


# Function definitions
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


# Raises an exception
mock = Mock(spec=get_animals)
mock.side_effect = MyError("Whoops! Big Problem")
result = mock(database, "Meerkat")
```

    MyError: Whoops! Big Problem
    ---------------------------------------------------------------------------
    MyError                                   Traceback (most recent call last)
    Cell In[5], line 30
         28 mock = Mock(spec=get_animals)
         29 mock.side_effect = MyError("Whoops! Big Problem")
    ---> 30 result = mock(database, "Meerkat")

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1176, in CallableMixin.__call__(self, *args, **kwargs)
       1174 self._mock_check_sig(*args, **kwargs)
       1175 self._increment_mock_call(*args, **kwargs)
    -> 1176 return self._mock_call(*args, **kwargs)

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1180, in CallableMixin._mock_call(self, *args, **kwargs)
       1179 def _mock_call(self, /, *args, **kwargs):
    -> 1180     return self._execute_mock_call(*args, **kwargs)

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1241, in CallableMixin._execute_mock_call(self, *args, **kwargs)
       1239 if effect is not None:
       1240     if _is_exception(effect):
    -> 1241         raise effect
       1242     elif not _callable(effect):
       1243         result = next(effect)

    MyError: Whoops! Big Problem

- The mocking module has a lot of functionality
  - Best place to start is the
    [docs](https://docs.python.org/3/library/unittest.mock.html)
- How to use `Mock` in testing?
  - We’ll build up tests for our zoo framework
  - First need some methods to handle feeding animals

``` python
from datetime import datetime
from unittest.mock import Mock


class MyError(Exception):
    pass


# Basic database functions


class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


# Database queries


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    return []


def get_food_period(database, species):
    """Query database

    Returns
    -------
    datetime.timedelta
    """
    pass


def feed_animal(database, name, when):
    """Write to database"""
    pass


def do_rounds(database, species):
    now = datetime.now()
    feeding_timedelta = get_food_period(database, species)
    animals = get_animals(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_animal(database, name, now)
            fed += 1
    return fed


print("Fed:", do_rounds(database=object(), species="Meerkat"))
```

    Fed: 0

- Want to write tests for `do_rounds` to verify
  1.  The correct animals are fed when called
  2.  Latest feeding time recorded to database
  3.  Total number fed is accurate
- Need to mock out:
  1.  `datetime.now` to provide a stable time
      - Otherwise tests will drift
  2.  `get_food_period` and `get_animals`
      - Avoid the explicit database calls
- Need to be able to *inject* the mock into the `do_rounds` function
  - Since these calls are hardcoded in the internals
- Could refactor the class itself to accept all the function calls as
  parameters like kwargs (See [Item
  37](../../Chapter_05/Item_037/item_037.qmd))
  - Can then create the `Mock` instances upfront and set their expected
    values
- Can then check the mocks to validate the test
  - `call` let’s you verify that a `Mock` has received a certain
    function call

``` python
from datetime import datetime, timedelta
from unittest.mock import Mock, call


class MyError(Exception):
    pass


# Basic database functions


class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


# Database queries


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    return []


def get_food_period(database, species):
    """Query database

    Returns
    -------
    datetime.timedelta
    """
    pass


def feed_animal(database, name, when):
    """Write to database"""
    pass


def do_rounds(
    database,
    species,
    *,
    now_func=datetime.now,
    food_func=get_food_period,
    animals_func=get_animals,
    feed_func=feed_animal,
):
    now = now_func()
    feeding_timedelta = food_func(database, species)
    animals = animals_func(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_func(database, name, now)
            fed += 1
    return fed


# Test code

now_func = Mock(spec=datetime.now)
now_func.return_value = datetime(2024, 6, 5, 15, 45)

food_func = Mock(spec=get_food_period)
food_func.return_value = timedelta(hours=3)

animals_func = Mock(spec=get_animals)
animals_func.return_value = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]

feed_func = Mock(spec=feed_animal)

database = object()
# do the test on the mock
result = do_rounds(
    database,
    "Meerkat",
    now_func=now_func,
    food_func=food_func,
    animals_func=animals_func,
    feed_func=feed_func,
)
assert result == 2
print("Number fed matched expecations")

food_func.assert_called_once_with(database, "Meerkat")
print("Food function called once with the correct arguments")

animals_func.assert_called_once_with(database, "Meerkat")
print("Animals function called once with the correct arguments")

feed_func.assert_has_calls(
    [
        call(database, "Spot", now_func.return_value),
        call(database, "Fluffy", now_func.return_value),
    ],
    any_order=True,  # We just care that the calls occured, not the ordering
)
print("Feed function calls match expectations")
```

    Number fed matched expecations
    Food function called once with the correct arguments
    Animals function called once with the correct arguments
    Feed function calls match expectations

- We don’t verify the `datetime.now` mock, because that should be
  verified via the behaviour of the downstream mocks
  - Again integration test vs unit test (See [Item
    109](../Item_109/item_109.qmd))
- Keyword argument injection approach works
  - But verbose
  - Requires us to reconfigure the entire class interface to support
    mocking
  - Don’t likely need this level of dependency injection throughout the
    codebase
- Instead prefer `unittest.mock.patch`
  - Family of functions
  - Allows a temporary overwrite of a module or class attribute or
    function / method
    - Can be used to temporarily replace a function call with a `Mock`
- For example, we could patch `get_animals`

``` python
from unittest.mock import patch


class MyError(Exception):
    pass


# Function definitions
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    raise DatabaseConnectionError("Not Connected")


print("Outside patch:", get_animals)
with patch("__main__.get_animals"):
    print("Inside patch", get_animals)
print("After patch:", get_animals)
```

    Outside patch: <function get_animals at 0x7fad74986e50>
    Inside patch <MagicMock name='get_animals' id='140382968142480'>
    After patch: <function get_animals at 0x7fad74986e50>

- Doesn’t work for all functions
- e.g. If we try to `patch` `datetime.now` to inject a stable time
  - Fails since `datetime` class is defined via C extensions

``` python
from datetime import datetime
from unittest.mock import patch

fake_now = datetime(2024, 6, 5, 15, 45)

with patch("datetime.datetime.now"):
    datetime.now.return_value = fake_now
```

    TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1624, in _patch.__enter__(self)
       1623 try:
    -> 1624     setattr(self.target, self.attribute, new_attr)
       1625     if self.attribute_name is not None:

    TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'

    During handling of the above exception, another exception occurred:

    TypeError                                 Traceback (most recent call last)
    Cell In[9], line 6
          2 from unittest.mock import patch
          4 fake_now = datetime(2024, 6, 5, 15, 45)
    ----> 6 with patch("datetime.datetime.now"):
          7     datetime.now.return_value = fake_now

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1637, in _patch.__enter__(self)
       1635     return new
       1636 except:
    -> 1637     if not self.__exit__(*sys.exc_info()):
       1638         raise

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/unittest/mock.py:1646, in _patch.__exit__(self, *exc_info)
       1643     return
       1645 if self.is_local and self.temp_original is not DEFAULT:
    -> 1646     setattr(self.target, self.attribute, self.temp_original)
       1647 else:
       1648     delattr(self.target, self.attribute)

    TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'

- To fix, we can use a wrapper function
  - Then patch the wrapper

``` python
from datetime import datetime
from unittest.mock import patch

fake_now = datetime(2024, 6, 5, 15, 45)


# Unpatched function
def get_do_rounds_time():
    return datetime.now()


print("Now outside patch:", get_do_rounds_time())
with patch("__main__.get_do_rounds_time"):
    get_do_rounds_time.return_value = fake_now
    print("Now inside patch:", get_do_rounds_time())
print("Now back outside patch:", get_do_rounds_time())
```

    Now outside patch: 2026-05-30 11:44:56.298028
    Now inside patch: 2024-06-05 15:45:00
    Now back outside patch: 2026-05-30 11:44:56.298479

- Alternatively we might decide to use a keyword-only dependency
  injection for the time
  - Can then pass an explicit mock
  - Patch remaining functionality

``` python
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, DEFAULT, call


class MyError(Exception):
    pass


# Basic database functions


class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port


class DatabaseConnectionError(Exception):
    pass


# Database queries


def get_animals(database, species):
    """Query the database

    Return a list of (name, last_mealtime) tuples
    """
    return []


def get_food_period(database, species):
    """Query database

    Returns
    -------
    datetime.timedelta
    """
    pass


def feed_animal(database, name, when):
    """Write to database"""
    pass


def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = get_food_period(database, species)
    animals = get_animals(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_animal(database, name, now)
            fed += 1
    return fed


database = object()
with patch.multiple(
    "__main__",
    autospec=True,
    get_food_period=DEFAULT,
    get_animals=DEFAULT,
    feed_animal=DEFAULT,
):
    now_func = Mock(spec=datetime.now)
    now_func.return_value = datetime(2024, 6, 5, 15, 45)
    get_food_period.return_value = timedelta(hours=3)
    get_animals.return_value = [
        ("Spot", datetime(2024, 6, 5, 11, 15)),
        ("Fluffy", datetime(2024, 6, 5, 12, 30)),
        ("Jojo", datetime(2024, 6, 5, 12, 45)),
    ]

    result = do_rounds(database, "Meerkat", now_func=now_func)
    assert result == 2

    get_food_period.assert_called_once_with(database, "Meerkat")
    get_animals.assert_called_once_with(database, "Meerkat")
    feed_animal.assert_has_calls(
        [
            call(database, "Spot", now_func.return_value),
            call(database, "Fluffy", now_func.return_value),
        ],
        any_order=True,
    )
print("Test passed!")
```

    Test passed!

- The test passes
- Mocks are an effective mechanism for testing
  - But they add a lot of boilerplate to setting up the test
  - Make’s it harder to see the actual behaviour being tested
- Can improve readability by designing code that is testable by design
  (See [Item 112](../Item_112/item_112.qmd))
  - Can then support mocking easily if needed or not need mocking at all
- Code designed to be easily tested is often easily modifiable too

## Things to Remember

- `unittest.mock` provides `Mock` objects which can be used to simulate
  the behaviour of interfaces and complex objects
  - Useful in tests when it is difficult to set-up dependencies required
    by testing code
    - Or those dependencies are unstable (e.g. databases, timestamps
      etc.)
- Mocks enable verification of both the behaviour of code (via the
  expected return values) and that code calls dependent functions
  correctly
  - Use the `Mock.assert_called...` family of functions
- Keyword only arguments or `unittest.mock.patch` can be used to inject
  mocks into code under test
