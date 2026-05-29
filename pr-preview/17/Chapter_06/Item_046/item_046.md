# Item 46: Pass Iterators into Generators as Arguments Instead of
Calling the `send` Method


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `yield` expressions let generator functions simply produce an iterable
  of output values (See [Item 43](../Item_043/item_043.qmd))
- However we might want a case where we have bidirectional communication
  - i.e. the ability to feed in data as well as read it
- For example, consider a program transmitting signals via a software
  defined radio
  - Might want to approximate a sine wave with a fixed point set
    (`wave`)
  - We’ll add a function to `transmit` the wave

``` python
import math


def wave(amplitude, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction

        yield output


def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")


def run(it):
    for output in it:
        transmit(output)


run(wave(3.0, 8))  # 8 step sine wave of amplitude 3
```

    Output:   0.0
    Output:   2.1
    Output:   3.0
    Output:   2.1
    Output:   0.0
    Output:  -2.1
    Output:  -3.0
    Output:  -2.1

- Works straightforward for simple fixed amplitude inputs
- Can’t be used if we want to vary a parameter via another parameter
  e.g. amplitude
  - This is necessary if we wanted to say represent AM Radio
- Python generators support the `send` method
  - Convert’s `yield` expressions to two-way communication
  - Provide streaming inputs to a generator while it’s yielding
- Normally, a `yield` expression returns `None`

``` python
def my_generator():
    received = yield 1
    print(f"{received=}")


it = my_generator()
output = next(it)  # Get first generator output
print(f"{output}")

try:
    next(it)  # Get next generator output, should exit
except StopIteration:
    pass
```

    1
    received=None

- When we use `send` supplied parameter becomes the value of the `yield`
  when the generator returns
- When a generator starts there is no `yield` yet
  - Only valid value for `send` is `None`
- For example using the above generators but with `send`

``` python
def my_generator():
    received = yield 1
    print(f"{received=}")


it = my_generator()
output = it.send(None)  # Get first generator output
print(f"{output=}")

try:
    it.send("hello")  # Send value into generator
except StopIteration:
    pass
```

    output=1
    received='hello'

- Now if we want to modulate the amplitude we can
  - We save the amplitude returned by the generator and use that in a
    calculation to feed in the next value

``` python
import math


def wave_modulating(steps):
    step_size = 2 * math.pi / steps
    amplitude = yield  # Receive the initial amplitude
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output  # Receive the next amplitude


def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")


def run_modulating(it):
    amplitudes = [None, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)


run_modulating(wave_modulating(12))
```

    Output is None
    Output:   0.0
    Output:   3.5
    Output:   6.1
    Output:   2.0
    Output:   1.7
    Output:   1.0
    Output:   0.0
    Output:  -5.0
    Output:  -8.7
    Output: -10.0
    Output:  -8.7
    Output:  -5.0

- This code is relatively unintuitive
- `yield` is typically analogous to a `return` so seeing it in an
  assignment is not obvious to a new reader
- Hard to follow the mixing of `yield` and `send`
  - They have a non-obvious relationship to new readers
- What if we had more complex requirements?
  - E.g. a complex waveform signal
  - Multiple signals in sequence
  - We could compose multiple generators (See [Item
    45](../Item_045/item_045.qmd))

``` python
import math


def wave(amplitude, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction

        yield output


# complex wave consisting of three sequential waves
def complex_wave():
    yield from wave(7.0, 3)
    yield from wave(2.0, 4)
    yield from wave(10.0, 5)


def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")


def run(it):
    for output in it:
        transmit(output)


run(complex_wave())
```

    Output:   0.0
    Output:   6.1
    Output:  -6.1
    Output:   0.0
    Output:   2.0
    Output:   0.0
    Output:  -2.0
    Output:   0.0
    Output:   9.5
    Output:   5.9
    Output:  -5.9
    Output:  -9.5

- One would hope to be able to merge `yield from` and `send`
- However results might be unintuitive

``` python
import math


def wave_modulating(steps):
    step_size = 2 * math.pi / steps
    amplitude = yield  # Receive the initial amplitude
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output  # Receive the next amplitude


def complex_wave_modulating():
    yield from wave_modulating(3)
    yield from wave_modulating(4)
    yield from wave_modulating(5)


def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")


def run_modulating(it):
    amplitudes = [None, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)


run_modulating(complex_wave_modulating())
```

    Output is None
    Output:   0.0
    Output:   6.1
    Output:  -6.1
    Output is None
    Output:   0.0
    Output:   2.0
    Output:   0.0
    Output: -10.0
    Output is None
    Output:   0.0
    Output:   9.5
    Output:   5.9

- The output *looks* reasonable
- However, there are too many `None` values
  - When each `yield from` finishes iterating a nested generator we move
    to the next one
  - This fresh generator starts with an empty `yield`
    - Results in a `None` output
- i.e. `yield from` and `send` do not work together
  - They break each other’s promises
- In general avoid `send` because of the hidden complexities
- Easiest solution is to pass an iterator into the wave function
  - Iterator should return an amplitude each time `next` is called
  - Results in each generator being processed as a cascade of input
  - Outputs are also processed efficiently (See [Item
    44](../Item_044/item_044.qmd) and [Item
    23](../../Chapter_03/Item_023/item_023.qmd))
- We can pass the iterator into each generator being composed via a
  `yield from`
  - Iterators are stateful, each generator will consume after the
    previous one (See [Item 21](../../Chapter_03/Item_021/item_021.qmd))
- The composed generator can then be run by passing in an iterator
  - e.g. by converting a `list`
- This approach supports *any* input iterator
  - Could be dynamic, e.g. from a function or composed (See [Item
    24](../../Chapter_03/Item_024/item_024.qmd))
- *Downside:* The above assumes the generator is *thread-safe*
  - Not strictly true
  - In such cases instead consider `async` functions

``` python
import math


def wave_cascading(amplitude_it, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it)  # get next input
        output = amplitude * fraction
        yield output


def complex_wave_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)


def run_cascading():
    amplitudes = [7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    it = complex_wave_cascading(iter(amplitudes))  # iterator
    for amplitude in amplitudes:
        output = next(it)
        transmit(output)


def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")


run_cascading()
```

    Output:   0.0
    Output:   6.1
    Output:  -6.1
    Output:   0.0
    Output:   2.0
    Output:   0.0
    Output:  -2.0
    Output:   0.0
    Output:   9.5
    Output:   5.9
    Output:  -5.9
    Output:  -9.5

## Things to Remember

- The `send` method can be used to inject data into a generator
  - Works via providing a return value to a `yield` expression
- Using `send` with `yield from` can cause surprising behaviour
  - E.g. surprising repetition of values
- Providing an input iterator to a set of composed generators is a
  better approach
  - Avoid using `send`
