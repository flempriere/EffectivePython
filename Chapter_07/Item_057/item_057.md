# Item 57: Inherit from `Collections.abc` Classes for Custom Container

Types

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- A common programming problem involves defining container classes
  - Those that contain data
- Then also need to define the relations between them
- All python classes are technically containers
  - They encapsulate functionality and data, usually in dictionaries
- Python provides basic built-in container types `list`, `dict`,
  `tuple`, `set`
- When defining simple containers, natural to want to subclass `list` or
  `dict` directly
  - e.g. for some sequence type we would use `list`
  - For some mapping we might use `dict`
- For example, we might want a list that also records the frequency of
  it’s elements
  - By inheriting from `list` we get all of it’s default functionality
    and semantics
  - Then can define any additional methods that we need

``` python
class FrequencyList(list):
    def __init__(self, members):
        super().__init__(members)

    def frequency(self):
        counts = {}
        for item in self:
            counts[item] = counts.get(item, 0) + 1
        return counts


foo = FrequencyList(["a", "b", "a", "c", "b", "a", "d"])
print("Length is", len(foo))
foo.pop()
print("After pop:", repr(foo))
print("Frequency:", foo.frequency())
```

    Length is 7
    After pop: ['a', 'b', 'a', 'c', 'b', 'a']
    Frequency: {'a': 3, 'b': 2, 'c': 1}

- What if we want to provide an object that feels like a `list` and
  supports indexing but isn’t a `list` subclass
  - e.g. We might want sequence semantics for a binary tree (So we can
    take slices for example - See [Item
    14](../../Chapter_02/Item_014/item_014.qmd))

``` python
# basic binary tree structure

class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

- We could make this behave as sequence by manually implementing the
  sequence dunder methods
- For example, to define access by indexing we have to define
  `__getitem__` for example the following are equivalent

``` python
bar = [1, 2, 3]

# access via the indexing operator
print("Accessing via the index operator:", bar[0])

# access via the `__getitem__` dunder method
print("Accesing via the __getitem__ method", bar.__getitem__(0))
```

    Accessing via the index operator: 1
    Accesing via the __getitem__ method 1

- For example we could implement a depth-first tree traversal for
  `__getitem__`
  - Can then access the tree both via the tree structure and a list-like
    structure
- But `__getitem__` doesn’t implement all the sequence semantics
  - e.g. `len` fails (see below)

``` python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# BinaryNode class that supports indexing
class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()

    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")


# constructing the tree as per usual
tree = IndexableNode(
    10,
    left=IndexableNode(
        5, left=IndexableNode(2), right=IndexableNode(6, right=IndexableNode(7))
    ),
    right=IndexableNode(15, left=IndexableNode(11)),
)

# list like access and traversal
print("LRR is", tree.left.right.right.value)
print("Index 0 is", tree[0])
print("Index 1 is", tree[1])
print("11 is in the tree?", 11 in tree)
print("17 is in the tree?", 17 in tree)
print("Tree is", list(tree))

# fails
len(tree)
```

    LRR is 7
    Index 0 is 2
    Index 1 is 5
    11 is in the tree? True
    17 is in the tree? False
    Tree is [2, 5, 6, 7, 10, 11, 15]

    TypeError: object of type 'IndexableNode' has no len()
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[4], line 42
         39 print("Tree is", list(tree))
         41 # fails
    ---> 42 len(tree)

    TypeError: object of type 'IndexableNode' has no len()

- To support `len` the sequence object has to provide the `__len__`
  dunder method

``` python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# BinaryNode class that supports indexing
class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()

    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")


# Adding length support
class SequenceNode(IndexableNode):
    def __len__(self):
        count = 0
        for _ in self._traverse():
            count += 1
        return count


# constructing the tree as per usual
tree = SequenceNode(
    10,
    left=SequenceNode(
        5, left=SequenceNode(2), right=SequenceNode(6, right=SequenceNode(7))
    ),
    right=SequenceNode(15, left=SequenceNode(11)),
)

# list like access and traversal
print("LRR is", tree.left.right.right.value)
print("Index 0 is", tree[0])
print("Index 1 is", tree[1])
print("11 is in the tree?", 11 in tree)
print("17 is in the tree?", 17 in tree)
print("Tree is", list(tree))

# passes
len(tree)
```

    LRR is 7
    Index 0 is 2
    Index 1 is 5
    11 is in the tree? True
    17 is in the tree? False
    Tree is [2, 5, 6, 7, 10, 11, 15]

    7

- We *still* don’t have a full sequence
- Need to further implement the `count` and `index` methods
- `collections.abc` is a built-in that provides abstract base classes
  providing the methods of the base container types
  - When subclassing one of these types forgetting to implement a method
    will lead to a runtime error

``` python
from collections.abc import Sequence


class BadSequence(Sequence):
    pass


foo = BadSequence()
```

    TypeError: Can't instantiate abstract class BadSequence without an implementation for abstract methods '__getitem__', '__len__'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[6], line 8
          4 class BadSequence(Sequence):
          5     pass
    ----> 8 foo = BadSequence()

    TypeError: Can't instantiate abstract class BadSequence without an implementation for abstract methods '__getitem__', '__len__'

- If we implement the required methods of the abstract class, the
  additional methods are then provided automatically by the base class

``` python
from collections.abc import Sequence


class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# BinaryNode class that supports indexing
class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()

    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")


# Adding length support
class SequenceNode(IndexableNode):
    def __len__(self):
        count = 0
        for _ in self._traverse():
            count += 1
        return count


class CompleteSequenceNode(SequenceNode, Sequence):
    pass


# constructing the tree as per usual
tree = CompleteSequenceNode(
    10,
    left=CompleteSequenceNode(
        5,
        left=CompleteSequenceNode(2),
        right=CompleteSequenceNode(6, right=CompleteSequenceNode(7)),
    ),
    right=CompleteSequenceNode(15, left=CompleteSequenceNode(11)),
)

# list like access and traversal
print("LRR is", tree.left.right.right.value)
print("Index 0 is", tree[0])
print("Index 1 is", tree[1])
print("11 is in the tree?", 11 in tree)
print("17 is in the tree?", 17 in tree)
print("Tree is", list(tree))

# passes since defined on the `SequenceClass`
len(tree)

# index and count inherited via the `Sequence` abstract class
print("Index of 7 is", tree.index(7))
print("Count of 10 is", tree.count(10))
```

    LRR is 7
    Index 0 is 2
    Index 1 is 5
    11 is in the tree? True
    17 is in the tree? False
    Tree is [2, 5, 6, 7, 10, 11, 15]
    Index of 7 is 3
    Count of 10 is 1

- Abstract base classes also exist for more complex container types
  (e.g. `Set` and `MutableMapping`)
  - These have a large number of special methods which must be
    implemented or derived
- There are also further special methods used for object comparison and
  sorting
  - Can be applied to container and non-container types (See [Item
    51](../Item_051/item_051.qmd))

## Things to Remember

- For simple use cases consider directly inheriting from a concrete
  container type like `list` or `dict`
  - Let’s you use their fundamental behaviour
- Custom container types may require the implementation of a large
  number of special methods when not directly inheriting from a concrete
  class
- Inheriting from the abstract collections in `collections.abc` ensures
  that custom container classes match the required behaviours
