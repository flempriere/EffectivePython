# Item 30: Know that Function Arguments can be Mutated


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python doesn’t support pointer types
  - But variables are all technically references
- Function arguments are passed by reference too
  - Simple types (`string`, `int` etc.) are immutable types
    - Appear to behave as value types
  - Complex types can thus be mutated in a function
    - The mutation will then replicate in the original reference

``` python
# demonstrate mutating function arguments

def my_func(items):
    items.append(4)

x = [1, 2, 3]
my_func(x) # `x` is mutated by the function
print(x)
```

    [1, 2, 3, 4]

- Can’t replace the reference with an entirely new object, but can
  mutate it
- More generally multiple variables can refer to the same data
  - They are said to *alias* each other
  - Modifying either reference is repeated in the other alias

``` python
def my_func(items):
    items.append(4)

a = [7, 6, 5]
b = a
my_func(b)

print("a:", a)
print("b:", b)
```

    a: [7, 6, 5, 4]
    b: [7, 6, 5, 4]

- List’s and dictionaries can pass a copy to act as insulation layer
- Here we demonstrate doing so via slice operators

``` python
# Using a copy of a list to isolate changes to the original reference


def capitalise_items(items):
    for i in range(len(items)):
        items[i] = items[i].capitalize()


my_items = ["hello", "world"]
items_copy = my_items[:]  # Creates a copy
capitalise_items(items_copy)

print("Original:", my_items)
print("Copy:", items_copy)
```

    Original: ['hello', 'world']
    Copy: ['Hello', 'World']

- Dictionary provides a `copy` method that can be used directly

``` python
def concat_pairs(items):
    for key in items:
        items[key] = f"{key}={items[key]}"


my_pairs = {"foo": 1, "bar": 2}
pairs_copy = my_pairs.copy()  # Create a dictionary copy
concat_pairs(pairs_copy)

print("Original:", my_pairs)
print("Copy:", pairs_copy)
```

    Original: {'foo': 1, 'bar': 2}
    Copy: {'foo': 'foo=1', 'bar': 'bar=2'}

- User-defined classes are also modifiable
  - Any internal properties that can be accessed can be modified

``` python
class MyClass:
    def __init__(self, value):
        self.value = value


x = MyClass(10)


def my_func(obj):
    obj.value = 20  # Modify the object


my_func(x)
print(x.value)
```

    20

- When implementing a function to be used by others,
  - don’t modify mutable values except where documented explicitly in
    the function interface (in order of priority):
    1.  The function name (make clear what’s being modified)
    2.  Function argument names (make clear which argument is being
        modified)
    3.  Documentation (Provide detailed explanation)
- You should also consider creating a defensive copy of received
  arguments to prevent confusion
  - Especially when iteration is involved (see [Item
    21](../../Chapter_03/Item_021/item_021.qmd), [Item
    22](../../Chapter_03/Item_022/item_022.qmd))
- When calling a function,
  - Be careful about passing mutable arguments
    - Your data might get modified
  - For complex objects you control,
    - Consider adding helper functions to create defensive copies
    - Or consider a functional approach
      - Leverage immutable objects
      - Make functions pure

## Things to Remember

- Arguments in python are passed by reference
  - This means their attributes can be mutated by functions and methods
- Functions should make it clear via naming and documentation when input
  arguments may be modified
  - In general, they should try to avoid the need to directly modify
    arguments
- Creating copies of collections and objects received as input ensures
  functions avoid accidentally modifying data
