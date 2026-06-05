# forward_references.py
#
# Working untyped implementation


class FirstClass:
    def __init__(self, value):
        self.value = value


class SecondClass:
    def __init__(self, value):
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
