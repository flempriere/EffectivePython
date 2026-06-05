# Item 109: Prefer Integration Tests over Unit Tests

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Testing is subject to as many different paradigms as software
  development itself
  1. Test-driven development,
  2. Property-based testing,
  3. Mutation testing,
  4. Code and branch coverage reporting

  - and more…
- The question is never when and can you write tests?
  - How much testing is enough?
  - *What* should tests verify?
- Test’s are insurance policies
  - They cannot prove code is correct, but they can catch incorrect code
- Test’s should verify *behaviour*, not *implementation*
  - Make’s it easy to identify change
  - Want to minimise the need to change the tests when we change the
    code
    - Ensures the test is still testing what should be tested and not
      just changed to ensure something passes
- Well-built tests make it easier to modify programs regardless of the
  language, not harder
- Testing can occur at different levels
  - *Unit tests*
    - Verify behaviours of specific code units e.g.
      - A class
      - A set of related functions
    - Useful when verifying a lot of edge cases
    - Typically fast to run (since small and contained)
    - Often need to use mock’s to emulate connected components (See
      [Item 111](../Item_111/item_111.qmd))
  - *Integration tests*
    - Verify that multiple components work together
    - Slower to run
      - Since testing more of the codebase
    - Typically also harder to write (See [Item
      110](../Item_110/item_110.qmd))
      - But since they test more natural boundaries can be more
        immutable to changes
    - Highly important in Python
      - Other languages can give some validation of boundaries using
        type checking
      - Python has no guarantees until runtime (See [Item
        3](../../Chapter_01/Item_003/item_003.qmd))
- Prefer writing integration tests
  - Write unit tests for edge cases or complex boundary conditions
  - Don’t *only* write unit tests
- For example, consider software that controls a toaster
  - User can specify a toast “level”
    - Needs a timer
    - timer is an external component
      - Should be able to be reset multiple times

``` python
import threading
import time


class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(
            0.1, min(120, self.doneness * 0.1)
        )  # time reduced for example simplicity

    def push_down(self):
        if self.hot:
            return
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()


class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()


# Demonstrative use
toaster = Toaster(ReusableTimer())
print("Initially hot:   ", toaster.hot)
toaster.doneness = 5
toaster.push_down()
print("After push down: ", toaster.hot)

time.sleep(1)
print("After time:  ", toaster.hot)
```

    Initially hot:    False
    After push down:  True
    Pop!
    After time:   False

- Might be tempted to write unit test’s for the `Toaster`
  - But would require us to mock out the timer (See [Item
    111](../Item_111/item_111.qmd))

``` python
%reset

from unittest import TestCase, main
from unittest.mock import Mock
import threading


# Toaster and Reusable Timer definitions
class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(
            0.1, min(120, self.doneness * 10)
        )  # time reduced for example simplicity

    def push_down(self):
        if self.hot:
            return
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()


class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()


# Testing


class ToasterUnitTest(TestCase):
    def test_start(self):
        timer = Mock(spec=ReusableTimer)
        toaster = Toaster(timer)
        toaster.push_down()
        self.assertTrue(toaster.hot)
        timer.countdown.assert_called_once_with(30, toaster.pop_up)

    def test_end(self):
        timer = Mock(spec=ReusableTimer)
        toaster = Toaster(timer)
        toaster.hot = True
        toaster.pop_up()
        self.assertFalse(toaster.hot)
        timer.end.assert_called_once()


main(argv=[""], exit=False)
```

    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.003s

    OK

    Pop!

    <unittest.main.TestProgram at 0x7f1d8c30be00>

- We’ll also then have to write unit tests for our `ReusableTimer` app

``` python
%reset

from unittest import TestCase, main, mock
import threading


# Toaster and Reusable Timer definitions
class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(
            0.1, min(120, self.doneness * 10)
        )  # time reduced for example simplicity

    def push_down(self):
        if self.hot:
            return
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()


class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()


# Testing


class ReuseableTimerUnitTest(TestCase):
    def test_countdown(self):
        my_func = lambda: None
        with mock.patch("threading.Timer"):
            timer = ReusableTimer()
            timer.countdown(0.1, my_func)
            threading.Timer.assert_called_once_with(0.1, my_func)
            timer.timer.start.assert_called_once()

    def test_end(self):
        my_func = lambda: None
        with mock.patch("threading.Timer"):
            timer = ReusableTimer()
            timer.countdown(0.1, my_func)
            timer.end()
            timer.timer.cancel.assert_called_once()


main(argv=[""], exit=False)
```

    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.003s

    OK

    <unittest.main.TestProgram at 0x7f1d8c372850>

- Since the `Toaster` and `ReusableTimer` are designed to be used
  together we can see we have to heavily mock the internals
- Arguably better to just test the two components together as an
  *integration test*

``` python
%reset

from unittest import TestCase, main
import threading


# Toaster and Reusable Timer definitions
class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(
            0.1, min(120, self.doneness * 10)
        )  # time reduced for example simplicity

    def push_down(self):
        if self.hot:
            return
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()


class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()


# Testing


class ToasterIntegrationTest(TestCase):
    def setUp(self):
        self.timer = ReusableTimer()
        self.toaster = Toaster(self.timer)
        self.toaster.doneness = 0

    def test_wait_finish(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)
        self.timer.timer.join()
        self.assertFalse(self.toaster.hot)

    def test_cancel_early(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)
        self.toaster.pop_up()
        self.assertFalse(self.toaster.hot)


main(argv=[""], exit=False)
```

    .

    Pop!

    .
    ----------------------------------------------------------------------
    Ran 2 tests in 0.103s

    OK

    Pop!

    <unittest.main.TestProgram at 0x7f1d8c372710>

- Test is shorter and more focused on the actual state being tested than
  the unit test implementations
- Focuses on the actual desired end-to-end rather than individual
  component behaviours in isolation
- Could argue the double attribute access to `timer.timer.join()` is a
  code smell that couples the test too much to the implementation
- No longer need to use the unit tests since they are encapsulated into
  the integration test
  - Might still be useful to unit test the range bounds of the `Toaster`
    `doneness` state

``` python
%reset

from unittest import TestCase, main
import threading


# Toaster and Reusable Timer definitions
class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(
            0.1, min(120, self.doneness * 10)
        )  # time reduced for example simplicity

    def push_down(self):
        if self.hot:
            return
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()


class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()


class DonenessUnitTest(TestCase):
    def setUp(self):
        self.toaster = Toaster(ReusableTimer())

    def test_min(self):
        self.toaster.doneness = 0
        self.assertEqual(0.1, self.toaster._get_duration())

    def test_max(self):
        self.toaster.doneness = 1000
        self.assertEqual(120, self.toaster._get_duration())


main(argv=[""], exit=False)
```

    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.002s

    OK

    <unittest.main.TestProgram at 0x7f1d8c32a650>

- We don’t have to mock out the `ReusableTimer` since we don’t use it’s
  functionality
- Try to avoid mocking when you can
  - Overuse of mocks is a code smell (See [Item
    112](../Item_112/item_112.qmd))
- Use integration tests as your main testing layer
  - Support with unit tests for self-contained edge cases
- The next step up from integration tests is system tests
  - Verify how programs communicate with each other, e.g.
    - Web clients
    - API endpoints
    - Mobile applications
    - Databases,
    - etc…

## Things to Remember

- Integration tests verify the behaviour of multiple components together
  - As opposed to unit tests which verify individual components
- Python’s highly dynamic nature means tests should focus on integration
  - Lack of compile time checks limits ability to verify components will
    communicate correctly
- Unit tests should be used to test self-contained edge cases or
  boundary conditions
