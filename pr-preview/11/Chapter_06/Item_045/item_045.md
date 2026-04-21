# Item 45: Compose Multiple Generators with `yield from`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Generators solve many problems (See [Item
  43](../Item_043/item_043.qmd) and [Item
  21](../../Chapter_03/Item_021/item_021.qmd))
- Many programs can look like layers of generators
- For example, a graphical program might use generators to animate
  images onscreen
  - The visual might move quickly first, then pause, then move at a
    slower pace
  - This can be done with a pair of generators each yielding the delta
    for each animation

``` python
def move(period, speed):
    for _ in range(period):
        yield speed

def pause(delay):
    for _ in range(delay):
        yield 0
```

- The final animation is made by combining the two generators above
  - We need to iterate over each generator in turn
  - `yield` from each generator respectively

``` python
def move(period, speed):
    for _ in range(period):
        yield speed


def pause(delay):
    for _ in range(delay):
        yield 0


def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta
    for delta in move(2, 3.0):
        yield delta
```

- - We can then use a single `render` interface to run the animations
    - In this case we’ll just list the delta’s

``` python
def move(period, speed):
    for _ in range(period):
        yield speed


def pause(delay):
    for _ in range(delay):
        yield 0


def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta
    for delta in move(2, 3.0):
        yield delta


def render(delta):

    print(f"Delta: {delta:.1f}")

    # Move the images onscreen


def run(func):
    for delta in func():
        render(delta)


run(animate)
```

    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 0.0
    Delta: 0.0
    Delta: 0.0
    Delta: 3.0
    Delta: 3.0

- It would be nice if we could make the `animate` function cleaner
  - Currently it has to repeat the `yield`, and individually use a `for`
    loop for each generator
  - Generalising this to more generators is even harder to read
- We can improve this by using the `yield from` statement
  - Let’s you yield all values from a nested generator before returning
    control to the parent generator
- Our reimplemented `animate` is then,

``` python
def move(period, speed):
    for _ in range(period):
        yield speed


def pause(delay):
    for _ in range(delay):
        yield 0


# Rewritten animate function
def animate_composed():
    yield from move(4, 5.0)
    yield from pause(3)
    yield from move(2, 3.0)


def render(delta):

    print(f"Delta: {delta:.1f}")

    # Move the images onscreen


def run(func):
    for delta in func():
        render(delta)


run(animate_composed)
```

    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 5.0
    Delta: 0.0
    Delta: 0.0
    Delta: 0.0
    Delta: 3.0
    Delta: 3.0

- The result is the same, the code is however cleaner and more obvious
  how to generalise
  - `yield from` effectively instructs the interpreter to handle a
    nested `for` and `yield`
    - This also speeds up execution
- Consider using `yield from` any time you compose generators

## Things to Remember

- The `yield from` expression aids combining multiple nested generators
  into a single generator
- `yield from` eliminates boilerplate required for manually iterating
  nested generators and yielding their outputs
