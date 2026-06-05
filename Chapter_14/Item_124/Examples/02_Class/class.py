# class.py
#
# Demonstrates the use of typing with a class


class Counter:
    def __init__(self):
        self.value = 0

    # first issue, not assigning to self.value parameter
    def add(self, offset):
        value += offset  # noqa: F821, F841

    def get(self) -> int:
        self.value


counter = Counter()

# second issue, missing return
found = counter.get()
assert found == 0, found
