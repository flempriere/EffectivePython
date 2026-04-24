# Item 27: Prefer `defaultdict` over `setdefault` to Handle Missing

Items in Internal State

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- We’ve seen that in general `get` is preferable to `setdefault` ([Item
  26](../Item_026/item_026.qmd))
- However, we’ve seen that `get` isn’t the cleanest interface when the
  type stored in the dictionary is complex
- For example,
  - Let’s keep track of cities, visited in countries around the world

``` python
visits = {
    "Mexico": {"Tulum", "Puerto Vallarta"},
    "Japan": {"Hakone"}
}
```

- Here `setdefault` let’s us add new cities regardless of if the country
  key exists

``` python
visits = {"Mexico": {"Tulum", "Puerto Vallarta"}, "Japan": {"Hakone"}}

#Short
visits.setdefault("France", set()).add("Arles")

#Long
if (japan := visits.get("Japan")) is None:
    visits["Japan"] = japan = set()

japan.add("Kyoto")
print(visits)
```

    {'Mexico': {'Puerto Vallarta', 'Tulum'}, 'Japan': {'Kyoto', 'Hakone'}, 'France': {'Arles'}}

- Here the `get` code is clearly longer and less clear
- One might be tempted to wrap the code above in a class to hide the
  complexity from the user

``` python
class Visits:
    def __init__(self):
        self.data = {}

    def add(self, country, city):
        city_set = self.data.setdefault(country, set())
        city_set.add(city)

visits = Visits()
visits.add("Russia", "Yekaterinburg")
visits.add("Tanzania", "Zanzibar")
print(visits.data)
```

    {'Russia': {'Yekaterinburg'}, 'Tanzania': {'Zanzibar'}}

- This hides the `setdefault` call
- `add` provides a clean interface and more meaningful interface
- There are still downsides
  - The complexity is still present in the internals of the `add` method
  - `setdefault` constructs a `set` object on every call (even if it
    isn’t assigned in the end)
- `defaultdict` simplifies this use case
  - Provided in the `collections` built-in module
  - Accepts a function that returns a default value whenever a key is
    missing
- We can rewrite our `Visits` class as before

``` python
from collections import defaultdict


class Visits:
    def __init__(self):
        self.data = defaultdict(set)

    def add(self, country, city):
        self.data[country].add(city)


visits = Visits()
visits.add("Russia", "Yekaterinburg")
visits.add("Tanzania", "Zanzibar")
print(visits.data)
```

    defaultdict(<class 'set'>, {'Russia': {'Yekaterinburg'}, 'Tanzania': {'Zanzibar'}})

- `add` is now succinct
- Code can assume that accessing any key in the data will return a `set`
  instance
- Only allocates a `set` when required
- Using `defaultdict` is better than using `setdefault`
  - `defaultdict` doesn’t solve every problem, but it is useful to know
    about

## Things to Remember

- If creating a dictionary to manage an arbitrary set of potential keys
  prefer a `defaultdict` instance from `collections` if you need complex
  types as default values
- If a dictionary of arbitrary keys is passed to you (i.e. you don’t
  control it’s creation), then prefer `get`
  - Consider `setdefault` if it leads to shorter code and the default
    objection allocation cost is low
