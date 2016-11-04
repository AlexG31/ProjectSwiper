/*
 * File: call_simple_function_emxAPI.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "call_simple_function_emxAPI.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

/*
 * Arguments    : int numDimensions
 *                int *size
 * Return Type  : emxArray_struct0_T *
 */
emxArray_struct0_T *emxCreateND_struct0_T(int numDimensions, int *size)
{
  emxArray_struct0_T *emx;
  int numEl;
  int i;
  emxInit_struct0_T(&emx, numDimensions);
  numEl = 1;
  for (i = 0; i < numDimensions; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = (struct0_T *)calloc((unsigned int)numEl, sizeof(struct0_T));
  emx->numDimensions = numDimensions;
  emx->allocatedSize = numEl;
  return emx;
}

/*
 * Arguments    : struct0_T *data
 *                int numDimensions
 *                int *size
 * Return Type  : emxArray_struct0_T *
 */
emxArray_struct0_T *emxCreateWrapperND_struct0_T(struct0_T *data, int
  numDimensions, int *size)
{
  emxArray_struct0_T *emx;
  int numEl;
  int i;
  emxInit_struct0_T(&emx, numDimensions);
  numEl = 1;
  for (i = 0; i < numDimensions; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = data;
  emx->numDimensions = numDimensions;
  emx->allocatedSize = numEl;
  emx->canFreeData = false;
  return emx;
}

/*
 * Arguments    : struct0_T *data
 *                int rows
 *                int cols
 * Return Type  : emxArray_struct0_T *
 */
emxArray_struct0_T *emxCreateWrapper_struct0_T(struct0_T *data, int rows, int
  cols)
{
  emxArray_struct0_T *emx;
  int size[2];
  int numEl;
  int i;
  size[0] = rows;
  size[1] = cols;
  emxInit_struct0_T(&emx, 2);
  numEl = 1;
  for (i = 0; i < 2; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = data;
  emx->numDimensions = 2;
  emx->allocatedSize = numEl;
  emx->canFreeData = false;
  return emx;
}

/*
 * Arguments    : int rows
 *                int cols
 * Return Type  : emxArray_struct0_T *
 */
emxArray_struct0_T *emxCreate_struct0_T(int rows, int cols)
{
  emxArray_struct0_T *emx;
  int size[2];
  int numEl;
  int i;
  size[0] = rows;
  size[1] = cols;
  emxInit_struct0_T(&emx, 2);
  numEl = 1;
  for (i = 0; i < 2; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = (struct0_T *)calloc((unsigned int)numEl, sizeof(struct0_T));
  emx->numDimensions = 2;
  emx->allocatedSize = numEl;
  return emx;
}

/*
 * Arguments    : emxArray_struct0_T *emxArray
 * Return Type  : void
 */
void emxDestroyArray_struct0_T(emxArray_struct0_T *emxArray)
{
  emxFree_struct0_T(&emxArray);
}

/*
 * File trailer for call_simple_function_emxAPI.c
 *
 * [EOF]
 */
