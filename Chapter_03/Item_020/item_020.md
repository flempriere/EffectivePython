# Item 20: Never use `for` Loop Variables after the Loop Ends


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Variables created in a python `for` loop persist after the loop ends
  - Python does not have loops as independent block scopes as in a
    language like C

``` python
for i in range(3):
    print(f"Inside {i=}")
print(f"After {i=}")
```

    Inside i=0
    Inside i=1
    Inside i=2
    After i=2

- Loop variable persists with the value last assigned to it
- Can manipulate this behaviour
  - Here we group periodic elements by looking for their indices in a
    list

``` python
categories = ["Hydrogen", "Uranium", "Iron", "Other"]

for i, name in enumerate(categories):
    if name == "Iron":
        break
print(i)
```

    2

- If an element isn’t found in the list, last index is bound to `i`
  - Here that’s the `"Other"` category
- Assumption is we either find a match and end early, or iterate over
  all elements and fall through

``` python
categories = ["Hydrogen", "Uranium", "Iron", "Other"]

for i, name in enumerate(categories):
    if name == "Lithium":
        break
print(i)
```

    3

- The approach above breaks if the initial list is empty
- Then the loop never runs and `i` is never bound
  - Leads to a runtime error

``` python
categories = []
for i, name in enumerate(categories):
    if name == "Lithium":
        break
print(i)
```

    3

- We can find a solution for this specific example
  - But general point, no way to guarantee a loop variable is bound
    after the loop completes
- Comprehensions and generator expressions do not leak their variables
  after execution
  - Trying to access them will lead to an error

``` python
foo = [37, 13, 128, 21]
even = [i for i in foo if i % 2 == 0]
print(i) # always raises an error
```

    3

- Assignment expressions in comprehensions can change this
- Exception variables also don’t leak
  - But have their own quirks

## Things to Remember

- `for` loop variables are still in scope after the loop exits
- `for` loop variables are not assigned if the loop never executes an
  iteration
  - Cannot thus guarantee a loop variable exists after the loop
- Comprehensions and generator expression variables do not leak by
  default
- Exception handlers do not leak exception instance variables
