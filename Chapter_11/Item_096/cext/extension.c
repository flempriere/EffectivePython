/* extension.c */
#include "extension.h"

PyObject *dot_product(PyObject *self, PyObject *args) {
    PyObject *left, *right;
    if (!PyArg_ParseTuple(args, "OO", &left, &right)) {
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
        PyErr_SetString(PyExc_ValueError, "Lists must be the same length");
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
