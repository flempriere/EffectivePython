# Subtract function
#
# This implementation uses type annotations to catch misuse


def subtract(a: int, b: int) -> int:  # Added type annotations
    return a - b


subtract(10, "5")  # Oops: passed string value
