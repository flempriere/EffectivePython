# Item 15: Avoid Striding and Slicing in a Single Expression


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python *slices* can be extended with a *stride*
  - i.e. `a_sequence[start:stop:stride]`
  - `stride` lets you specify $n$ such that every $n$-th item is taken
  - For example slicing even and odd indices in a list

``` python
x = ["red", "orange", "yellow", "green", "blue", "purple"]
odds = x[::2] # First, third, fifth
evens = x[1::2] # Second, fourth, sixth

print(odds)
print(evens)
```

    ['red', 'yellow', 'blue']
    ['orange', 'green', 'purple']

- The stride syntax can cause unexpected behaviour
- e.g. to reverse a string one normally slices with a stride of `-1`

``` python
x = b"Mongoose"
y = x[::-1]
print(y)
```

    b'esoognoM'

- Also works for unicode strings (See [Item
  10](../../Chapter_02/Item_010/item_010.qmd))
  - But not when encoded as a UTF-8 byte string
  - The individual bytes are reversed, no longer valid utf-8, so the
    decoding fails

``` python
print("Reversing a unicode string")
x = "☘️🪉"
y = x[::-1]
print(y)

print("Reversing the encoded UTF-8 representation")
x = "☘️🪉"
w = x.encode("utf-8")
y = w[::-1]
z = y.decode("utf-8")
print(z)
```

    Reversing a unicode string
    🪉️☘
    Reversing the encoded UTF-8 representation

    UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte
    ---------------------------------------------------------------------------
    UnicodeDecodeError                        Traceback (most recent call last)
    Cell In[3], line 10
          8 w = x.encode("utf-8")
          9 y = w[::-1]
    ---> 10 z = y.decode("utf-8")
         11 print(z)

    UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte

- Consider the following other strides
  1.  Here `[::2]` means select every 2nd element starting at the
      beginning
  2.  What does `[::-2]` mean?
      - Take every second element, starting at the end, moving backwards
  3.  What does `[2::2]` mean?
      - Every second item, starting at the third
  4.  What does `[-2::-2]` mean?
      - Select every second item, starting two from the end and moving
        backwards
  5.  What does `[-2:2:-2]` mean?
      - Select every second item, starting two from the end, moving
        backwards to the third index
  6.  What does `[2:2:-2]` mean?
      - Select every second element from the third element to the third
        element, moving backwards
      - So select nothing because `[2:2]` is empty

``` python
x = ["a", "b", "c", "d", "e", "f", "g", "h"]


print("x[::2]:", x[::2])
print("x[::-2]:", x[::-2])
print("x[2::2]:", x[2::2])
print("x[-2::-2]:", x[-2::-2])
print("x[-2:2:-2]:", x[-2:2:-2])
print("x[2:2:-2]:", x[2:2:-2])
```

    x[::2]: ['a', 'c', 'e', 'g']
    x[::-2]: ['h', 'f', 'd', 'b']
    x[2::2]: ['c', 'e', 'g']
    x[-2::-2]: ['g', 'e', 'c', 'a']
    x[-2:2:-2]: ['g', 'e']
    x[2:2:-2]: []

- Combining strides and slices thus creates very dense and hard to parse
  expressions
  - Especially when the stride is negative
- Consider splitting into two steps
  1.  Stride first
  2.  Then slice

``` python
x = ["a", "b", "c", "d", "e", "f", "g", "h"]
y = x[::2] # take every second item
y = y[1:-1] # take every element from the first, to one from the end
print(y)
```

    ['c', 'e']

- Striding + slicing results in an additional shallow copy
  - Hence why we stride first -\> reduces the memory footprint of the
    intermediate copy
  - If this is still too memory intensive consider the `itertools`
    module
    - Provides `islice` which is a cleaner interface

## Things to Remember

- Specifying start, end and stride in one expression can result in
  overly dense expressions
- If striding try to only use positive strides and mixed start or end
  indices
  - Negative strides should be avoided due to unclear behaviour
- If you need to start, end and stride consider splitting it into two
  operations
  - Alternatively use `islice` from `itertools`
