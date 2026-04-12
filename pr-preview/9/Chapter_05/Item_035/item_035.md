# Item 35: Provide Optional Behaviour with Keyword Arguments


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python supports passing arguments by keyword
  - i.e writing the argument as `name=value`
- Keyword arguments and position arguments can be mixed and matched
  - But all positional arguments must *precede* the keyword arguments

``` python
def remainder(number, divisor):
    return number % divisor

# all valid calls
remainder(20, 7)
remainder(20, divisor=7)
remainder(number=20, divisor=7)
remainder(divisor=7, number=20)

# invalid call
remainder(number=20, 7)
```

    SyntaxError: positional argument follows keyword argument (4246727497.py, line 11)
      Cell In[1], line 11
        remainder(number=20, 7)
                              ^
    SyntaxError: positional argument follows keyword argument

- You can unpack a dictionary object into keyword arguments using the
  `**` operator

``` python
kwargs = {"number": 20, "divisor": 7}

assert(remainder(**kwargs) == 6)
```

    NameError: name 'remainder' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[2], line 3
          1 kwargs = {"number": 20, "divisor": 7}
    ----> 3 assert(remainder(**kwargs) == 6)

    NameError: name 'remainder' is not defined

- You can mix the unpacking operator with standard keyword definitions
  (so long as no key is included more than once)

``` python
kwargs = {"divisor": 7}

assert(remainder(number=20, **kwargs) == 6)
```

    NameError: name 'remainder' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[3], line 3
          1 kwargs = {"divisor": 7}
    ----> 3 assert(remainder(number=20, **kwargs) == 6)

    NameError: name 'remainder' is not defined

- You can also unpack multiple dictionaries using `**`
  - Dictionaries must have mutually exclusive keys

``` python
kwargs_1 = {"divisor": 7}
kwargs_2 = {"number": 20}

assert(remainder(**kwargs_1, **kwargs_2))
```

    NameError: name 'remainder' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[4], line 4
          1 kwargs_1 = {"divisor": 7}
          2 kwargs_2 = {"number": 20}
    ----> 4 assert(remainder(**kwargs_1, **kwargs_2))

    NameError: name 'remainder' is not defined

- Similarly to how `*args` lets a function accept a variable number of
  positional arguments, `**kwargs` lets you accept a variable number of
  keyword arguments
  - keyword arguments are packaged into a dictionary

``` python
def print_parameters(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

print_parameters(alpha=1.5, beta=9, gamma=4)
```

    alpha = 1.5
    beta = 9
    gamma = 4

- Keyword arguments provide a number of benefits
- Function call is clearer as each parameter is labelled explicitly
- Keyword arguments can have default values
  - E.g. consider the below code to calculate fluid flow into a
    container

``` python
def flow_rate(weight_diff, time_diff):
    return weight_diff / time_diff

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a
flow = flow_rate(weight_diff, time_diff)
print(f"{flow:.3} kg per second")
```

    0.167 kg per second

- This provides a default value in kilograms per second
- Might be useful to use the last reading to predict the rate over a
  longer period
- Can add an optional `period` parameter

``` python
def flow_rate(weight_diff, time_diff, period):
    return (weight_diff / time_diff) * period

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a

flow_per_second = flow_rate(weight_diff, time_diff, 1)
flow_per_hour = flow_rate(weight_diff, time_diff, 60 * 60)

print(f"{flow_per_second:.3f} kg per second\n{flow_per_hour:.3f} kg per hour")
```

    0.167 kg per second
    600.000 kg per hour

- Now requires `period` to be provided for every call
  - Much nicer if we instead specify a default value

``` python
def flow_rate(weight_diff, time_diff, period=1):
    return (weight_diff / time_diff) * period

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a

flow_per_second = flow_rate(weight_diff, time_diff)
flow_per_hour = flow_rate(weight_diff, time_diff, period=60 * 60)

print(f"{flow_per_second:.3f} kg per second\n{flow_per_hour:.3f} kg per hour")
```

    0.167 kg per second
    600.000 kg per hour

- Works well for simple, immutable default arguments

- Tricky for complex, mutable values e.g. `list`

- Keyword arguments also let us extend function arguments in a backwards
  compatible way

- E.g. If we want to extend `flow_rate` to support different weight
  units

  - Can’t add a new positional argument since every existing call would
    need to update
  - Add a new keyword parameter with default value
    - Choose default to preserve existing behaviour

``` python
def flow_rate(weight_diff, time_diff, period=1, units_per_kg=1):
    return (weight_diff * units_per_kg / time_diff) * period

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a

flow_per_second = flow_rate(weight_diff, time_diff)
flow_pounds_per_hour = flow_rate(weight_diff, time_diff, period=60 * 60, units_per_kg = 2.2)


print(f"{flow_per_second:.3f} kg per second\n{flow_pounds_per_hour:.3f} pounds per hour")
```

    0.167 kg per second
    1320.000 pounds per hour

- This is required when dealing with variable positional arguments
  - As others backwards compatibility is broken (See [Item
    34](../Item_034/item_034.qmd))
- This approach has the downside that keyword parameters may still be
  specified via position, e.g.

``` python
def flow_rate(weight_diff, time_diff, period=1, units_per_kg=1):
    return (weight_diff * units_per_kg / time_diff) * period

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a

flow_per_second = flow_rate(weight_diff, time_diff)
flow_pounds_per_hour = flow_rate(weight_diff, time_diff, 60 * 60, 2.2) # using positional call structure


print(f"{flow_per_second:.3f} kg per second\n{flow_pounds_per_hour:.3f} pounds per hour")
```

    0.167 kg per second
    1320.000 pounds per hour

- Best practice is to always specify optional parameters as keyword
  arguments
  - The function author can enforce this

## Things to Remember

- Function arguments can be specified by position or keyword
- Keywords make it clear what each argument corresponds to
- Keyword arguments with default values make it easy to extend function
  call interfaces
- Optional keyword arguments should always be passed by keyword instead
  of position
