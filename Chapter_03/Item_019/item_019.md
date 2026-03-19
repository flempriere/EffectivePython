# Item 19: Avoid `else` Blocks After `for` and `while` Loops

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Unlike most languages python’s `for` and `while` loops support an
  optional `else` block
  - The behaviour is not very intuitive

``` python
for i in range(3):
    print("Loop", i)
else:
    print("Else block!")
```

    Loop 0
    Loop 1
    Loop 2
    Else block!

- The else block above runs immediately after the loop!
- Why?
  - `else` in an `if/elif/else` construct only runs if neither preceding
    block does
  - `else` in a `try...except...else` only runs if no exception is
    thrown
  - `finally` in a `try...except...finally` is clear in that it always
    runs after the block regardless
- Intuitively one would expect it to mean “Do if the loop didn’t fully
  complete”
  - But is skipped if we `break` out of a loop

``` python
for i in range(3):
    print("Loop", i)
    if i == 1:
        break
else:
    print("Else block")
```

    Loop 0
    Loop 1

- `else` runs immediately if looping over empty sequence

``` python
for x in []:
    print("Never runs")
else:
    print("for else block")
```

    for else block

- `else` also runs when loop condition is initially `False`

``` python
while False:
    print("Never runs")
else:
    print("While else block")
```

    While else block

- `else` blocks are designed for when you’re searching for something
  - The idea being that you `break` if you find the object
  - Fall out of the loop otherwise
- E.g. determining if two numbers are co-prime
  - Iterate over the possible common divisors
  - If we find one we break out of the loop after declaring the numbers
    not co-prime
  - Otherwise the `else` informs the user that the result is coprime

``` python
a = 4
b = 9

for i in range(2, min(a, b) + 1):
    print("Testing", i)
    if a % i == 0 and b % i == 0:
        print("Not co-prime")
        break
else:
    print("Coprime")
```

    Testing 2
    Testing 3
    Testing 4
    Coprime

- In practice, the use case is niche for language level syntax support
  - Especially when that behaviour is not obvious by inference from
    other uses of the word
  - Prefer writing helper functions
- Approach 1: Return early on condition match
  - Return default after falling out of the loop

``` python
def coprime(a, b):
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            return False
    return True

assert coprime(4, 9)
assert not coprime(3, 6)
```

- Approach 2: Use a flag variable at the outer scope

``` python
def coprime(a, b):
    is_coprime = True
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            is_coprime = False
            break
    return is_coprime

assert coprime(4, 9)
assert not coprime(3, 6)
```

## Things to Remember

- Python has syntax allowing `else` blocks after `while` and `for` loops
- They execute any time the preceding loop is not exited via a `break`
- Avoid using them
  - Their behaviour is unintuitive
