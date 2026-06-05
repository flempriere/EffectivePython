# real_number.py
#
# Function operating on real numbers
# Demonstrates using generics for typing

from collections.abc import Callable
from typing import TypeVar

Value = TypeVar("Value")
Func = Callable[[Value, Value], Value]


def combine(func: Func[Value], values: list[Value]) -> Value:
    assert len(values) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result


Real = TypeVar("Real", int, float)


def add(x: Real, y: Real) -> Real:
    return x + y


inputs = [1, 2, 3, 4j]  # Includes a complex number so not a list[Real] type
result = combine(add, inputs)
assert result == 10
