/*
 * File: sum.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "sum.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

/*
 * Arguments    : const emxArray_real_T *x
 *                emxArray_real_T *y
 * Return Type  : void
 */
void sum(const emxArray_real_T *x, emxArray_real_T *y)
{
  unsigned int sz[2];
  int ixstart;
  int k;
  int ix;
  int iy;
  int i;
  double s;
  for (ixstart = 0; ixstart < 2; ixstart++) {
    sz[ixstart] = (unsigned int)x->size[ixstart];
  }

  ixstart = y->size[0] * y->size[1];
  y->size[0] = 1;
  y->size[1] = (int)sz[1];
  emxEnsureCapacity((emxArray__common *)y, ixstart, (int)sizeof(double));
  if (x->size[1] == 0) {
    ixstart = y->size[0] * y->size[1];
    y->size[0] = 1;
    emxEnsureCapacity((emxArray__common *)y, ixstart, (int)sizeof(double));
    ixstart = y->size[0] * y->size[1];
    y->size[1] = (int)sz[1];
    emxEnsureCapacity((emxArray__common *)y, ixstart, (int)sizeof(double));
    k = (int)sz[1];
    for (ixstart = 0; ixstart < k; ixstart++) {
      y->data[ixstart] = 0.0;
    }
  } else {
    ix = -1;
    iy = -1;
    for (i = 1; i <= x->size[1]; i++) {
      ixstart = ix + 1;
      ix++;
      s = x->data[ixstart];
      for (k = 0; k < 2; k++) {
        ix++;
        s += x->data[ix];
      }

      iy++;
      y->data[iy] = s;
    }
  }
}

/*
 * File trailer for sum.c
 *
 * [EOF]
 */
