# Item 50: Consider `functools.singledispatch` for Functional-Style

Programming Instead of Object-Oriented Polymorphism

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- We’ve seen that Object-Oriented Programming lets us structure code by
  packaging behaviours and data in a class hierarchy
  - Then use runtime polymorphism to dispatch methods to the respective
    subclass implementation
- Results in a hierarchy like,

``` python
class NodeAlt:
    def evaluate(self):
        raise NotImplementedError

    def pretty(self):
        raise NotImplementedError


class IntegerNodeAlt(NodeAlt):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

    def pretty(self):
        return repr(self.value)


class AddNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() + self.right.evaluate()

    def pretty(self):
        return f"({self.left.pretty()} + {self.right.pretty()})"


class MultiplyNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()

    def pretty(self):
        return f"({self.left.pretty()} * {self.right.pretty()})"


tree = MultiplyNodeAlt(
    AddNodeAlt(IntegerNodeAlt(3), IntegerNodeAlt(5)),
    AddNodeAlt(IntegerNodeAlt(4), IntegerNodeAlt(7)),
)
print(tree.pretty())
```

    ((3 + 5) * (4 + 7))

- If we instead had 25 methods on the superclass rather than two, we
  would have 25 methods on each node implementation
  - These methods for example might,
    1. Simplify an equation
    2. Check for undefined variables
    3. Calculate derivatives
    4. Produce LaTeX output
    5. etc.
- Sticking with the OOP approach leads to large class definitions
  - Especially if methods require helper functions and data structures
- Might then want to split node class definitions across multiple
  modules
  - e.g. one file per node type

``` python
class NodeAlt2:
    def evaluate(self): ...

    def pretty(self): ...

    def solve(self): ...

    def error_check(self): ...

    def derivative(self): ...

    # further methods
```

- Class per module structure leads to maintainability issues
  - Each method may be very different to the other methods on a class
  - Rather than grouping behaviours together (i.e. the same method
    across all implementations) each implementation groups distinct
    behaviours
- Issue is to change one behaviour we might have to navigate a small
  part of twenty-plus files rather than one
- OOP also conflates dependencies
  - e.g. LaTeX generation might require, special formatting libraries,
    formula-solving might require symbolic math
  - Each class then needs to import those dependencies
  - Dependencies from various subsystems thus leak across into each
    other due to class-based organisation
- *Single dispatch* is an alternative approach
- Functional-style programming technique
  - Program decides which version of a function to call based on the
    types of it’s arguments
  - Is another form of polymorphism
- Single dispatch avoids the OOP pitfalls
  - Allows us to have behaviour that changes based on the subclass
  - However that implementation is separate from the class definition
    itself
- Accessed via the `singledispatch` decorator supplied via `functools`
  - To use we first have to define and then wrap the function
- Here we define a function for custom object printing
  - Initial version is a fallback if no other option is found for the
    type of the first argument (here `value`)
- We then specialise for types using the `register` method on the
  function as a decorator
  - e.g. We might start by defining `int` and `float`

``` python
import functools


@functools.singledispatch
def my_print(value):
    raise NotImplementedError


@my_print.register(int)
def _(value):
    print("Integer!", value)


@my_print.register(float)
def _(value):
    print("Float!", value)


my_print(20)
my_print(1.23)
my_print("string")
```

    Integer! 20
    Float! 1.23

    NotImplementedError:
    ---------------------------------------------------------------------------
    NotImplementedError                       Traceback (most recent call last)
    Cell In[3], line 21
         19 my_print(20)
         20 my_print(1.23)
    ---> 21 my_print("string")

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/functools.py:982, in singledispatch.<locals>.wrapper(*args, **kw)
        979 if not args:
        980     raise TypeError(f'{funcname} requires at least '
        981                     '1 positional argument')
    --> 982 return dispatch(args[0].__class__)(*args, **kw)

    Cell In[3], line 6, in my_print(value)
          4 @functools.singledispatch
          5 def my_print(value):
    ----> 6     raise NotImplementedError

    NotImplementedError:

- The registered functions are defined with the name `_` which is the
  python shorthand for a name that doesn’t matter
  - Recall we used `_` as a placeholder when we wanted to discard a
    variable in an unpacking
- Dispatching occurs through `my_print`
- We could reimplement the pocket calculator using a `singledispatch`
  approach

``` python
import functools


@functools.singledispatch
def my_evaluate(node):
    raise NotImplementedError


class Integer:
    def __init__(self, value):
        self.value = value


@my_evaluate.register(Integer)
def _(node):
    return node.value


class Add:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Add)
def _(node):
    return my_evaluate(node.left) + my_evaluate(node.right)


class Multiply:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Multiply)
def _(node):
    return my_evaluate(node.left) * my_evaluate(node.right)


tree = Multiply(Add(Integer(3), Integer(5)), Add(Integer(4), Integer(7)))
print(my_evaluate(tree))
```

    88

- Now if we want to add a new method like pretty printing (See [Item
  49](../Item_049/item_049.qmd)) we can do so via another
  `singledispatch` function

``` python
import functools


@functools.singledispatch
def my_evaluate(node):
    raise NotImplementedError


class Integer:
    def __init__(self, value):
        self.value = value


@my_evaluate.register(Integer)
def _(node):
    return node.value


class Add:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Add)
def _(node):
    return my_evaluate(node.left) + my_evaluate(node.right)


class Multiply:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Multiply)
def _(node):
    return my_evaluate(node.left) * my_evaluate(node.right)


# Defining new single dispatch function


@functools.singledispatch
def my_pretty(node):
    raise NotImplementedError


@my_pretty.register(Integer)
def _(node):
    return repr(node.value)


@my_pretty.register(Add)
def _(node):
    return f"({my_pretty(node.left)} + {my_pretty(node.right)})"


@my_pretty.register(Multiply)
def _(node):
    return f"({my_pretty(node.left)} * {my_pretty(node.right)})"


tree = Multiply(Add(Integer(3), Integer(5)), Add(Integer(4), Integer(7)))
print(my_pretty(tree))
```

    ((3 + 5) * (4 + 7))

- If we subclass an already registered type than the dispatch will work
  as expected
  - Single dispatch follows method resolution order
  - If not defined on the class check the parent class until a method is
    found
  - Similar to inheritance (See [Item 53](../Item_053/item_053.qmd))
  - For example we could add a `PositiveInteger` type
- However trying to add a *new* class outside the hierarchy can cause
  issues
  - e.g. Let’s define a `Float`
  - calling `my_pretty` on the class leads to a `NotImplementedError`
    - No registered dispatch in the class hierarchy

``` python
import functools


@functools.singledispatch
def my_evaluate(node):
    raise NotImplementedError


class Integer:
    def __init__(self, value):
        self.value = value


@my_evaluate.register(Integer)
def _(node):
    return node.value


class Add:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Add)
def _(node):
    return my_evaluate(node.left) + my_evaluate(node.right)


class Multiply:
    def __init__(self, left, right):
        self.left = left
        self.right = right


@my_evaluate.register(Multiply)
def _(node):
    return my_evaluate(node.left) * my_evaluate(node.right)


# Defining new single dispatch function


@functools.singledispatch
def my_pretty(node):
    raise NotImplementedError


@my_pretty.register(Integer)
def _(node):
    return repr(node.value)


@my_pretty.register(Add)
def _(node):
    return f"({my_pretty(node.left)} + {my_pretty(node.right)})"


@my_pretty.register(Multiply)
def _(node):
    return f"({my_pretty(node.left)} * {my_pretty(node.right)})"


# Adding new types


class PositiveInteger(Integer):
    def __init__(self, value):
        if value < 0:
            raise ValueError(f"Invalid value {value} found. Must be >= 0")
        self.value = value


# method resolution matches existing Integer type
print(my_pretty(PositiveInteger(1234)))


class Float:
    def __init__(self, value):
        self.value = value


print(my_pretty(Float(5.678)))
```

    1234

    NotImplementedError:
    ---------------------------------------------------------------------------
    NotImplementedError                       Traceback (most recent call last)
    Cell In[6], line 83
         79     def __init__(self, value):
         80         self.value = value
    ---> 83 print(my_pretty(Float(5.678)))

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/functools.py:982, in singledispatch.<locals>.wrapper(*args, **kw)
        979 if not args:
        980     raise TypeError(f'{funcname} requires at least '
        981                     '1 positional argument')
    --> 982 return dispatch(args[0].__class__)(*args, **kw)

    Cell In[6], line 46, in my_pretty(node)
         44 @functools.singledispatch
         45 def my_pretty(node):
    ---> 46     raise NotImplementedError

    NotImplementedError:

- Since the “methods” are no longer attached to the class it is no
  longer clear we have to implement them until we try to use them
- This is the trade-off of single-dispatch vs polymorphism
  - Adding a new type requires us to add an implementation for each
    dispatch function supported
  - May have to modify many different modules
- With OOP we instead
  - New classes easier to add since methods defined
  - Adding new method requires updating every class
- Generally single-dispatch has less friction and better organisational
  cohesion
  - Can have many data structures and behaviours without leading to
    large class definitions
  - Modules can be defined to handle specific behaviours
  - Simple data structures live in low down modules used by many higher
    level dependencies with low coupling
  - Maintainability is improved as is extensibility and refactorability
- OOP is still a good organisation pattern for shared functionality and
  large interconnected components
  - Both styles can be mixed

## Things to Remember

- OOP leads to a class-centric design and code layout
  - Poses challenges for building and maintaining large systems as
    behaviours become spread out over modules
- Single dispatch achieves runtime dispatch via functions instead of
  methods
  - Resolution is still type dependent
  - Related functionality can be defined and stored together
- Python’s `functools` built-in provides `singledispatch` as a decorator
  for implementing single dispatch
- Programs with highly independent systems operating on the same data
  tend to benefit from a functional over OOP style
