/* init.c */
#include "extension.h"

static PyMethodDef extension_methods[] = {
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

static struct PyModuleDef extension = {
    PyModuleDef_HEAD_INIT,
    "extension",
    "My C-extension Module",
    -1,
    extension_methods,
};

PyMODINIT_FUNC
PyInit_extension(void) {
  return PyModule_Create(&extension);
}
