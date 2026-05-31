# Item 108: Verify Related Behaviours in `TestCase` Subclasses


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `unittest` is the built-in testing module for python
  - Similar to the Java ecosystem’s `Junit` testing framework
- Consider the following utility code to be tested

``` python
def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"Must supply str or bytes, found: {data}")
```

- Normally tests are then defined in a second file
  - For demonstration we’ll be doing everything in the notebook
  - Typically named either `test_util` or `util_test` etc.

``` python
from unittest import TestCase, main


# utils functionality
def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"Must supply str or bytes, found: {data}")


# Testing code


class UtilsTestCase(TestCase):
    def test_to_str_bytes(self):
        self.assertEqual("hello", to_str(b"hello"))

    def test_to_str_str(self):
        self.assertEqual("hello", to_str("hello"))

    def test_failing(self):
        self.assertEqual("incorrect", to_str("hello"))


main(argv=[""], exit=False)
```

    F..
    ======================================================================
    FAIL: test_failing (__main__.UtilsTestCase.test_failing)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/1261816152.py", line 25, in test_failing
        self.assertEqual("incorrect", to_str("hello"))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: 'incorrect' != 'hello'
    - incorrect
    + hello


    ----------------------------------------------------------------------
    Ran 3 tests in 0.002s

    FAILED (failures=1)

    <unittest.main.TestProgram at 0x7fe4c0776ba0>

- One can then run the test file via

``` shell
uv run test_util.py
```

- For us we run the cell above directly
- Two of the tests pass
  - We get some error output indicating a test has failed
- Test’s are organised via `TestCase` subclasses
  - Tests are methods beginning with `test`
- Any test method that runs without raising an exception is regarded to
  have passed (See [Item 81](../../Chapter_10/Item_081/item_081.qmd))
- Even if one test fails, all remaining tests should still run
- To run a specific test it can be specified directly via the command
  line

``` shell
uv run test_util.py UtilsTestCase.test_to_str_bytes
```

- Debugger can also be invoked directly in test methods for
  introspection (See [Item 114](../Item_114/item_114.qmd))
- `TestCase` provides assertion methods for simplifying asserts
  - `AssertEqual` for equality
  - `AssertTrue` for truthfulness
  - `AssertAlmostEqual` for imprecise floating point (See [Item
    113](../Item_113/item_113.qmd))
- As always you should [read the
  docs](https://docs.python.org/3/library/unittest.html)
  - Prefer them over a raw `assert`
  - They will provide more contextual information for understanding why
    a test case has failed

``` python
from unittest import TestCase, main
# Testing code


class AssertTestCase(TestCase):
    def test_assert_helper(self):
        expected = 12
        found = 2 * 5
        self.assertEqual(expected, found)

    def test_assert_statement(self):
        expected = 12
        found = 2 * 5
        assert found == expected


main(argv=[""], exit=False)
```

    FFF..
    ======================================================================
    FAIL: test_assert_helper (__main__.AssertTestCase.test_assert_helper)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 9, in test_assert_helper
        self.assertEqual(expected, found)
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    AssertionError: 12 != 10

    ======================================================================
    FAIL: test_assert_statement (__main__.AssertTestCase.test_assert_statement)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 14, in test_assert_statement
        assert found == expected
               ^^^^^^^^^^^^^^^^^
    AssertionError

    ======================================================================
    FAIL: test_failing (__main__.UtilsTestCase.test_failing)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/1261816152.py", line 25, in test_failing
        self.assertEqual("incorrect", to_str("hello"))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: 'incorrect' != 'hello'
    - incorrect
    + hello


    ----------------------------------------------------------------------
    Ran 5 tests in 0.003s

    FAILED (failures=3)

    <unittest.main.TestProgram at 0x7fe4c07e2490>

- If we want to verify that a method *does* raise an exception we can
  use the `assertRaises`
  - Can also be used as a context manager (See [Item
    82](../../Chapter_10/Item_082/item_082.qmd))
  - Gives a similar interface to a `try/except` block

``` python
from unittest import TestCase, main


# utils functionality
def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"Must supply str or bytes, found: {data}")


# Testing code


class UtilsErrorTestCase(TestCase):
    def test_to_str_bad(self):
        with self.assertRaises(TypeError):
            to_str(object())

    def test_to_str_bad_encoding(self):
        with self.assertRaises(UnicodeDecodeError):
            to_str(b"\xfa\xfa")


main(argv=[""], exit=False)
```

    FF..F..
    ======================================================================
    FAIL: test_assert_helper (__main__.AssertTestCase.test_assert_helper)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 9, in test_assert_helper
        self.assertEqual(expected, found)
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    AssertionError: 12 != 10

    ======================================================================
    FAIL: test_assert_statement (__main__.AssertTestCase.test_assert_statement)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 14, in test_assert_statement
        assert found == expected
               ^^^^^^^^^^^^^^^^^
    AssertionError

    ======================================================================
    FAIL: test_failing (__main__.UtilsTestCase.test_failing)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/1261816152.py", line 25, in test_failing
        self.assertEqual("incorrect", to_str("hello"))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: 'incorrect' != 'hello'
    - incorrect
    + hello


    ----------------------------------------------------------------------
    Ran 7 tests in 0.004s

    FAILED (failures=3)

    <unittest.main.TestProgram at 0x7fe4c07e2710>

- Normal helper methods can be defined for complex logic
  - Just don’t name the method starting with `test`
- Can use the `fail` method to clarify why a test fails
  - e.g. if an invariant is violated

``` python
from unittest import TestCase, main


def sum_squares(values):
    cumulative = 0
    for value in values:
        cumulative += value**2
        yield cumulative


class HelperTestCase(TestCase):
    def verify_complex_case(self, values, expected):
        expect_it = iter(expected)
        found_it = iter(sum_squares(values))
        test_it = zip(expect_it, found_it, strict=True)

        for i, (expect, found) in enumerate(test_it):
            if found != expect:
                self.fail(f"Index {i} is wrong: ", f"{found} != {expect}")

    def test_too_short(self):
        values = [1.1, 2.2]
        expected = [1.1**2]
        self.verify_complex_case(values, expected)

    def test_too_long(self):
        values = [1.1, 2.2]
        expected = [1.1**2, 1.1**2 + 2.2**2, 0]
        self.verify_complex_case(values, expected)

    def test_wrong_results(self):
        values = [1.1, 2.2, 3.3]
        expected = [
            1.1**2,
            1.1**2 + 2.2**2,
            1.1**2 + 2.2**2 + 3.3**2 + 4.4**2,
        ]
        self.verify_complex_case(values, expected)


main(argv=[""], exit=False)
```

    FFEEE..F..
    ======================================================================
    ERROR: test_too_long (__main__.HelperTestCase.test_too_long)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 29, in test_too_long
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 17, in verify_complex_case
        for i, (expect, found) in enumerate(test_it):
                                  ~~~~~~~~~^^^^^^^^^
    ValueError: zip() argument 2 is shorter than argument 1

    ======================================================================
    ERROR: test_too_short (__main__.HelperTestCase.test_too_short)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 24, in test_too_short
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 17, in verify_complex_case
        for i, (expect, found) in enumerate(test_it):
                                  ~~~~~~~~~^^^^^^^^^
    ValueError: zip() argument 2 is longer than argument 1

    ======================================================================
    ERROR: test_wrong_results (__main__.HelperTestCase.test_wrong_results)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 38, in test_wrong_results
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 19, in verify_complex_case
        self.fail(f"Index {i} is wrong: ", f"{found} != {expect}")
        ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    TypeError: TestCase.fail() takes from 1 to 2 positional arguments but 3 were given

    ======================================================================
    FAIL: test_assert_helper (__main__.AssertTestCase.test_assert_helper)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 9, in test_assert_helper
        self.assertEqual(expected, found)
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    AssertionError: 12 != 10

    ======================================================================
    FAIL: test_assert_statement (__main__.AssertTestCase.test_assert_statement)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 14, in test_assert_statement
        assert found == expected
               ^^^^^^^^^^^^^^^^^
    AssertionError

    ======================================================================
    FAIL: test_failing (__main__.UtilsTestCase.test_failing)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/1261816152.py", line 25, in test_failing
        self.assertEqual("incorrect", to_str("hello"))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: 'incorrect' != 'hello'
    - incorrect
    + hello


    ----------------------------------------------------------------------
    Ran 10 tests in 0.007s

    FAILED (failures=3, errors=3)

    <unittest.main.TestProgram at 0x7fe4c0794fc0>

- A good pattern is *one* `TestCase` subclass for each set of related
  tests
  - e.g. if a function has many edge cases it get’s it’s own class
- For simple functions one test case per module may be a better
  organisation
- Often one-to-one matching of a `TestCase` to a basic class and it’s
  methods (See [Item 109](../Item_109/item_109.qmd))
- `subTest` helper method can be used to reduce boilerplate for multiple
  tests
  - Helpful when writing data-driven tests
  - Can continue to run further tests after one fails (See [Item
    110](../Item_110/item_110.qmd))
    - similar to how different `test` methods in the same `TestCase`
      continue to run even after failure

``` python
from unittest import TestCase, main


# utils functionality
def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"Must supply str or bytes, found: {data}")


class DataDrivenTestCase(TestCase):
    def test_good(self):
        good_cases = [
            (b"my bytes", "my bytes"),
            ("no error", b"no error"),  # this one fails
            ("other str", "other str"),
        ]

        for value, expected in good_cases:
            with self.subTest(value):
                self.assertEqual(expected, to_str(value))

    def test_bad(self):
        bad_cases = [
            (object(), TypeError),
            (b"\xfa\xfa", UnicodeDecodeError),
        ]
        for value, exception in bad_cases:
            with self.subTest(value):
                with self.assertRaises(exception):
                    to_str(value)


main(argv=[""], exit=False)
```

    FF.FEEE..F..
    ======================================================================
    ERROR: test_too_long (__main__.HelperTestCase.test_too_long)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 29, in test_too_long
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 17, in verify_complex_case
        for i, (expect, found) in enumerate(test_it):
                                  ~~~~~~~~~^^^^^^^^^
    ValueError: zip() argument 2 is shorter than argument 1

    ======================================================================
    ERROR: test_too_short (__main__.HelperTestCase.test_too_short)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 24, in test_too_short
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 17, in verify_complex_case
        for i, (expect, found) in enumerate(test_it):
                                  ~~~~~~~~~^^^^^^^^^
    ValueError: zip() argument 2 is longer than argument 1

    ======================================================================
    ERROR: test_wrong_results (__main__.HelperTestCase.test_wrong_results)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2356407664.py", line 38, in test_wrong_results
        self.verify_complex_case(values, expected)
        ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
      File "/tmp/ipykernel_13698/2356407664.py", line 19, in verify_complex_case
        self.fail(f"Index {i} is wrong: ", f"{found} != {expect}")
        ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    TypeError: TestCase.fail() takes from 1 to 2 positional arguments but 3 were given

    ======================================================================
    FAIL: test_assert_helper (__main__.AssertTestCase.test_assert_helper)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 9, in test_assert_helper
        self.assertEqual(expected, found)
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    AssertionError: 12 != 10

    ======================================================================
    FAIL: test_assert_statement (__main__.AssertTestCase.test_assert_statement)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/2536451551.py", line 14, in test_assert_statement
        assert found == expected
               ^^^^^^^^^^^^^^^^^
    AssertionError

    ======================================================================
    FAIL: test_good (__main__.DataDrivenTestCase.test_good) [no error]
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/3680052845.py", line 24, in test_good
        self.assertEqual(expected, to_str(value))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: b'no error' != 'no error'

    ======================================================================
    FAIL: test_failing (__main__.UtilsTestCase.test_failing)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_13698/1261816152.py", line 25, in test_failing
        self.assertEqual("incorrect", to_str("hello"))
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: 'incorrect' != 'hello'
    - incorrect
    + hello


    ----------------------------------------------------------------------
    Ran 12 tests in 0.008s

    FAILED (failures=4, errors=3)

    <unittest.main.TestProgram at 0x7fe4c0795f30>

- `unittest` is a powerful framework
  - However it does it have it’s limits
  - E.g. it’s java-style focus on OOP and naming conventions
- When you outgrow `unittest` consider
  [`pytest`](https://docs.pytest.org/en/stable/)
  - Community-developed test framework
    - Very popular
  - Uses a more functional style
  - Has a large number of extensions and plugins to provide more testing
    power

## Things to Remember

- Tests can be created using the `unittest` built-in framework
  - Subclass the `TestCase` class
  - Define one method per behaviour being tested
    - It’s name must start with `test`
- Use helper methods defined by `TestCase` such as `assertEqual` to
  confirm expected behaviours and get meaningful output when tests fail
  - Prefer them over the built-in `assert` function
- Use the `SubTest` helper method to write data-driven tests with
  reduced boilerplate
