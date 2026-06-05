# real_number.py
#
# Function operating on real numbers without typing


def combine(func, values):
    assert (len(values)) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result


def add(x, y):
    return x + y


inputs = [1, 2, 3, 4j]  # complex number fulfills number interface, but not expected
result = combine(add, inputs)
assert result == 10, result  # Fails
