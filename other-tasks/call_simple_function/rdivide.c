/*
 * File: rdivide.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "rdivide.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

/*
 * Arguments    : const emxArray_real_T *x
 *                double y
 *                emxArray_real_T *z
 * Return Type  : void
 */
void rdivide(const emxArray_real_T *x, double y, emxArray_real_T *z)
{
  int i10;
  int loop_ub;
  i10 = z->size[0] * z->size[1];
  z->size[0] = 1;
  z->size[1] = x->size[1];
  emxEnsureCapacity((emxArray__common *)z, i10, (int)sizeof(double));
  loop_ub = x->size[0] * x->size[1];
  for (i10 = 0; i10 < loop_ub; i10++) {
    z->data[i10] = x->data[i10] / y;
  }
}

/*
 * File trailer for rdivide.c
 *
 * [EOF]
 */
