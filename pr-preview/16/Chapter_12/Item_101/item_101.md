# Know the difference between `sort` and `sorted`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `sort` performs an in-place sort (See [Item
  100](../Item_100/item_100.qmd))
  - Results in original list being modified

``` python
butterflies = ["Swallowtail", "Monarch", "Red Admiral"]
print(f"Before sort: {butterflies}")
butterflies.sort()
print(f"After sort: {butterflies}")
```

    Before sort: ['Swallowtail', 'Monarch', 'Red Admiral']
    After sort: ['Monarch', 'Red Admiral', 'Swallowtail']

- The `sorted` built-in also can used to perform sorts
  - Contents are sorted and returned as a list
  - Original is left intact

``` python
original = ["Swallowtail", "Monarch", "Red Admiral"]
alphabetical = sorted(original)
print(f"Original {original}")
print(f"Sorted {alphabetical}")
```

    Original ['Swallowtail', 'Monarch', 'Red Admiral']
    Sorted ['Monarch', 'Red Admiral', 'Swallowtail']

- `sorted` can be used with any *iterable* object (See [Item
  21](../../Chapter_03/Item_021/item_021.qmd))
  - Works on dictionaries, tuples and sets

``` python
print("Sorting a dictionary")
dictionary = {"foo": 4568, "bar": 1234}
print(f"Sorted: {sorted(dictionary)}")

print("Sorting a tuple")
a_tuple = ("foo", "bar")
print(f"Sorted: {sorted(a_tuple)}")

print("Sorting a set")
patterns = {"solid", "spotted", "cells"}
print(f"Sorted: {sorted(patterns)}")
```

    Sorting a dictionary
    Sorted: ['bar', 'foo']
    Sorting a tuple
    Sorted: ['bar', 'foo']
    Sorting a set
    Sorted: ['cells', 'solid', 'spotted']

- Supports the `reverse` and `key` parameters like `sort` (See [Item
  100](../Item_100/item_100.qmd))

``` python
legs = {"insects": 6, "spiders": 8, "lizards": 4}
sorted_legs = sorted(legs, key=lambda x: legs[x], reverse=True)
print(sorted_legs)
```

    ['spiders', 'insects', 'lizards']

- When to use `sort` or `sorted`
  - `sort` is in-place so has a smaller memory overhead
    - No need to create a duplicate copy
    - Might be faster since restricted to a fixed size, `list` type, as
      opposed to an arbitrary iterable type
  - `sorted` creates a duplicate and so,
    - Preserves the original object
      - Avoids accidentally modifying objects or attributes (See [Item
        30](../../Chapter_05/Item_030/item_030.qmd) and [Item
        56](../../Chapter_07/Item_056/item_056.qmd))
    - Works for any Iterator
      - Can be used in functions to support *duck-typing* interfaces
        (See [Item 25](../../Chapter_04/Item_025/item_025.qmd))

## Things to Remember

- `sort` performs in-place on `list` types
  - Maximises speed and minimises memory overhead
- `sorted` returns a sorted copy of any Iterator
  - Maximises flexibility
  - Preserves original data
