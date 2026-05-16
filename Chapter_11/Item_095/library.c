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
