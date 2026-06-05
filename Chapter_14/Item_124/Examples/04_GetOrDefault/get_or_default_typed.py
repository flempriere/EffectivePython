# get_or_default_typed.py
#
# Demonstrates using union types to handle None checking


def get_or_default(value: int | None, default: int) -> int:
    if value is not None:
        return value  # type narrows to `int`
    return value  # does not match signature since if of type `int | None`


found = get_or_default(3, 5)
assert found == 3
print("Test 1 passed!")

found = get_or_default(None, 5)
assert found == 5, found
print("Test 2 passed!")
