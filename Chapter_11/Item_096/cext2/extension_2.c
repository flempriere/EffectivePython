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
