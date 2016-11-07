/*
 * File: abs.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
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
  int i3;
  int k;
  for (i3 = 0; i3 < 2; i3++) {
    uv0[i3] = (unsigned int)x->size[i3];
  }

  i3 = y->size[0] * y->size[1];
  y->size[0] = 3;
  y->size[1] = (int)uv0[1];
  emxEnsureCapacity((emxArray__common *)y, i3, (int)sizeof(double));
  i3 = 3 * x->size[1];
  for (k = 0; k < i3; k++) {
    y->data[k] = fabs(x->data[k]);
  }
}

/*
 * File trailer for abs.c
 *
 * [EOF]
 */
