# Item 60: Use Descriptors for Reusable `@property` Methods


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Properties (See [Item 58](../Item_058/item_058.qmd) and [Item
  59](../Item_059/item_059.qmd)) are great, but by being locked to a
  class they limit reuse

- Decorated methods can’t be reused for multiple attributes

- Also can’t be used by unrelated classes

- For example, consider a class that validates a student’s homework
  grade ensuring it is a percentage

  - An `@property` approach is a natural solution here

``` python
class Homework:
    def __init__(self):
        self._grade = 0

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._grade = value


galileo = Homework()
galileo.grade = 95
print("Homework grade:", galileo.grade)
```

    Homework grade: 95

- Now consider we also want a graded exam
  1.  Each exam consisting of potentially multiple subjects
  2.  Each subject has a grade
- We can attempt to implement this in an identical way using properties

``` python
class Exam:
    def __init__(self):
        self._writing_grade = 0
        self._math_grade = 0

    @staticmethod
    def _check_grade(value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")

    @property
    def writing_grade(self):
        return self._writing_grade

    @writing_grade.setter
    def writing_grade(self, value):
        self._check_grade(value)
        self._writing_grade = value

    @property
    def math_grade(self):
        return self._math_grade

    @math_grade.setter
    def math_grade(self, value):
        self._check_grade(value)
        self._math_grade = value


test = Exam()
test.writing_grade = 80
test.math_grade = 90
print(f"Writing grade: {test.writing_grade}\nMath grade: {test.math_grade}")
```

    Writing grade: 80
    Math grade: 90

- This approach is frankly awful
- For each exam section we have to write out the `@property` getter and
  setter
  - Including rewriting effectively the same validation code
  - Every validation is calling out to `check_grade`
- The appropriate solution is to use a *descriptor*
  - The *descriptor protocol* defines how the language interprets
    attribute access
- A descriptor provides `__get__` and `__set__` methods
  - Allows us to reuse validation code
  - Reduces boilerplate
- Descriptors are better than mix-ins (See [Item
  54](../../Chapter_07/Item_054/item_054.qmd))
  - Let us reuse the same logic for multiple attributes in the one class
- We can reimplement our `Exam` class by first defining a `Grade` class
  to implement the descriptor protocol

``` python
class Grade:
    def __get__(self, instance, instance_type): ...

    def __set__(self, instance, value): ...


class Exam:
    # Class Attributes
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


exam = Exam()
exam.writing_grade = 40
print(exam.writing_grade)  # comes up as `None` since not implemented
```

    None

- How do you interpret the above?
- The assignment is interpreted as

``` python
Exam.__dict__["writing_grade"].__set__(exam, 40)
```

- The access is interpreted as

``` python
Exam.__dict__["writing_grade"].__get__(exam, Exam)
```

- Underlying implementation relies on `__getattribute__` for the object
  class (See [Item 61](../Item_061/item_061.qmd))
- If an `Exam` instance doesn’t have an attribute `writing_grade`,
  Python then checks for a class attribute on `Exam`
  - If this class attribute satisfies the descriptor protocol i.e. has
    `__get__` and `__set__`, the descriptor protocol is invoked
- Let us have a first attempt at implementing this descriptor

``` python
class Grade:
    def __init__(self):
        self._value = 0

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._value = value


class Exam:
    # Class Attributes
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


# Looking at the first instance
exam = Exam()
exam.writing_grade = 82
exam.science_grade = 99
print("Writing:", exam.writing_grade)
print("Science:", exam.science_grade)

# Looking at a  second instance

exam_2 = Exam()
exam_2.writing_grade = 75

print(f"Second {exam_2.writing_grade} is right")
print(f"First {exam.writing_grade} is wrong; should be 82")
```

    Writing: 82
    Science: 99
    Second 75 is right
    First 75 is wrong; should be 82

- So the `Grade` instance is shared across all `Exam` instances for the
  class attribute (e.g. `writing_grade`)
- `Grade` instance is created once at definition time, not at each
  instance
- Need to make `Grade` keep track of it’s value for all unique `Exam`
  instances
  - Save the per-instance state in a dictionary

``` python
class DictGrade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._values[instance] = value


class Exam:
    # Class Attributes
    math_grade = DictGrade()
    writing_grade = DictGrade()
    science_grade = DictGrade()


# Looking at the first instance
exam = Exam()
exam.writing_grade = 82
exam.science_grade = 99
print("Writing:", exam.writing_grade)
print("Science:", exam.science_grade)

# Looking at a  second instance

exam_2 = Exam()
exam_2.writing_grade = 75

print(f"Second {exam_2.writing_grade} is right")
print(f"First is {exam.writing_grade}; should be 82")
```

    Writing: 82
    Science: 99
    Second 75 is right
    First is 82; should be 82

- Implementation is simple and works
- *However* it leaks memory
  - Since the dictionary stores a reference to all instances of an
    `Exam` passed to `__set__` all `Exam` instances will always have at
    least one reference
  - Means that these `Exam` instances will never be cleaned up by the
    garbage collector
- Instead use the `__set_name__` special method for descriptors (See
  [Item 64](../Item_064/item_064.qmd))
  - Called on each descriptor instance after a class is defined
  - Name of the class attribute assigned to descriptor instance is
    supplied by Python
  - Can compute a per-object string to give a per-object attribute name
    - Can even make it protected
- Then have to update `__get__` and `__set__` to use this internal name
  to store and retrieve attribute data

``` python
class NamedGrade:
    def __set_name__(self, owner, name):
        self.internal_name = "_" + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        setattr(instance, self.internal_name, value)


class Exam:
    # Class Attributes
    math_grade = NamedGrade()
    writing_grade = NamedGrade()
    science_grade = NamedGrade()


# Looking at the first instance
exam = Exam()
exam.writing_grade = 82
exam.science_grade = 99
print("Writing:", exam.writing_grade)
print("Science:", exam.science_grade)

# Looking at a  second instance

exam_2 = Exam()
exam_2.writing_grade = 75

print(f"Second {exam_2.writing_grade} is right")
print(f"First is {exam.writing_grade}; should be 82")

print(
    f"Inspecting internal state of the Exam instances\n"
    f"First: {exam.__dict__}\n"
    f"Second: {exam_2.__dict__}"
)
```

    Writing: 82
    Science: 99
    Second 75 is right
    First is 82; should be 82
    Inspecting internal state of the Exam instances
    First: {'_writing_grade': 82, '_science_grade': 99}
    Second: {'_writing_grade': 75}

- Doesn’t leak memory
  - When an `Exam` is garbage collected all it’s attribute data is
    destroyed
  - Including those assigned by descriptors

## Things to Remember

- Reuse the behaviour and validation of `@property` methods by defining
  your own descriptor classes
- Use `__set_name__` along with `setattr` and `getattr` to assign data
  needed by descriptors in object instances
  - This avoids memory leaks
- Don’t worry about trying to understand the intricacies of how
  `__getattribute__` uses the descriptor protocol for getting and
  setting attributes
