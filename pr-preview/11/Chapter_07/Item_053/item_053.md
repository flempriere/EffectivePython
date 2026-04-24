# Item 53: Initialise Parent Classes with `super`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- The old way to initialise a parent class is to explicitly call the
  parent class’ `__init__` method within the child

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value


class ChildClass(BaseClass):
    def __init__(self, value):
        BaseClass.__init__(self, 5)


child = ChildClass(5)
print(child.value)
```

    5

- Approach is brittle and likely to break in more complex set-ups
- If we consider using multiple-inheritance (See [Item
  54](../Item_054/item_054.qmd)) calling the superclasses’ `__init__`
  can be unpredictable
  - `__init__` call order isn’t specified across all subclasses, e.g.
  - For example, we might have two base classes (`TimesTwo` and
    `PlusFive`)
    - Then have two subclasses that call the superclass `__init__` but
      accept inherit the superclasses in different orders

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value


class TimesTwo:
    def __init__(self):
        self.value *= 2


class PlusFive:
    def __init__(self):
        self.value += 5


class OneWay(BaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        BaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)


class AnotherWay(BaseClass, PlusFive, TimesTwo):
    def __init__(self, value):
        # construction order doesn't match parameter order
        BaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)


foo = OneWay(5)
bar = AnotherWay(5)
print("First ordering should be (5 * 2) + 5 = 15. Is", foo.value)
print("Second ordering should be (5 + 5) * 2 = 20. Is", bar.value)
```

    First ordering should be (5 * 2) + 5 = 15. Is 15
    Second ordering should be (5 + 5) * 2 = 20. Is 15

- In the second case the order of the `__init__` calls in the subclass
  don’t match the inheritance order in the class, and so the behaviour
  doesn’t match
- The problem is we are defining the ordering in two places
  - First in the class definition where we define the inheritance
  - Second in the `__init__` where we construct the objects
- There are similar issues with *diamond inheritance*
  - i.e Class A inherits from classes B and C both of which inherit from
    class D

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value


class TimesTwo(BaseClass):
    def __init__(self, value):
        BaseClass.__init__(self, value)
        self.value *= 2


class PlusFive(BaseClass):
    def __init__(self):
        BaseClass.__init__(self, value)
        self.value += 5


class ThisWay(TimesTwo, PlusFive):
    def __init__(self, value):
        TimesTwo.__init__(self, value)
        PlusFive.__init__(self, value)


foo = ThisWay(5)
print("Should be (5 * 2) + 5 = 15. Is", foo.value)
```

    TypeError: PlusFive.__init__() takes 1 positional argument but 2 were given
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[3], line 24
         20         TimesTwo.__init__(self, value)
         21         PlusFive.__init__(self, value)
    ---> 24 foo = ThisWay(5)
         25 print("Should be (5 * 2) + 5 = 15. Is", foo.value)

    Cell In[3], line 21, in ThisWay.__init__(self, value)
         19 def __init__(self, value):
         20     TimesTwo.__init__(self, value)
    ---> 21     PlusFive.__init__(self, value)

    TypeError: PlusFive.__init__() takes 1 positional argument but 2 were given

- The above returns $10$ not $15$, why?
  - The call to the second superclass (`PlusFive`) calls the `BaseClass`
    constructor for a second time
  - This resets `self.value` and we lose the changes made by the first
    superclass `TimesTwo`
- The built-in `super` function and method order resolution (MRO) exist
  to work around these issues
  - `super` ensures common superclasses in diamond hierarchies are
    instantiated only once
    - Also means we don’t need to explicitly pass the `self` parameter
  - MRO defines the ordering of superclass initialisation
    - Uses an algorithm (C3 linearisation)
- We can rewrite our previous example to use `super`

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value


class TimesTwo(BaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value *= 2


class PlusFive(BaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value += 5


class ThisWay(TimesTwo, PlusFive):
    def __init__(self, value):
        super().__init__(value)


foo = ThisWay(5)
print(foo.value)
```

    20

- We can see that the result above is $20$ which corresponds to
  $2 \times \left(5 + 5\right)$ which might not intuitively seem correct
  - Since we defined our first superclass as `TimesTwo` we might expect
    it to run first
- It is this way due to the method order resolution ordering
  - We can inspect this with the `mro` class method or via the attribute
    `__mro__`

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value


class TimesTwo(BaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value *= 2


class PlusFive(BaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value += 5


class ThisWay(TimesTwo, PlusFive):
    def __init__(self, value):
        super().__init__(value)


mro_str = "\n".join(repr(cls) for cls in ThisWay.__mro__)
print(mro_str)
```

    <class '__main__.ThisWay'>
    <class '__main__.TimesTwo'>
    <class '__main__.PlusFive'>
    <class '__main__.BaseClass'>
    <class 'object'>

- Here the ordering is

$$
\begin{align}
\text{ThisWay} \rightarrow \text{TimesTwo} \rightarrow \text{PlusFive} \rightarrow \text{BaseClass} \rightarrow \text{object}
\end{align}
$$

- Means that the `__init__` methods work backwards from the definition
  order
  - Since we walk up the chain calling `__init__` recursively, then
    return back
    1.  `BaseClass` sets value to $5$
    2.  `PlusFive` then adds $5$ to get $10$
    3.  `TimesTwo` then multiplies by $2$ to get $20$
    4.  `ThisWay` doesn’t then change the value
- `super` is also more flexible and maintainable
  - If we rename the class we don’t have to change the `super` call
  - Can also be called with two parameters
    1.  Type of the class who MRO parent view you’re trying to access
    2.  The instance on which to access that view
  - Parameters are not required but will be supplied automatically
    (`__class__` and `self`) when they are not passed
  - The following are equivalent

``` python
class BaseClass:
    def __init__(self, value):
        self.value = value

class ExplicitTrisect(BaseClass):
    def __init__(self, value):
        super(ExplicitTrisect, self).__init__(value)
        self.value /= 3

class AutomaticTrisect(BaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value)
        self.value /= 3

class ImplicitTrisect(BaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value /= 3

assert ExplicitTrisect(9).value == 3
assert AutomaticTrisect(9).value == 3
assert ImplicitTrisect(9).value == 3
```

- Only pass explicit parameters to `super` where you explicitly need to
  access a superclass’s implementation from within a child class
  - e.g. to wrap or reuse functionality

## Things to Remember

- Python’s MRO solves the problem of superclass initialisation order and
  diamond inheritance
- Use the `super` built-in function with zero arguments to initialise
  parent classes and methods
