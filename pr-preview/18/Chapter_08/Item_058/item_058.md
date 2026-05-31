# Item 58: Use Plain Attributes Instead of Setter and Getter Methods


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Other languages with tighter access controls tend to use the `getter`
  and `setter` idiom for configuring attributes
- Natural for people to try and repeat this pattern in python

``` python
class OldResistor:
    def __init__(self, ohms):
        self._ohms = ohms

    def get_ohms(self):
        return self._ohms

    def set_ohms(self, ohms):
        self._ohms = ohms


r0 = OldResistor(50e3)
print("Before:", r0.get_ohms())
r0.set_ohms(10e3)
print("After:", r0.get_ohms())

# incrementing the value
r0.set_ohms(r0.get_ohms() - 4e3)  # equivalent to ohms -= 4e3
assert r0.get_ohms() == 6e3
```

    Before: 50000.0
    After: 10000.0

- Not a pythonic pattern
- As seen above trying to combine with increment / decrement operators
  and other operations gets very awkward
- Getters and Setters are helpful for defining interfaces
  - Define boundaries
  - Encapsulate functionality
  - Validate usage
- These are important when we consider the evolution and maintenance of
  a class and/or interface
- In python always start with simple public attributes

``` python
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0


r = Resistor(50e3)
r.ohms = 10e3

print("Before:", r.ohms)
# incrementing
r.ohms += 5e3
print("After:", r.ohms)
```

    Before: 10000.0
    After: 15000.0

- If special behaviour is later needed this can be provided via the
  `@property` decorator (See [Item
  38](../../Chapter_05/Item_038/item_038.qmd))
- `@property` lets you associate a `setter` function with the attribute
- For example say we want to provide a version of the `Resistor` class
  such that the voltage and current obey Ohm’s Law
  - We can achieve this by using a property on `voltage` to synchronise
    the value of `current`
- To use a `@property` decorator properly, the getter and setter
  function being decorated must match the name of the attribute (here
  `voltage`)

``` python
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0


class VoltageResistor(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
        self._voltage = 0

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self._voltage / self.ohms


r = VoltageResistor(1e2)
print(f"Before: {r.current:.2f} amps")
r.voltage = 10  # uses the setter - looks like variable assignment
print(f"After: {r.current:.2f} amps")
```

    Before: 0.00 amps
    After: 0.10 amps

- Assigning to a property runs the setter, i.e. `r.voltage = 10` is
  equivalent to `r.voltage(10)` where `voltage` is the setter function
  - This leads to `current` being updated
- Specifying a setter for a property also allows you to run
  type-checking and value validation
- For example, we can ensure a value is positive such as the `ohms` for
  our `Resistor`

``` python
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0


class BoundedResistor(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError(f"Ohms must be > 0; got {ohms}")
        self._ohms = ohms


r = BoundedResistor(1e3)
print(f"Ohms are: {r.ohms}")
r.ohms = 0  # raises exception
```

    Ohms are: 1000.0

    ValueError: Ohms must be > 0; got 0
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[4], line 25
         23 r = BoundedResistor(1e3)
         24 print(f"Ohms are: {r.ohms}")
    ---> 25 r.ohms = 0  # raises exception

    Cell In[4], line 19, in BoundedResistor.ohms(self, ohms)
         16 @ohms.setter
         17 def ohms(self, ohms):
         18     if ohms <= 0:
    ---> 19         raise ValueError(f"Ohms must be > 0; got {ohms}")
         20     self._ohms = ohms

    ValueError: Ohms must be > 0; got 0

- The setter is called in the constructor too
  - Means we can’t construct an invalid object
  - Here `BoundedResistance.__init__` calls `Resistor.__init__` performs
    `self.ohms = ohms` which goes back to the `@ohms.setter` method from
    `BoundedResistor`
- Properties provide another mechanism for making attributes immutable
  (See [Item 56](../../Chapter_07/Item_056/item_056.qmd))
  - Say if we only want to have certain attributes fixed

``` python
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0


class FixedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if hasattr(self, "_ohms"):
            raise AttributeError("Ohms is immutable")
        self._ohms = ohms


r = FixedResistance(1e3)  # first assignment works fine
print(f"Ohms are: {r.ohms}")
r.ohms = 2e3  # fails because of immutable setter
```

    Ohms are: 1000.0

    AttributeError: Ohms is immutable
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[5], line 25
         23 r = FixedResistance(1e3)  # first assignment works fine
         24 print(f"Ohms are: {r.ohms}")
    ---> 25 r.ohms = 2e3  # fails because of immutable setter

    Cell In[5], line 19, in FixedResistance.ohms(self, ohms)
         16 @ohms.setter
         17 def ohms(self, ohms):
         18     if hasattr(self, "_ohms"):
    ---> 19         raise AttributeError("Ohms is immutable")
         20     self._ohms = ohms

    AttributeError: Ohms is immutable

- Make sure that getter’s and setters follow expected behaviour
- *Don’t* modify attributes (especially other attributes) in the getter
  - Leads to side effects
  - Hard to reason about

``` python
class Resistor:
    def __init__(self, ohms):
        self.voltage = 0
        self.current = 0
        self.ohms = ohms


class MysteryResistor(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        self.voltage = self._ohms * self.current
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        self._ohms = ohms


r = MysteryResistor(10)  # first assignment works fine
r.current = 0.1
print(f"Before: {r.voltage:.2f}")
print(f"Ohms: {r.ohms}")
print(f"After: {r.voltage:.2f}")
```

    Before: 0.00
    Ohms: 10
    After: 1.00

- When using getters and setters to enforce state constraints also make
  sure this is done in the setter (`@property.setter`)
- Avoid any other side effects that are not expected
  - e.g. module import, slow helper function calls, I/O, expensive
    database queries
- Users will see the property as any other data attribute
  - You should make it behave like one
- Use clearly named methods for any expensive, stateful or complex
  behaviours
- `@property` has one big shortcoming
  - methods for attributes can only be shared by subclasses
  - Unrelated classes can’t share the implementation
  - Descriptors (See [Item 60](../Item_060/item_060.qmd)) enable
    reusable property logic and many other use cases

## Things to Remember

- Define new class interfaces using simple public attributes
- Avoid getter and setter methods
  - Especially those called `get_attribute` and `set_attribute`
- Use `@property` to define special behaviour when attributes are
  accessed
- Follow the rule of least surprise and avoid odd side effects in
  `@property` methods
- Ensure that `@property` methods are fast
  - For slow or complex work use normal methods
  - Where there are unexpected side effects or heavy I/O definitely use
    methods
