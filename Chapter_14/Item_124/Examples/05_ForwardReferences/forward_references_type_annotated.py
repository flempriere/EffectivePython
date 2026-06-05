# forward_references_annotated.py
#
# type annotated version
# breaks for python < 3.14 or without `from __future__ import annotations`

# if python version < 3.13
# from __future__ import annotations


class FirstClass:
    def __init__(self, value: SecondClass) -> None:
        self.value = value


class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
