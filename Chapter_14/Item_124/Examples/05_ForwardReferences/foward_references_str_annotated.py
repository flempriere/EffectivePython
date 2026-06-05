# forward_references_str_annotated.py
#
# str annotated versions
# Uses stringifyed type annotation to resolve forward reference
# Works for Python < 3.14


class FirstClass:
    def __init__(self, value: "SecondClass") -> None:
        self.value = value


class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
