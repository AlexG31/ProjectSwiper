/*
 * File: floor.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "floor.h"

/* Function Definitions */

/*
 * Arguments    : emxArray_real_T *x
 * Return Type  : void
 */
void b_floor(emxArray_real_T *x)
{
  int i12;
  int k;
  i12 = x->size[1];
  for (k = 0; k < i12; k++) {
    x->data[k] = floor(x->data[k]);
  }
}

/*
 * File trailer for floor.c
 *
 * [EOF]
 */
