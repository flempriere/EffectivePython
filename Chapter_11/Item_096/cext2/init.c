/* init.c */
#include "extension_2.h"

static PyMethodDef extension2_methods[] = {
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

static struct PyModuleDef extension2 = {
    PyModuleDef_HEAD_INIT,
    "extension2",
    "My C-extension Module",
    -1,
    extension2_methods,
};

PyMODINIT_FUNC
PyInit_extension2(void) {
  return PyModule_Create(&extension2);
}
