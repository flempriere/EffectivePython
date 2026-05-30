# Item 113: Use `assertAlmostEqual` to Control Precision in Floating
Point Tests


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Floating point numbers supported in python are useful but beware their
  precision limitations (See [Item
  106](../../Chapter_12/Item_106/item_106.qmd))
- Mathematical code often needs to be checked for boundary conditions or
  other error cases (See [Item 109](../Item_109/item_109.qmd))
- Can be difficult to automate floating point tests
  - Since precision often cannot be predicted ahead of time
  - The following simple test fails as a result
    - Can’t represent $5/3$ exactly as a `float`
    - Passed expected value is insufficiently precise
      - In theory could then change the provided expected value to match
        what is expected
      - But don’t want to have to write a test, let it fail to work out
        the expected value, then fix it
        - Essentially we are using the code supposedly being tested to
          instead test the test
      - Precision is also then often overkill and hard to maintain
        - May change on different architectures
        - May change due to ordering of operations impacting rounding of
          intermediates

``` python
import unittest


class MyTestCase(unittest.TestCase):
    def test_equal(self):
        n = 5
        d = 3
        self.assertEqual(1.667, n / d)  # Raises


unittest.main(argv=[""], exit=False)
```

    F
    ======================================================================
    FAIL: test_equal (__main__.MyTestCase.test_equal)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_14122/1899314891.py", line 8, in test_equal
        self.assertEqual(1.667, n / d)  # Raises
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
    AssertionError: 1.667 != 1.6666666666666667

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    FAILED (failures=1)

    <unittest.main.TestProgram at 0x7fe098faaf90>

- For example, the two equivalent calculations below will actually give
  different answers due to rounding in the intermediates

``` python
print(5 / 3 * 0.1)
print(0.1 * 5 / 3)
```

    0.16666666666666669
    0.16666666666666666

- Often we instead want to test the value matches the expected result to
  a controlled level of precision
- In this case can use the `unittest.TestCase.assertAlmostEqual` method
  - Properly handles `NaN` and infinities
  - Minimises rounding errors
  - Can specify the level of precision such as number of decimal places

``` python
import unittest


class MyImprovedTestCase(unittest.TestCase):
    def test_equal(self):
        n = 5
        d = 3
        self.assertAlmostEqual(1.667, n / d, places=2)


unittest.main(argv=[""], exit=False)
```

    .F
    ======================================================================
    FAIL: test_equal (__main__.MyTestCase.test_equal)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_14122/1899314891.py", line 8, in test_equal
        self.assertEqual(1.667, n / d)  # Raises
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
    AssertionError: 1.667 != 1.6666666666666667

    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s

    FAILED (failures=1)

    <unittest.main.TestProgram at 0x7fe0a00be210>

- `places` is suitable for verifying numbers with a fractional part that
  are close to unit magnitude
  - Rounding behaviour and precision is harder to predict for larger or
    smaller quantities
  - Operations between floating point numbers of significantly different
    magnitudes are liable to lose precision

``` python
print(1e24 / 1.1e16)
print(1e24 / 1.101e16)
```

    90909090.9090909
    90826521.34423251

- The above values are “close”, but the difference is around $80,000$
  - May or may not matter depending on the required precision
- Can use the `delta` parameter to specify acceptable precision
  - `assertAlmostEqual` will then compare the absolute difference of the
    expected value and result
    - Fail’s if the absolute difference is greater than the `delta`

``` python
import unittest


class DeltaTestCase(unittest.TestCase):
    def test_equal(self):
        a = 1e24 / 1.1e16
        b = 1e24 / 1.101e16
        self.assertAlmostEqual(90.9e6, a, delta=0.1e6)
        self.assertAlmostEqual(90.9e6, b, delta=0.1e6)


unittest.main(argv=[""], exit=False)
```

    ..F
    ======================================================================
    FAIL: test_equal (__main__.MyTestCase.test_equal)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_14122/1899314891.py", line 8, in test_equal
        self.assertEqual(1.667, n / d)  # Raises
        ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
    AssertionError: 1.667 != 1.6666666666666667

    ----------------------------------------------------------------------
    Ran 3 tests in 0.002s

    FAILED (failures=1)

    <unittest.main.TestProgram at 0x7fe0a00be490>

- If you need to assert a false case, then consider using
  `unittest.TestCase.assertNotAlmostEqual`
- For more complex cases (such as relative tolerances) consider the
  `isclose` function from the `math` built-in library

## Things to Remember

- Rounding behaviour in floating point can mean that changing the order
  of operations changes the result
- Testing floating point values with equality ala `assertEqual` should
  always be avoided
- Use `assertAlmostEqual` or `assertNotAlmostEqual` when testing
  floating point values in a `unittest.TestCase` test.
  - You can specify a tolerance via the `places` or `delta` parameters
