/*
 * File: abs.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "abs.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

/*
 * Arguments    : const emxArray_real_T *x
 *                emxArray_real_T *y
 * Return Type  : void
 */
void b_abs(const emxArray_real_T *x, emxArray_real_T *y)
{
  unsigned int uv0[2];
  int i2;
  int k;
  for (i2 = 0; i2 < 2; i2++) {
    uv0[i2] = (unsigned int)x->size[i2];
  }

  i2 = y->size[0] * y->size[1];
  y->size[0] = 3;
  y->size[1] = (int)uv0[1];
  emxEnsureCapacity((emxArray__common *)y, i2, (int)sizeof(double));
  i2 = 3 * x->size[1];
  for (k = 0; k < i2; k++) {
    y->data[k] = fabs(x->data[k]);
  }
}

/*
 * File trailer for abs.c
 *
 * [EOF]
 */
