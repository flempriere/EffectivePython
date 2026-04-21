# Item 29: Compose Classes Instead of Deeply Nesting Dictionaries, Lists
and Tuples


- [Notes](#notes)
  - [Refactoring to Classes](#refactoring-to-classes)
- [Things to Remember](#things-to-remember)

## Notes

- Dictionaries help maintain dynamic state
  - E.g. bookkeeping for an arbitrary key set
- This includes managing the internal state of an object
- For example, managing student grades
  - The set of student names is likely dynamic
  - We can use a lightweight class wrapper

``` python
class SimpleGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = []

    def report_grade(self, name, score):
        self._grades[name].append(score)

    def average_grade(self, name):
        grades = self._grades[name]
        return sum(grades) / len(grades)


# Example usage:
book = SimpleGradebook()
book.add_student("Issac Newton")
book.report_grade("Issac Newton", 90)
book.report_grade("Issac Newton", 95)
book.report_grade("Issac Newton", 85)

print(book.average_grade("Issac Newton"))
```

    90.0

- Over relying on Dictionaries, Lists and Sets can lead to code that is
  brittle
- E.g. Let’s say that our Gradebook now requires grades to be tracked
  per subject
  - We could nest dictionaries, i.e. the gradebook keys return a
    dictionary mapping subjects to grades
  - Use `defaultdict` to handle missing subjects in the inner dictionary

``` python
from collections import defaultdict


class BySubjectGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = defaultdict(list)

    def report_grade(self, name, subject, grade):
        subject_grades = self._grades[name]
        grade_list = subject_grades[subject]
        grade_list.append(grade)

    def average_grade(self, name):
        subject_grade = self._grades[name]
        total, count = 0, 0
        for grades in subject_grade.values():
            total += sum(grades)
            count += len(grades)
        return total / count


book = BySubjectGradebook()
book.add_student("Issac Newton")
book.report_grade("Issac Newton", "Math", 75)
book.report_grade("Issac Newton", "Math", 65)
book.report_grade("Issac Newton", "Gym", 90)
book.report_grade("Issac Newton", "Gym", 95)

print(book.average_grade("Issac Newton"))
```

    81.25

- Still manageable
- Can see that we’re starting to have to write some reasonably nested
  access patterns
- Let’s extend the class again
  - Now grades can have a weighting, (e.g. To make finals and midterms
    more important)
- We can make the inner dictionary now a mapping of subjects to a list
  of (grade, weight) tuples
- But now, the method signatures and the code is starting to get
  complex, and coupled to our implementation
  - And increasingly nested

``` python
from collections import defaultdict


class WeightedGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = defaultdict(list)

    def report_grade(self, name, subject, score, weight):
        subjects = self._grades[name]
        grades_for_subject = subjects[subject]
        grades_for_subject.append((score, weight))

    def average_grade(self, name):

        subjects = self._grades[name]

        score_sum, score_count = 0, 0
        for scores in subjects.values():
            subject_avg, total_weight = 0, 0
            for score, weight in scores:
                subject_avg += score * weight
                total_weight += weight

            score_sum += subject_avg / total_weight
            score_count += 1

        return score_sum / score_count


book = WeightedGradebook()
book.add_student("Issac Newton")
book.report_grade("Issac Newton", "Math", 75, 0.05)
book.report_grade("Issac Newton", "Math", 65, 0.15)
book.report_grade("Issac Newton", "Math", 70, 0.80)
book.report_grade("Issac Newton", "Gym", 100, 0.40)
book.report_grade("Issac Newton", "Gym", 85, 0.60)

print(book.average_grade("Issac Newton"))
```

    80.25

- At this point we probably want to be implementing a formal class
  hierarchy
- Key point,
  - Dictionaries and other collections are great for initial simple
    tasks
  - When requirements get more complex, consider a more complex
    implementation

### Refactoring to Classes

- Refactoring a topic in and off itself
- In this example we work bottom up
- First our grades are simple scores and weights
  - Probably overkill to wrap this in a class, so these can stay as
    tuples

``` python
grades = []

grades.append((95, 0.45))
grades.append((85, 0.55))

total = sum(score * weight for score, weight in grades)
total_weight = sum(weight for _, weight in grades)

average_grade = total / total_weight
print(average_grade)
```

    89.5

- The `_` in the `total_weight` assignment is a python convention for a
  discarded variable
  - For calculating the total weight we only care about the weight
    component of the tuple
- Tuples rely on positional accesses for their values
  - If we were to extend the tuple further, e.g. adding teacher notes,
    everywhere that we unpack the tuple would need to be updated to
    handle a three-element tuple

``` python
grades = []

grades.append((95, 0.45, "Great job"))
grades.append((85, 0.55, "Better next time"))

total = sum(score * weight for score, weight, _ in grades)
total_weight = sum(weight for _, weight, _ in grades)

average_grade = total / total_weight
print(average_grade)
```

    89.5

- If you find yourself extending a tuple repeatedly it’s a sign to
  consider a higher level structure like a class
  - `dataclass` from the `dataclasses` built-in module provides an easy
    way to define lightweight classes
  - You can additionally make them immutable (like a tuple) via the
    `frozen` attribute

``` python
from dataclasses import dataclass

@dataclass(frozen=True)
class Grade:
    score: int
    weight: float
```

- We’ll look at dataclasses in more detail later
  - Generally they are good for simple, typed objects that are largely
    just bundles of data attributes
  - Similar to the conventional `struct` in C-like languages
- The next level in the hierarchy is to handle subjects
  - Subjects group assignments together

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class Grade:
    score: int
    weight: float


class Subject:
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight
```

- This handles the final level of nesting
- Still have the mapping of a student’s name to a dictionary of all
  their subjects (here a class)
- We could then implement a `Student` class to handle to association of
  subjects to a student

``` python
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Grade:
    score: int
    weight: float


class Subject:
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight


class Student:
    def __init__(self):
        self._subjects = defaultdict(Subject)

    def get_subject(self, name):
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total +=  subject.average_grade()
            count += 1
        return total / count
```

- Last thing to do is update our grade book

``` python
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Grade:
    score: int
    weight: float


class Subject:
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight


class Student:
    def __init__(self):
        self._subjects = defaultdict(Subject)

    def get_subject(self, name):
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count


class Gradebook:
    def __init__(self):
        self._students = defaultdict(Student)

    def get_student(self, name):
        return self._students[name]


book = Gradebook()
newton = book.get_student("Issac Newton")
math = newton.get_subject("Math")
math.report_grade(75, 0.05)
math.report_grade(65, 0.15)
math.report_grade(70, 0.80)
gym = newton.get_subject("Gym")
gym.report_grade(100, 0.40)
gym.report_grade(85, 0.60)
print(newton.average_grade())
```

    80.25

- Code is longer
  - Due to the class definition boilerplate
- But much easier to read
  - Responsibilities and interfaces are clearly defined
- For backwards compatibility we could provide methods that match the
  old interface on the various classes

## Things to Remember

- Avoid dictionaries that store dictionaries, long tuples or other forms
  of complex nestings
- Use the `dataclasses` built-in module for lightweight, possibly
  immutable data containers that don’t need the overhead of a full class
  implementation
- Move bookkeeping code into multiple discrete classes when internal
  state management gets complicated
