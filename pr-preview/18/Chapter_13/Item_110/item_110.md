# Item 110: Isolate Tests from Each Other with `setUp`, `tearDown`,
`setUpModule` and `tearDownModule`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Often test’s (See [Item 108](../Item_108/item_108.qmd)) need a test
  environment to be configured before tests are run
  - Want this to be clean for each test
  - Sometimes called the *test harness*
- `unittest` supports this for the `TestCase` class via the `setUp` and
  `tearDown` methods
  - `setUp` called before each test method runs
  - `tearDown` called after each test method runs
- For example, if we have a test that needs to write some temporary
  files we might want an isolated test directory for each invocation

``` python
%reset

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main


class EnvironmentTest(TestCase):
    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_modify_file(self):
        with open(self.test_path / "data.bin", "w") as f:
            f.write("Hello, World!")


main(argv=[""], exit=False)
```

    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK

    <unittest.main.TestProgram at 0x7f6f4067eba0>

- For integration tests (See [Item 109](../Item_109/item_109.qmd)) it
  can be expensive to set up the environment for *every* individual test
  - e.g. If we need to connect to a database and load some data
- `unittest` allows module-level test configuration of the test harness
  - Configured once
  - All `TestCase` classes can then run with the set up harness
  - Test harness is then torn down once

``` python
%reset

from unittest import TestCase, main


def setupModule():
    print("* Module setup")


def tearDownModule():
    print("* Module clean-up")


class IntegrationTest(TestCase):
    def setUp(self):
        print("* Test setup")

    def tearDown(self):
        print("* Test clean-up")

    def test_end_to_to_end1(self):
        print("* Test 1")

    def test_end_to_end2(self):
        print("* Test 2")


main(argv=[""], exit=False)
```

    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s

    OK

    * Test setup
    * Test 2
    * Test clean-up
    * Test setup
    * Test 1
    * Test clean-up
    * Module clean-up

    <unittest.main.TestProgram at 0x7f6f406e6490>

- `setUpModule` is run once by `unittest` once *before* any `setUp`
- `tearDownModule` is run once *after* every `tearDown`

## Things to Remember

- `setUp` and `tearDown` are methods of the `unittest.TestCase` class
  that can configure the test environment before it’s test methods are
  run
  - Ensure’s tests are isolated from each other
  - Sets up a clean test environment
- For integration tests use the `setUpModule` and `tearDownModule`
  module-level functions to manage the test-harness for the lifetime of
  a test module
  - Is then used by all `TestCase` subclasses it contains
