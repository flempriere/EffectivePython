# Item 96: Consider Extension Modules to Maximise Performance and
Ergonomics


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- An alternative to `ctypes` (See [Item 95](../Item_095/item_095.qmd))
  is to write a C Extension module
- Can directly use the Python API
- Let’s you use python features, e.g.
  - OOP
  - Protocols
  - Reference-counting
  - etc…
- Extension modules let the calling code be more Pythonic
- Creating an extension module is much more complicated than using
  `ctypes`
  - Have to understand the Python C API
- We’ll demonstrate by again implementing our `dot_product` function
  (See [Item 94](../Item_094/item_094.qmd))
- As usual start by providing a header declaration

``` c
/* extension.h */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *dot_product(PyObject *self, PyObject *args);
```

- Next need to provide an implementation

``` c
/* extension.c */
#include "extension.h"

PyObject *dot_product(PyObject *self, PyObject *args) {
    PyObject *left, *right;
    if (!PyArg_ParseTuple(args, "OO", &left, *right)) {
        return NULL;
    }
    if (!PyList_Check(left) || !PyList_Check(right)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be lists");
        return NULL;
    }

    Py_ssize_t left_length = PyList_Size(left);
    Py_ssize_t right_length = PyList_Size(right);

    if (left_length == -1 || right_length == -1) {
        return NULL;
    }

    if (left_length != right_length) {
        PyErr_SetString(PyExc_ValueError, "Lists must be same length");
        return NULL;
    }

    double result = 0;

    for (Py_ssize_t i = 0; i < left_length; i++) {
        PyObject *left_item = PyList_GET_ITEM(left, i);
        PyObject *right_item = PyList_GET_ITEM(right, i);

        double left_double = PyFloat_AsDouble(left_item);
        double right_double = PyFloat_AsDouble(right_item);

        if (PyErr_Occurred()) {
            return NULL;
        }

        result += left_double * right_double;
    }

    return PyFloat_FromDouble(result);
}
```

- The implementation is already longer than the equivalent `ctypes`
  function
  - There’s some additional boilerplate to configure the extension
    module
  - Also initialises it

``` c
/* init.c */
#include "extension.h"

static PyMethodDef my_extension_methods[] = {
    {
        "dot_product",
        dot_product,
        METH_VARARGS,
        "Compute dot product",
    },
    {
        NULL,
        NULL,
        0,
        NULL,
    },
};

static struct PyModuleDef my_extension = {
    PyModuleDef_HEAD_INIT,
    "my_extension",
    "My C-extension Module",
    -1,
    my_extension_methods,
};

PyMODINIT_FUNC
PyInit_extension(void) {
  return PyModule_Create(&my_extension);
}
```

- Now need to compile C code into a native library
  - Can then be dynamically loaded into the CPython interpreter
- Can do so via a simple `setup.py` configuration file

``` python
# setup.py

from setuptools import Extension, setup

setup(
    name="extension",
    ext_modules=[
        Extension(
            name="extension",
            sources=["init.c", "extension.c"],
        ),
    ],
)
```

- We can then use this to install the extension into our virtual
  environment
  - By running the following from the folder containing our extension
    module

``` shell
uv pip install -e .
```

> [!IMPORTANT]
>
> There are many methods for packaging projects and extension modules.
> The process outlined above almost certainly isn’t the best approach,
> but works for the purposes of getting this example together. Python
> packaging is in fact such a hot debate of how best to do it that there
> is an entire organisation and site dedicated to documenting the best
> way to do python packaging - [The Official Python Packaging
> Authority](https://www.pypa.io/en/latest/)

> [!CAUTION]
>
> The above steps install our module as an *editable* install in our
> local virtual environment. This is a good way to deal with a local
> package that is being actively developed. In general avoid installing
> packages into the system python (non-virtual environment), but doubly
> so for those packages that are ephemeral or active development.

- We can now test our module

``` python
import unittest
import extension


class ExtensionTest(unittest.TestCase):
    def test_empty(self):
        result = extension.dot_product([], [])
        self.assertAlmostEqual(0, result)

    def test_positive_result(self):
        result = extension.dot_product([3, 4, 5], [-1, 9, -2.5])
        self.assertAlmostEqual(20.5, result)

    def test_zero_result(self):
        result = extension.dot_product([0, 0, 0], [1, 1, 1])
        self.assertAlmostEqual(0, result)

    def test_negative_result(self):
        result = extension.dot_product([-1, -1, -1], [1, 1, 1])
        self.assertAlmostEqual(-3, result)

    def test_non_lists(self):
        with self.assertRaises(TypeError) as context:
            extension.dot_product([1, 2], (3, 4))
        self.assertEqual("Both arguments must be lists", str(context.exception))

    def test_mismatched_size(self):
        with self.assertRaises(ValueError) as context:
            extension.dot_product([1], [2, 3])
        self.assertEqual("Lists must be the same length", str(context.exception))

        with self.assertRaises(ValueError) as context:
            extension.dot_product([1, 2], [3])
        self.assertEqual("Lists must be the same length", str(context.exception))

    def test_not_floatable(self):
        with self.assertRaises(TypeError) as context:
            extension.dot_product(["bad"], [1])
        self.assertEqual("must be real number, not str", str(context.exception))


unittest.main(argv=[""], verbosity=2, exit=False)
```

    test_empty (__main__.ExtensionTest.test_empty) ... ok
    test_mismatched_size (__main__.ExtensionTest.test_mismatched_size) ... ok
    test_negative_result (__main__.ExtensionTest.test_negative_result) ... ok
    test_non_lists (__main__.ExtensionTest.test_non_lists) ... ok
    test_not_floatable (__main__.ExtensionTest.test_not_floatable) ... ok
    test_positive_result (__main__.ExtensionTest.test_positive_result) ... ok
    test_zero_result (__main__.ExtensionTest.test_zero_result) ... ok

    ----------------------------------------------------------------------
    Ran 7 tests in 0.007s

    OK

    <unittest.main.TestProgram at 0x7fecd4e7ee40>

- Compared to `ctypes` there is a lot of overhead in this implementation
  - However the interface appears more pythonic
- However, we’ve still written quite a restrictive API under the hood
  - Expects to receive lists of equal length containing floats
    - Does not support duck-typing
- So if needing strongly typed interfaces, probably better to stick with
  `ctypes`
  - But can use the extension API to use pythonic features
- We’ll rewrite the extension module to instead use the iterator and
  number protocols
  - Adds about 50% more code than the original implementation
  - But, provides a very pythonic interface
  - We use `PyObject_GetIter` and `PyIter_Next` to support iterators
    - Let’s us use tuples, lists, generators etc.(See [Item
      21](../../Chapter_03/Item_021/item_021.qmd))
  - Using `PyNumber_Multiply` and `PyNumber_Add` lets us work with any
    object that behaves like a number (See [Item
    57](../../Chapter_07/Item_057/item_057.qmd))

``` c
/* dot_product.c */
#include "extension_2.h"

PyObject *dot_product(PyObject *self, PyObject *args) {
    PyObject *left, *right;
    if (!PyArg_ParseTuple(args, "OO", &left, &right)) {
        return NULL;
    }
    PyObject *left_iter = PyObject_GetIter(left);
    if (left_iter == NULL) {
        return NULL;
    }
    PyObject *right_iter = PyObject_GetIter(right);
    if (right_iter == NULL) {
        Py_DECREF(left_iter);
        return NULL;
    }

    PyObject *left_item = NULL;
    PyObject *right_item = NULL;
    PyObject *multiplied = NULL;
    PyObject *result = PyLong_FromLong(0);

    while (1) {
        Py_CLEAR(left_item);
        Py_CLEAR(right_item);
        Py_CLEAR(multiplied);
        left_item = PyIter_Next(left_iter);
        right_item = PyIter_Next(right_iter);

        if (left_item == NULL && right_item == NULL) {
            break;
        }
        else if (left_item == NULL || right_item == NULL) {
            PyErr_SetString(PyExc_ValueError, "Arguments had unequal length");
            break;
        }

        multiplied = PyNumber_Multiply(left_item, right_item);
        if (multiplied == NULL) {
            break;
        }

        PyObject *added = PyNumber_Add(result, multiplied);
        if (added == NULL) {
            break;
        }

        Py_CLEAR(result);
        result = added;
    }

    Py_CLEAR(left_item);
    Py_CLEAR(right_item);
    Py_CLEAR(multiplied);
    Py_CLEAR(left_iter);
    Py_CLEAR(right_iter);

    if (PyErr_Occurred()) {
        Py_CLEAR(result);
        return NULL;
    }

    return result;
}
```

- A complication is that we have to manually manage our reference counts
  - Also need to propagate errors properly
  - Handle borrowed references
- We can then set-up tests for the module

``` python
import unittest
import extension2


class Extension2Test(unittest.TestCase):
    def test_decimals(self):
        import decimal

        a = [decimal.Decimal(1), decimal.Decimal(2)]
        b = [decimal.Decimal(3), decimal.Decimal(4)]
        result = extension2.dot_product(a, b)
        self.assertEqual(11, result)

    def test_not_lists(self):
        result1 = extension2.dot_product(
            (1, 2),
            [3, 4],
        )
        result2 = extension2.dot_product(
            [1, 2],
            (3, 4),
        )
        result3 = extension2.dot_product(
            range(1, 3),
            range(3, 5),
        )
        self.assertAlmostEqual(11, result1)
        self.assertAlmostEqual(11, result2)
        self.assertAlmostEqual(11, result3)

    def test_empty(self):
        result = extension2.dot_product([], [])
        self.assertAlmostEqual(0, result)

    def test_positive_result(self):
        result = extension2.dot_product(
            [3, 4, 5],
            [-1, 9, -2.5],
        )
        self.assertAlmostEqual(20.5, result)

    def test_zero_result(self):
        result = extension2.dot_product(
            [0, 0, 0],
            [1, 1, 1],
        )
        self.assertAlmostEqual(0, result)

    def test_negative_result(self):
        result = extension2.dot_product(
            [-1, -1, -1],
            [1, 1, 1],
        )
        self.assertAlmostEqual(-3, result)

    def test_mismatched_size(self):
        with self.assertRaises(ValueError) as context:
            extension2.dot_product([1], [2, 3])
        self.assertEqual("Arguments had unequal length", str(context.exception))

        with self.assertRaises(ValueError) as context:
            extension2.dot_product([1, 2], [3])
        self.assertEqual("Arguments had unequal length", str(context.exception))

    def test_not_floatable(self):
        with self.assertRaises(TypeError) as context:
            extension2.dot_product(["bad"], [1])
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )


unittest.main(argv=[""], verbosity=2, exit=False)
```

    test_decimals (__main__.Extension2Test.test_decimals) ... ok
    test_empty (__main__.Extension2Test.test_empty) ... ok
    test_mismatched_size (__main__.Extension2Test.test_mismatched_size) ... ok
    test_negative_result (__main__.Extension2Test.test_negative_result) ... ok
    test_not_floatable (__main__.Extension2Test.test_not_floatable) ... ok
    test_not_lists (__main__.Extension2Test.test_not_lists) ... ok
    test_positive_result (__main__.Extension2Test.test_positive_result) ... ok
    test_zero_result (__main__.Extension2Test.test_zero_result) ... ok
    test_empty (__main__.ExtensionTest.test_empty) ... ok
    test_mismatched_size (__main__.ExtensionTest.test_mismatched_size) ... ok
    test_negative_result (__main__.ExtensionTest.test_negative_result) ... ok
    test_non_lists (__main__.ExtensionTest.test_non_lists) ... ok
    test_not_floatable (__main__.ExtensionTest.test_not_floatable) ... ok
    test_positive_result (__main__.ExtensionTest.test_positive_result) ... ok
    test_zero_result (__main__.ExtensionTest.test_zero_result) ... ok

    ----------------------------------------------------------------------
    Ran 15 tests in 0.014s

    OK

    <unittest.main.TestProgram at 0x7fecd4d111d0>

- The flexibility and extensibility of above provides good ergonomics
  - Would have to reinvent a lot of the Python machinery to reimplement
    this in basic C

## Things to Remember

- Extension modules are written in C
  - Allow execution at native speed
  - Can use the Python API to hook into python features
- Python API does introduce some difficulties
  - Manual memory management
  - Error Propagation
  - Hard to learn and difficult to get right
- C Extensions provide value when they enable reuse or support for
  Python’s built-in protocols and data types
  - Difficult to replicate in raw C
