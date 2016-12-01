/*
 * File: gaussian_function.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "gaussian_function.h"
#include "call_simple_function_emxutil.h"
#include "rdivide.h"
#include "power.h"

/* Function Definitions */

/*
 * Arguments    : const emxArray_real_T *x
 *                const double param[2]
 *                emxArray_real_T *y
 * Return Type  : void
 */
void gaussian_function(const emxArray_real_T *x, const double param[2],
  emxArray_real_T *y)
{
  emxArray_real_T *b_x;
  int A;
  int loop_ub;
  emxArray_real_T *b_A;
  emxArray_real_T *c_A;
  emxInit_real_T(&b_x, 2);
  A = b_x->size[0] * b_x->size[1];
  b_x->size[0] = 1;
  b_x->size[1] = x->size[1];
  emxEnsureCapacity((emxArray__common *)b_x, A, (int)sizeof(double));
  loop_ub = x->size[0] * x->size[1];
  for (A = 0; A < loop_ub; A++) {
    b_x->data[A] = x->data[A] - param[1];
  }

  emxInit_real_T(&b_A, 2);
  power(b_x, b_A);
  A = b_A->size[0] * b_A->size[1];
  b_A->size[0] = 1;
  emxEnsureCapacity((emxArray__common *)b_A, A, (int)sizeof(double));
  A = b_A->size[0];
  loop_ub = b_A->size[1];
  loop_ub *= A;
  emxFree_real_T(&b_x);
  for (A = 0; A < loop_ub; A++) {
    b_A->data[A] = -b_A->data[A];
  }

  emxInit_real_T(&c_A, 2);
  A = c_A->size[0] * c_A->size[1];
  c_A->size[0] = 1;
  c_A->size[1] = b_A->size[1];
  emxEnsureCapacity((emxArray__common *)c_A, A, (int)sizeof(double));
  loop_ub = b_A->size[0] * b_A->size[1];
  for (A = 0; A < loop_ub; A++) {
    c_A->data[A] = b_A->data[A];
  }

  rdivide(c_A, 2.0 * (param[0] * param[0]), b_A);
  A = y->size[0] * y->size[1];
  y->size[0] = 1;
  y->size[1] = b_A->size[1];
  emxEnsureCapacity((emxArray__common *)y, A, (int)sizeof(double));
  loop_ub = b_A->size[0] * b_A->size[1];
  emxFree_real_T(&c_A);
  for (A = 0; A < loop_ub; A++) {
    y->data[A] = b_A->data[A];
  }

  for (A = 0; A < b_A->size[1]; A++) {
    y->data[A] = exp(y->data[A]);
  }

  emxFree_real_T(&b_A);
}

/*
 * File trailer for gaussian_function.c
 *
 * [EOF]
 */
