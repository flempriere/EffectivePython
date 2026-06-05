# Item 112: Encapsulate Dependencies to Faciliate Mocking and Testing


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- We’ve seen how to use `unittest.mock` to simulate complex dependencies
  (See [Item 111](../Item_111/item_111.qmd))
  - Mocking code required a lot of boilerplate
  - Obfuscates the actual behaviour under test
- Better to encapsulate primitives like database connections in
  interface objects
  - Avoids passing the raw database connection into functions
- Better abstractions help facilitate mocking and testing
  - If a program is hard to test, probably good evidence it needs a
    refactor (See [Item 123](../../Chapter_14/Item_123/item_123.qmd))
- Our new `ZooDatabase` object might look like below
  - Can then be directly injected into `do_rounds`

``` python
from datetime import datetime


class ZooDatabase:
    def get_animals(self, species):
        return []

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1

    return fed


print(f"Fed {do_rounds(database=ZooDatabase(), species='Meerkat')}")
```

    Fed 0

- Now rather than having to mock out three distinct functions, we can
  mock *one* object
- `Mock`’s modelling classes will also provide a `Mock` object for each
  underlying attribute or method accessed
  - Can set expected values and verify calls
  - Makes it much cleaner to separate setting up a `Mock` from the
    object being tested

``` python
from datetime import datetime
from unittest.mock import Mock


class ZooDatabase:
    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1

    return fed


# testing

database = Mock(spec=ZooDatabase)
print(database.feed_animal)
database.feed_animal()
database.feed_animal.assert_any_call()
print("Mock passed all testes")
```

    <Mock name='mock.feed_animal' id='139673154387456'>
    Mock passed all testes

- Implementing the full mock code

``` python
from datetime import datetime, timedelta
from unittest.mock import Mock, call


class ZooDatabase:
    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1
    return fed


# Testing code

now_func = Mock(spec=datetime.now)
now_func.return_value = datetime(2019, 6, 5, 15, 45)

database = Mock(spec=ZooDatabase)
database.get_food_period.return_value = timedelta(hours=3)
database.get_animals.return_value = [
    ("Spot", datetime(2019, 6, 5, 11, 15)),
    ("Fluffy", datetime(2019, 6, 5, 12, 30)),
    ("Jojo", datetime(2019, 6, 5, 12, 55)),
]

result = do_rounds(database, "Meerkat", now_func=now_func)
print(result)
assert result == 2

database.get_food_period.assert_called_once_with("Meerkat")
database.get_animals.assert_called_once_with("Meerkat")
database.feed_animal.assert_has_calls(
    [
        call("Spot", now_func.return_value),
        call("Fluffy", now_func.return_value),
    ],
    any_order=True,
)
print("All mocked tests passed")
```

    2
    All mocked tests passed

- Always use the `spec` parameter so the `Mock` maps to the underlying
  class
  - Avoids duplicating difficult to spot errors like typos in function
    calls in the caller code and the test
- If writing an end-to-end integration test (See [Item
  109](../Item_109/item_109.qmd)) still need to inject a mock
  - Use helper functions that act as *seams* to control dependency
    injection
- For example, cache a module scope `ZooDatabase` object (See [Item
  120](../../Chapter_14/Item_120/item_120.qmd))
- Can then use `patch` to inject the mock

``` python
import contextlib
from datetime import datetime, timedelta
import io
from unittest.mock import Mock, patch


# Interface code
class ZooDatabase:
    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1

    return fed


# End to end code

DATABASE = None


def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = ZooDatabase()
    return DATABASE


def main(argv):
    database = get_database()
    species = argv[1]
    count = do_rounds(database, species)
    print(f"Fed {count} {species}(s)")
    return 0


# end to end test
with patch("__main__.DATABASE", spec=ZooDatabase):
    now = datetime.now()  # using offset based testing

    DATABASE.get_food_period.return_value = timedelta(hours=3)
    DATABASE.get_animals.return_value = [
        ("Spot", now - timedelta(hours=4.5)),
        ("Fluffy", now - timedelta(hours=3.25)),
        ("Jojo", now - timedelta(hours=2.5)),
    ]

    fake_stdout = io.StringIO()
    with contextlib.redirect_stdout(fake_stdout):
        main(["program name", "Meerkat"])

    found = fake_stdout.getvalue()
    print(found)
    expected = "Fed 2 Meerkat(s)\n"

    assert found == expected
print("End to End Test passed!")
```

    Fed 2 Meerkat(s)

    End to End Test passed!

- Here we define our test times to be relative to the current time
  - In theory more brittle, but also test’s more of the actual code
    surface area
- Observe doing the integration test is straightforward because we have
  designed a test friendly interface

## Things to Remember

- Avoid lots of repeated boilerplate in setting up mocks by
  encapsulating dependencies into classes
- `Mock` from `unittest.mock` simulates classes by returning a mock
  which behaves like a mocked method for every accessed attribute
  - Class `Mock` objects should use the `spec` keyword to ensure they
    match the correct interface
- For end to end tests it is useful to refactor code to have helper
  functions that act as seams for dependency injection
  - Act as points at which mocks can be injected for testing
