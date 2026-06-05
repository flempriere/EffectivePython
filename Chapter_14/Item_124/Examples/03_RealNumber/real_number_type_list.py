# real_number.py
#
# Function operating on real numbers
# Demonstrates using generics for typing
# With Python 3.12 type parameter lists

from collections.abc import Callable


def combine[Value](func: Callable[[Value, Value], Value], values: list[Value]) -> Value:
    assert len(values) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result


def add[Real: (int, float)](x: Real, y: Real) -> Real:
    return x + y


inputs = [1, 2, 3, 4j]  # Includes a complex number so not a list[Real] type
result = combine(add, inputs)
assert result == 10
