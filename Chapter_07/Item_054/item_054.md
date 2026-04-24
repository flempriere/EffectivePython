# Item 54: Consider Composing Functionality with Mix-in Classes

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python’s object-oriented support enables multiple-inheritance (See
  [Item 53](../Item_053/item_053.qmd))
  - In general you should try to avoid multiple inheritance
- A compromise that gives the composition and inheritance of multiple
  inheritance is to use *mix-ins*
- A *mix-in* is a class defining a set of additional methods for child
  classes to implement
- Mix-in classes don’t define instance attributes or require an
  `__init__` constructor to be called
- Mix-in’s work because the python allows for simple inspection of the
  state of any object
  - Can write generic functionality once as a mix-in then apply it to
    other classes
  - Support composition, layering and reuse
- For example, might want to write a generic dictionary serialisation
  method
  - Makes sense to write one, then mix-in to classes as needed
  - Implementation is straightforward using dynamic attribute access
    - Using `hasattr`, dynamic type inspection with `isinstance` and the
      instance dictionary `__dict__`
- We’ll define a simple binary tree to demonstrate the use of this
  mix-in

``` python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


tree = BinaryTree(
    10,
    left=BinaryTree(7, right=BinaryTree(9)),
    right=BinaryTree(13, left=BinaryTree(11)),
)
print(tree.to_dict())
```

    {'value': 10, 'left': {'value': 7, 'left': None, 'right': {'value': 9, 'left': None, 'right': None}}, 'right': {'value': 13, 'left': {'value': 11, 'left': None, 'right': None}, 'right': None}}

- Mix-ins can make their functionality customizable
  - Allows for behaviour to be overridden when required
- For example, we might extend a `BinaryTree` to have a reference to
  it’s parent
  - The circular reference causes the default `to_dict` method to
    infinitely loop
  - Have to override the `_traverse` method to only process new values

``` python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Overrides the `ToDictMixin` `_traverse` method to avoid cycles


class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None, right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        if isinstance(value, BinaryTreeWithParent) and key == "parent":
            return value.value  # Prevent cycles
        else:
            return super()._traverse(key, value)  # traverse as per normal


root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)
print(root.to_dict())
```

    {'value': 10, 'left': {'value': 7, 'left': None, 'right': {'value': 9, 'left': None, 'right': None, 'parent': 7}, 'parent': 10}, 'right': None, 'parent': None}

- Defining `BinaryTreeWithParent._traverse` means any class that
  composes a `BinaryTreeWithParent` will automatically work with the
  `ToDictMixin`

``` python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Overrides the `ToDictMixin` `_traverse` method to avoid cycles


class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None, right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        if isinstance(value, BinaryTreeWithParent) and key == "parent":
            return value.value  # Prevent cycles
        else:
            return super()._traverse(key, value)  # traverse as per normal


# Adding a class that wrap's the BinaryTreeWithParent to demonstrate `ToDictMixin` working on composed attributes


class NamedSubTree(ToDictMixin):
    def __init__(self, name, tree_with_parent):
        self.name = name
        self.tree_with_parent = tree_with_parent


root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)

my_tree = NamedSubTree("foobar", root.left.right)
print(my_tree.to_dict())
```

    {'name': 'foobar', 'tree_with_parent': {'value': 9, 'left': None, 'right': None, 'parent': 7}}

- Mix-in’s can be composed together
- E.g. A JSON serializer might composed the `ToDictMixin` to use the
  `to_dict` method
  - The mixin can define both class and instance methods
  - Here we use a class method to deserialize and an instance method to
    serialize
  - Only requirements for `JSONMixin` are
    1. The class supports the `to_dict` method
    2. The `__init__` accepts keyword arguments (See [Item
        35](../../Chapter_05/Item_035/item_035.qmd))

``` python
import json


class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class JSONMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())
```

- We can then use this mixin to create a class hierarchy that supports
  serialization and deserialization
  - e.g. Here we have a datacenter topology represented as a class
    hierarchy

``` python
import json


class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class JSONMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())

class DatacenterRack(ToDictMixin, JSONMixin):
    def __init__(self, switch=None, machines=None):
        self.switch = Switch(**switch)
        self.machines = [Machine(**kwargs) for kwargs in machines]

class Switch(ToDictMixin, JSONMixin):
    def __init__(self, ports=None, speed=None):
        self.ports = ports
        self.speed = speed

class Machine(ToDictMixin, JSONMixin):
    def __init__(self, cores=None, ram=None, disk=None):
        self.cores = cores
        self.ram = ram
        self.disk = disk

serialized = """{
    "switch": {"ports": 5, "speed": 1e9},
    "machines": [
        {"cores": 8, "ram": 32e9, "disk": 5e12},
        {"cores": 4, "ram": 16e9, "disk": 1e12},
        {"cores": 2, "ram": 4e9, "disk": 500e9}
    ]
}"""

deserialized = DatacenterRack.from_json(serialized)
roundtrip = deserialized.to_json()
assert json.loads(serialized)  == json.loads(roundtrip)
```

- `super` ensures that even if we have a class hierarchy with multiple
  inheritances of a mix-in everything works correctly

## Things to Remember

- Avoid using multiple inheritance with instance attributes and
  `__init__` if mix-in classes can achieve the same outcome
- Use pluggable behaviours at the instance level to customise mix-in
  classes per-class when required
- Mix-ins can include instance methods or class methods
- Compose mix-ins to create complex functionality from simple behaviours
