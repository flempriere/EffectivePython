# Item 26: Prefer `get` over `in` and `KeyError` to Handle Missing
Dictionary Keys


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Dictionaries support three main operations on keys
  1.  Access
  2.  Assign
  3.  Delete
- Dictionary contents are dynamic
  - Common at runtime that a key may be absent when an attempt is made
    to access or delete it
- Consider a dictionary acting as a counter for people’s favourite bread
  type

``` python
bread_votes = {
    "pumpernickel" : 2,
    "sourdough" : 1,
}
```

- To increment the votes for a given bread type first need to check that
  the key exists
- Insert with default value of $0$ if missing
- Else increment by $1$

``` python
bread_votes = {
    "pumpernickel": 2,
    "sourdough": 1,
}

key = "wheat"

if key in bread_votes:
    count = bread_votes[key]
else:
    count = 0
bread_votes[key] = count + 1
print(bread_votes)
```

    {'pumpernickel': 2, 'sourdough': 1, 'wheat': 1}

- The key is accessed twice and assigned once
- Instead of explicitly checking, we can use the fact that dictionaries
  raise a `KeyError` when attempting to access a non-existent key

``` python
bread_votes = {
    "pumpernickel": 2,
    "sourdough": 1,
}

key = "wheat"

try:
    count = bread_votes[key]
except KeyError:
    count = 0

bread_votes[key] = count + 1
print(bread_votes)
```

    {'pumpernickel': 2, 'sourdough': 1, 'wheat': 1}

- In theory this is more efficient since we only do one key lookup
- However, what we’re really trying to do here is get the value
  associated with a key *or* a default value
  - `get` provides a clean dictionary method
  - By default the default value is `None`
- The `get` approach is not strictly more efficient than the exception
  handling method but it is a more encapsulated interface

``` python
bread_votes = {
    "pumpernickel": 2,
    "sourdough": 1,
}

key = "wheat"

count = bread_votes.get(key, 0)
bread_votes[key] = count + 1

print(bread_votes)
```

    {'pumpernickel': 2, 'sourdough': 1, 'wheat': 1}

> [!TIP]
>
> `Counter`
>
> If maintaining a dictionary of counters, consider using the `Counter`
> class from the `collections` built-in module. It should naturally
> support most the functionality that you need out of the box

- `get` works well for simple types, but how about more complex types?
  - e.g. If instead of a counter we tracked votes by a list of names

``` python
bread_voters = {
    "pumpernickel": ["Alice", "Bob"],
    "sourdough": ["Charlie"],
}

key = "wheat"
voter = "Danielle"

if key in bread_voters:
    names = bread_voters[key]
else:
    bread_voters[key] = names = []

names.append(voter)
print(bread_voters)
```

    {'pumpernickel': ['Alice', 'Bob'], 'sourdough': ['Charlie'], 'wheat': ['Danielle']}

- Again, using `in` requires two accesses to the key (if present)
  - One access and assignment if the key is not present
- The triple assignment `bread_voters[key] = names = []` populates the
  key in one step
  - Works because the list is stored as a reference not a value type
- We can also use the `KeyError` approach as before
  - This requires fewer key lookup’s (at the cost of the exception
    handling overhead)

``` python
bread_voters = {
    "pumpernickel": ["Alice", "Bob"],
    "sourdough": ["Charlie"],
}

key = "wheat"
voter = "Danielle"

try:
    names = bread_voters[key]
except KeyError
    bread_voters[key] = names = []

names.append(voter)
print(bread_voters)
```

    SyntaxError: expected ':' (2936407258.py, line 11)
      Cell In[6], line 11
        except KeyError
                       ^
    SyntaxError: expected ':'

- We could use `get` again
  - Combine with an assignment expression for brevity

``` python
bread_voters = {
    "pumpernickel": ["Alice", "Bob"],
    "sourdough": ["Charlie"],
}

key = "wheat"
voter = "Danielle"

if (names := bread_voters.get(key)) is None:
    bread_voters = names = []

names.append(voter)
print(bread_voters)
```

    ['Danielle']

- `dict` provides `setdefault` to reduce this boilerplate
  - `setdefault` acts like `get` in that it tries to fetch a key
  - *But* if the key isn’t present, rather than returning a default
    value it inserts that key with a default value
  - *Then* returns the value (original or default)
- We can reimplement the previous code as below

``` python
bread_voters = {
    "pumpernickel": ["Alice", "Bob"],
    "sourdough": ["Charlie"],
}

key = "wheat"
voter = "Danielle"

names = bread_voters.setdefault(key, [])

names.append(voter)
print(bread_voters)
```

    {'pumpernickel': ['Alice', 'Bob'], 'sourdough': ['Charlie'], 'wheat': ['Danielle']}

- This approach is shorter than before, but less readable
  - `setdefault` is not intuitively clear (called set, but returns a
    value)
- The default value is also assigned directly as opposed to copied
  - See below

``` python
data = {}
key = "foo"
value = []

data.setdefault(key, value)
print("Before:", data)
value.append("hello")
print("After:", data)
```

    Before: {'foo': []}
    After: {'foo': ['hello']}

- i.e. if we modify `value` that is propagated through to the dictionary
- Requires us to construct a new default value for each key
  - Leads to a performance cost
  - Have to allocate a new list every time
- We could also use `setdefault` for our original counter based approach

``` python
bread_votes = {
    "pumpernickel": 2,
    "sourdough": 1,
}

key = "wheat"

count = bread_votes.setdefault(key, 0)
bread_votes[key] = count + 1

print(bread_votes)
```

    {'pumpernickel': 2, 'sourdough': 1, 'wheat': 1}

- But the `setdefault` call is wasted
  - Since we immediately assign back to the key
  - So we’re just adding an extra layer of assignment
- `setdefault` is rarely the shortest way to handle missing key-values
  - One case is for `list` instance default values
  - They are cheap to construct and don’t raise exceptions
- However, the lack of clarity in the method name means it’s often
  preferable to use a `defaultDict`
  - A dictionary-type class that can have defined default value for
    missing keys

## Things to Remember

- There are four common ways to detect and handle missing keys
  1.  Using the `in` operator
  2.  `KeyError` exceptions
  3.  The `get`method,
  4.  The `setdefault` method
- The `get` method is best for dictionaries containing basic types
  - e.g. counters
  - Preferably use assignment operators
  - Useful when creating default values with a high cost or a risk of
    raising exceptions
- When the `setdefault` method seems appropriate, instead consider a
  `defaultdict` class
