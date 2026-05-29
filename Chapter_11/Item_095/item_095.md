# Item 95: Consider `ctypes` to Rapidly Integrate with Native Libraries


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `ctypes` is a built-in for calling native libraries from Python
  - Native libraries must export their functions using the C ABI /
    calling convention
- `ctypes` has two main benefits
  1.  Can use `ctypes` to glue different systems together via Python
  2.  Provides a path to optimise a python program by replacing
      components with a native implementation
- Consider again our `dot_product` function from before (See [Item
  94](../Item_094/item_094.qmd))

``` python
def dot_product(a, b):
    result = 0
    for i, j in zip(a, b):
        result += i * j
    return result


print(dot_product([1, 2], [3, 4]))
```

    11

- We could provide a simple C implementation, first defining a header
  interface

``` c
/* library.h */
extern double dot_product(int length, double* a, double* b);
```

- Then define our implementation
  - And compile the result

``` c
/* library.c */
/* Simple Library demonstrating ctypes in python */

#include "library.h"

double dot_product(int length, double *a, double *b) {
  double result = 0;
  for (int i = 0; i < length; i++) {
    result += a[i] * b[i];
  }
  return result;
}
```

> [!IMPORTANT]
>
> Compilation of libraries can be a relatively involved process. There
> are no guarantees that the provided library will work on your machine.
> You may have to compile the library yourself and update the program
> below to work with the new library.

- Using our library function is relatively involved
  - We’ll demonstrate below

``` python
import ctypes
import pathlib

# Set up the library
library_path = "./library.lib"
my_library = ctypes.cdll.LoadLibrary(library_path)


print(my_library.dot_product)
my_library.dot_product.restype = ctypes.c_double

vector_ptr = ctypes.POINTER(ctypes.c_double)
my_library.dot_product.argtypes = (ctypes.c_int, vector_ptr, vector_ptr)

size = 3
vector3 = ctypes.c_double * size
a = vector3(1.0, 2.5, 3.5)
b = vector3(-7, 4, -12.1)

result = my_library.dot_product(
    3, ctypes.cast(a, vector_ptr), ctypes.cast(b, vector_ptr)
)
print(result)
```

    <_FuncPtr object at 0x7fd608718230>
    -39.35

- We can find the `dot_product` function as an attribute of the
  `my_library`
  - This is the loaded object representing the library
  - We can see that it is a function pointer
- Wrapping the imported function as a `ctypes.CFUNCTYPE` object can lead
  to broken behaviour
  - The function will implicitly try and perform type conversions
  - Best to directly assign `restype` and `argtypes` attributes
    - Assign the matching `ctype` that matches the function signature
    - For the `dot_product` it returns a double and accepts an integer,
      and two pointers to doubles
      - We define `vector_ptr` to obfuscate the pointer to a double
- Now we have to call our function
  - Define a variable `vector3` which a type that holds three doubles
    - i.e. this is an array type
  - Then create two of these arrays
  - Can then finally call our `dot_product` as a python function
    - Have to use `ctypes.cast` to ensure both arrays are properly
      passed as pointers to doubles
      - Ensures they match the C calling convention
  - The return value is automatically cast back to a python type
- The `ctypes` module obviously has very poor ergonomics
  - Not very Pythonic
- We can obfuscate a lot of the complexity by using a python wrapper
  function

``` python
import ctypes
import pathlib

# Set up the library
"./library.lib"
my_library = ctypes.cdll.LoadLibrary(library_path)

# Setup dot product library function
vector_ptr = ctypes.POINTER(ctypes.c_double)
my_library.dot_product.restype = ctypes.c_double
my_library.dot_product.argtypes = (ctypes.c_int, vector_ptr, vector_ptr)


# Provide Python Wrapper
def dot_product(a, b):
    size = len(a)
    assert len(b) == size, "a and b must have the same length"
    vector = ctypes.c_double * size

    a_vector = vector(*a)
    b_vector = vector(*b)
    result = my_library.dot_product(
        size, ctypes.cast(a_vector, vector_ptr), ctypes.cast(b_vector, vector_ptr)
    )
    return result


result = dot_product([1.0, 2.5, 3.5], [-7, 4, -12.1])
print(result)
```

    -39.35

- Alternatively one can use the Python C Extension API (See [Item
  96](../Item_096/item_096.qmd))
  - Provides a more pythonic interface
  - Less set-up required at runtime
- However, `ctypes` provides some advantages
  - Pointer values held with `ctypes` will be freed automatically once
    reference counts go to zero
    - C extension modules must manually handle the memory for C pointers
      and reference count Python objects
  - Calling a function via `ctypes` automatically releases the GIL while
    in the native function
    - Other python threads can then progress (See [Item
      68](../../Chapter_09/Item_068/item_068.qmd))
    - For C extension modules the GIL must be handled explicitly
      - Limited functionality without the lock
  - `ctypes` simply requires a path to a dynamic library or shared
    object
    - Compilation can be done separate to the python runtime execution
    - Python C extensions need to leverage the Python build
      - Must include the right paths
      - Set linker flags
      - etc.
- There are some disadvantages to using `ctypes` over a C Extension
  module
  - `ctypes` restricts you to the data types that C describes
    - Lose most of Python’s expressiveness
      - No Iterators (See [Item
        21](../../Chapter_03/Item_021/item_021.qmd))
      - No Duck typing (See [Item
        25](../../Chapter_04/Item_025/item_025.qmd))
    - Wrappers can still be confusing and difficult to use correctly
  - Calling `ctypes` with the right data requires copies or
    transformations of function inputs and outputs
    - Overhead cost might undermine performance benefits of a native
      library
    - C extensions reduce the need for copies
  - Using `ctypes` wrong can corrupt the memory of a program
    - Will cause odd behaviour
    - Common sources are passing the wrong data type
      (e.g. `ctype.c_double` instead of `ctype.c_int`)
    - Can use `faulthandler` built-in to try and trace these errors
- When using `ctypes` you should always write unit tests before
  implementing into more complex code
  - Confirm that the library works as expected for simple use cases
  - Help’s ensure that if the library is updated your downstream code
    isn’t unaware of any breaking changes

``` python
import unittest
import ctypes
import pathlib

# Set up the library
"./library.lib"
my_library = ctypes.cdll.LoadLibrary(library_path)

# Setup dot product library function
vector_ptr = ctypes.POINTER(ctypes.c_double)
my_library.dot_product.restype = ctypes.c_double
my_library.dot_product.argtypes = (ctypes.c_int, vector_ptr, vector_ptr)


# Provide Python Wrapper
def dot_product(a, b):
    size = len(a)
    assert len(b) == size, "a and b must have the same length"
    vector = ctypes.c_double * size

    a_vector = vector(*a)
    b_vector = vector(*b)
    result = my_library.dot_product(
        size, ctypes.cast(a_vector, vector_ptr), ctypes.cast(b_vector, vector_ptr)
    )
    return result


# Test
class MyLibraryTest(unittest.TestCase):
    def test_dot_product(self):
        result = dot_product([1.0, 2.5, 3.5], [-7, 4, -12.1])
        self.assertAlmostEqual(-39.35, result)


unittest.main(argv=[""], verbosity=2, exit=False)
```

    test_dot_product (__main__.MyLibraryTest.test_dot_product) ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK

    <unittest.main.TestProgram at 0x7fd60850acf0>

- `ctypes` provides further functionality, e.g.
  - Mapping python objects to C structs
  - Copying memory
  - Error checking
- Consider reading the
  [docs](https://docs.python.org/3/library/ctypes.html)

## Things to Remember

- `ctypes` built-in enables integrating existing native libraries
  written in other languages
- Provides a more rapid development experience over directly using the C
  Extension API
- `ctype` APIs can often be anti-patterns because of the limited data
  types and protocols supported
