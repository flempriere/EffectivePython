# get_or_default
#
# Unexpected None received without type checking


def get_or_default(value, default):
    if value is not None:
        return value  # bug
    return value


found = get_or_default(3, 5)
assert found == 3
print("Test 1 passed!")

found = get_or_default(None, 5)
assert found == 5, found
print("Test 2 passed!")
