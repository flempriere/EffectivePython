# Item 17: Prefer `enumerate` over `range`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `range` is a built-in useful for loops iterating over integer
  sequences
  - e.g. Generating a 32-bit random number by coin-flipping each bit
    position

``` python
from random import randint

random_bits = 0
for i in range(32): # 32 bits
    if randint(0, 1): # coin flip
        random_bits |= 1 << i

print(f"Randomly generated: {bin(random_bits)}")
```

    Randomly generated: 0b11101011100011000100100001110010

- We can directly loop over an data structure

``` python
ice_cream_flavours = ["vanilla", "chocolate", "pecan", "strawberry"]
for flavour in ice_cream_flavours:
    print(f"{flavour} is delicious")
```

    vanilla is delicious
    chocolate is delicious
    pecan is delicious
    strawberry is delicious

- A common paradigm is wanting to iterate over a list but also track the
  index
  - E.g. if we want to print out the index in a list
- You could do this with `range`

``` python
ice_cream_flavours = ["vanilla", "chocolate", "pecan", "strawberry"]

for i in range(len(ice_cream_flavours)):
    flavour = ice_cream_flavours[i]
    print(f"{i + 1}: {flavour}")
```

    1: vanilla
    2: chocolate
    3: pecan
    4: strawberry

- Not very pythonic
- Lot’s of noise is introduced via the explicit list index accesses and
  the call to `len`
- The `enumerate` built-in manages this for us
  - Wraps any iterator with a lazy generator
  - yields pairs of the form `(counter, value)`
    - Where counter is the number of elements previously returned
    - i.e. returns `0`, then `1` etc.
- Demonstrating the behaviour manually,

``` python
ice_cream_flavours = ["vanilla", "chocolate", "pecan", "strawberry"]
it = enumerate(ice_cream_flavours)
print(next(it))
print(next(it))
```

    (0, 'vanilla')
    (1, 'chocolate')

- We can then use unpacking to easily separate the components of the
  `enumerate` pair

``` python
ice_cream_flavours = ["vanilla", "chocolate", "pecan", "strawberry"]

for i, flavour in enumerate(ice_cream_flavours):
    print(f"{i + 1}: {flavour}")
```

    1: vanilla
    2: chocolate
    3: pecan
    4: strawberry

- `enumerate` also provides a `start` keyword, which sets the starting
  counter value
  - i.e. If we write `start=1` the counter values returned are `1` then
    `2` etc.
  - Does mean that the counter no longer directly aligns with the index
    in a sequence

``` python
ice_cream_flavours = ["vanilla", "chocolate", "pecan", "strawberry"]

for i, flavour in enumerate(ice_cream_flavours, start=1):
    print(f"{i}: {flavour}")
```

    1: vanilla
    2: chocolate
    3: pecan
    4: strawberry

## Things to Remember

- `enumerate` let’s you loop over the contents of a sequence while still
  getting the index as you go
- Prefer `enumerate` instead of looping over a range and indexing
  - More concise
  - Better readability
- `enumerate` accepts a `start` keyword argument to specify the starting
  value of the count value (default `0`)
  - This can mean that the returned count is not one-to-one with the
    index in the sequence
