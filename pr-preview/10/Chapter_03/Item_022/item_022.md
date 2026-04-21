# Item 22: Never Modify Containers While Iterating over Them; Use Copies
or Caches Instead


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Modifying containers while iterating over them can lead to many
  gotchas
- For example, adding a key to a dictionary while iterating will raise a
  runtime error

``` python
search_key = "red"

my_dict = {"red": 1, "blue": 2, "green": 3}
for key in my_dict:
    if key == "blue":
        my_dict["yellow"] = 4
print(my_dict)
```

    RuntimeError: dictionary changed size during iteration
    ---------------------------------------------------------------------------
    RuntimeError                              Traceback (most recent call last)
    Cell In[1], line 4
          1 search_key = "red"
          3 my_dict = {"red": 1, "blue": 2, "green": 3}
    ----> 4 for key in my_dict:
          5     if key == "blue":
          6         my_dict["yellow"] = 4

    RuntimeError: dictionary changed size during iteration

- Similar thing happens if we call delete

``` python
search_key = "red"

my_dict = {"red": 1, "blue": 2, "green": 3}
for key in my_dict:
    if key == search_key:
        del my_dict[search_key]
print(my_dict)
```

    RuntimeError: dictionary changed size during iteration
    ---------------------------------------------------------------------------
    RuntimeError                              Traceback (most recent call last)
    Cell In[2], line 4
          1 search_key = "red"
          3 my_dict = {"red": 1, "blue": 2, "green": 3}
    ----> 4 for key in my_dict:
          5     if key == search_key:
          6         del my_dict[search_key]

    RuntimeError: dictionary changed size during iteration

- You can modify the values associated with a key
  - Just cannot modify the set of keys

``` python
search_key = "red"

my_dict = {"red": 1, "blue": 2, "green": 3}
for key in my_dict:
    if key == search_key:
        my_dict[search_key] = 4

print(my_dict)
```

    {'red': 4, 'blue': 2, 'green': 3}

- A similar issue is seen with changing the size of a python `set`
  - But only if we add a new item
  - Attempting to add an existing item won’t cause an error
    - Because the size doesn’t change

``` python
search_key = "red"
my_set = {"red", "green", "blue"}

# modifying existing element
for colour in my_set:
    if colour == search_key:
        my_set.add("green")
print(my_set)

# adding new element
for colour in my_set:
    if colour == search_key:
        my_set.add("yellow")
print(my_set)
```

    {'green', 'red', 'blue'}

    RuntimeError: Set changed size during iteration
    ---------------------------------------------------------------------------
    RuntimeError                              Traceback (most recent call last)
    Cell In[4], line 11
          8 print(my_set)
         10 # adding new element
    ---> 11 for colour in my_set:
         12     if colour == search_key:
         13         my_set.add("yellow")

    RuntimeError: Set changed size during iteration

- Lists also have odd behaviour
  - Can overwrite indices during iteration

``` python
my_list = [1, 2, 3]

for number in my_list:
    print(number)
    if number == 2:
        my_list[0] = -1 #okay
print(my_list)
```

    1
    2
    3
    [-1, 2, 3]

- But inserting *before* the current iterator position causes the
  program to loop
  - Be careful running the cell below

``` python
my_list = [1, 2, 3]

for number in my_list:
    print(number)
    if number == 2:
        my_list.insert(0, 4)  # causes an infinite loop (insert 4 at position 0)

print(my_list)
```

- Appending to a list at a position *after* the current iterator is not
  a problem

``` python
my_list = [1, 2, 3]

for number in my_list:
    print(number)
    if number == 2:
        my_list.append(4)  # okay

print(my_list)
```

    1
    2
    3
    4
    [1, 2, 3, 4]

- End result is that it’s hard to codify a set of rules for when it’s
  safe to modify a container while looping
  - Best approach is therefore to avoid doing it at all
  - Especially when dealing with more complex algorithms rather than
    linear traversal where the access my be more esoteric
- If you need to modify a container by iterating over it’s contents
  - Make a copy, iterate over the copy
  - Modify the original
- For example,

``` python
# Copying and modifying a dictionary

search_key = "red"
my_dict = {"red": 1, "blue": 2, "green": 3}

keys_copy = list(my_dict.keys())  # copy original dict keys
for key in keys_copy:  # loop over the copy
    if key == search_key:
        my_dict["green"] = 4  # modify the original
print(my_dict)

# Copying and modifying a list
my_list = [1, 2, 3]

list_copy = list(my_list)
for number in list_copy:
    print(number)
    if number == 2:
        my_list.insert(0, 4)  # okay
print(my_list)

# copy and modifying a set
my_set = {"red", "blue", "green"}
set_copy = set(my_set)
for colour in set_copy:
    if colour == search_key:
        my_set.add("yellow")
print(my_set)
```

    {'red': 1, 'blue': 2, 'green': 4}
    1
    2
    3
    [4, 1, 2, 3]
    {'red', 'blue', 'green', 'yellow'}

- Copying can be slow for large containers
- Alternative is to stage modifications in a container
- Then merge the changes into the main container post-iteration

``` python
search_key = "red"
my_dict = {"red": 1, "blue": 2, "green": 3}

modifications = {}

for key in my_dict:
    if key == search_key:
        modifications["green"] = 4  # add to staging

my_dict.update(modifications)
print(my_dict)
```

    {'red': 1, 'blue': 2, 'green': 4}

- Staging modifications has the aren’t immediately visible in the
  original container until the iteration ends
- Logic relying on the modifications being immediately visible is liable
  to break
- E.g. the following code might have expected `"yellow"` to be added
  during iteration

``` python
search_key = "red"
my_dict = {"red" : 1, "blue" : 2, "green" : 3}
modifications = {}

for key in my_dict:
    if key == search_key:
        modifications["green"] = 4
    value = my_dict[key]
    if value == 4: # never true because green is updated in the modifications dictionary, *not* the original
        modifications["yellow"] = 5

my_dict.update(modifications)
print(my_dict)
```

    {'red': 1, 'blue': 2, 'green': 4}

- Obvious solution is to check both containers
  - Modifications effectively acts as a cache

``` python
search_key = "red"
my_dict = {"red": 1, "blue": 2, "green": 3}
modifications = {}

for key in my_dict:
    if key == search_key:
        modifications["green"] = 4
    value = my_dict[key]
    other_value = modifications.get(key)  # check cache, missing key is None
    if (
        value == 4
    ):  # never true because green is updated in the modifications dictionary, *not* the original
        modifications["yellow"] = 5

my_dict.update(modifications)
print(my_dict)
```

    {'red': 1, 'blue': 2, 'green': 4}

- Hard to generalise this solution
  - Need to ensure that the cache respects the constraints of the
    algorithm
- Best enforced with automated tests

## Things to Remember

- Adding or removing elements from a container while iterating can cause
  run time errors or infinite loops
- You can iterate over a copy to avoid these runtime errors
- If you need to avoid copying
  - Stage modifications in a secondary container
  - Post-iteration merge these with the original
  - This can require careful design to ensure the algorithm is still
    correct
