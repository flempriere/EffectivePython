# Item 44: Consider Generator Expressions for Large List Comprehensions

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- List comprehensions have the disadvantage of needing to instance all
  their values
  - Can lead to excessive memory consumption for large inputs
- For example, reading and counting the number of characters on each
  line

``` python
value = [len(x) for x in open("my_file.txt")]
print(value)
```

    [70, 38, 18, 2, 5, 44, 6, 50, 61, 12]

- This would break for a long file
  - Or an *infinite file* like a network socket
- *generator expressions* or *generator comprehensions* provide the
  syntax of list comprehensions but the behaviour of generators
  - They don’t instantiate their entire output when run
  - Instead returns an iterator that yields one item at a time
- Generator expressions are created like a list comprehension using `()`
  instead of `[]`
- For example, (Naively) converting our program above to use a generator
  expression

``` python
it = (len(x) for x in open("my_file.txt"))
print(it)
```

    <generator object <genexpr> at 0x7fd98cb19460>

- To actually get values out of the returned iterator we have to call
  the `next` method (either explicitly or implicitly via a loop)

``` python
it = (len(x) for x in open("my_file.txt"))
print(next(it))
print(next(it))
```

    70
    38

- Generator expressions can also be composed together
- We could combine the above generator with a second that also includes
  the square root

``` python
it = (len(x) for x in open("my_file.txt"))
roots = ((x, x**0.5) for x in it)

print(next(roots))
```

    (70, 8.366600265340756)

- Iterating this iterator will *domino* iterating the wrapped iterators
- Chaining iterators tends to execute very quickly in Python
- When looking to compose functionality operating on large stream of
  input, generator expressions are the best tool (See [Item
  23](../../Chapter_03/Item_023/item_023.qmd) and [Item
  24](../../Chapter_03/Chapter_03.qmd))
- Again, beware that iterators returned by generators are stateful (See
  [Item 21](../../Chapter_03/Item_021/item_021.qmd))

## Things to Remember

- List comprehensions can consume excessive memory for large inputs
- Generator expressions avoid memory issues by producing outputs one at
  a time as iterators
- Generator expressions can be composed by passing iterators from one
  generator expression into the `for` subexpression of another
- Chained generator expressions execute very quickly (and are very
  memory efficient)
