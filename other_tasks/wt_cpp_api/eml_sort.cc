/*
 * File: eml_sort.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "eml_sort.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

/*
 * Arguments    : const emxArray_real_T *x
 *                emxArray_real_T *y
 * Return Type  : void
 */
void eml_sort(const emxArray_real_T *x, emxArray_real_T *y)
{
  emxArray_real_T *vwork;
  int vlen;
  int i2;
  int ix;
  emxArray_int32_T *iidx;
  emxArray_int32_T *idx0;
  int k;
  unsigned int unnamed_idx_0;
  boolean_T p;
  int j;
  int pEnd;
  int b_p;
  int q;
  int qEnd;
  int kEnd;
  b_emxInit_real_T(&vwork, 1);
  vlen = x->size[1] - 1;
  i2 = vwork->size[0];
  vwork->size[0] = vlen + 1;
  emxEnsureCapacity((emxArray__common *)vwork, i2, (int)sizeof(double));
  for (i2 = 0; i2 < 2; i2++) {
    ix = y->size[0] * y->size[1];
    y->size[i2] = x->size[i2];
    emxEnsureCapacity((emxArray__common *)y, ix, (int)sizeof(double));
  }

  b_emxInit_int32_T(&iidx, 1);
  b_emxInit_int32_T(&idx0, 1);
  ix = 1;
  for (k = 0; k <= vlen; k++) {
    vwork->data[k] = x->data[ix - 1];
    ix++;
  }

  unnamed_idx_0 = (unsigned int)vwork->size[0];
  i2 = iidx->size[0];
  iidx->size[0] = (int)unnamed_idx_0;
  emxEnsureCapacity((emxArray__common *)iidx, i2, (int)sizeof(int));
  if (vwork->size[0] == 0) {
  } else {
    for (k = 1; k <= vwork->size[0]; k++) {
      iidx->data[k - 1] = k;
    }

    for (k = 1; k <= vwork->size[0] - 1; k += 2) {
      if ((vwork->data[k - 1] <= vwork->data[k]) || rtIsNaN(vwork->data[k])) {
        p = true;
      } else {
        p = false;
      }

      if (p) {
      } else {
        iidx->data[k - 1] = k + 1;
        iidx->data[k] = k;
      }
    }

    i2 = idx0->size[0];
    idx0->size[0] = vwork->size[0];
    emxEnsureCapacity((emxArray__common *)idx0, i2, (int)sizeof(int));
    ix = vwork->size[0];
    for (i2 = 0; i2 < ix; i2++) {
      idx0->data[i2] = 1;
    }

    ix = 2;
    while (ix < vwork->size[0]) {
      i2 = ix << 1;
      j = 1;
      for (pEnd = 1 + ix; pEnd < vwork->size[0] + 1; pEnd = qEnd + ix) {
        b_p = j;
        q = pEnd - 1;
        qEnd = j + i2;
        if (qEnd > vwork->size[0] + 1) {
          qEnd = vwork->size[0] + 1;
        }

        k = 0;
        kEnd = qEnd - j;
        while (k + 1 <= kEnd) {
          if ((vwork->data[iidx->data[b_p - 1] - 1] <= vwork->data[iidx->data[q]
               - 1]) || rtIsNaN(vwork->data[iidx->data[q] - 1])) {
            p = true;
          } else {
            p = false;
          }

          if (p) {
            idx0->data[k] = iidx->data[b_p - 1];
            b_p++;
            if (b_p == pEnd) {
              while (q + 1 < qEnd) {
                k++;
                idx0->data[k] = iidx->data[q];
                q++;
              }
            }
          } else {
            idx0->data[k] = iidx->data[q];
            q++;
            if (q + 1 == qEnd) {
              while (b_p < pEnd) {
                k++;
                idx0->data[k] = iidx->data[b_p - 1];
                b_p++;
              }
            }
          }

          k++;
        }

        for (k = 0; k + 1 <= kEnd; k++) {
          iidx->data[(j + k) - 1] = idx0->data[k];
        }

        j = qEnd;
      }

      ix = i2;
    }
  }

  ix = 1;
  for (k = 0; k <= vlen; k++) {
    y->data[ix - 1] = vwork->data[iidx->data[k] - 1];
    ix++;
  }

  emxFree_int32_T(&idx0);
  emxFree_int32_T(&iidx);
  emxFree_real_T(&vwork);
}

/*
 * File trailer for eml_sort.c
 *
 * [EOF]
 */
