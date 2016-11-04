/*
 * File: call_simple_function_emxAPI.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

#ifndef __CALL_SIMPLE_FUNCTION_EMXAPI_H__
#define __CALL_SIMPLE_FUNCTION_EMXAPI_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"

/* Function Declarations */
extern emxArray_struct0_T *emxCreateND_struct0_T(int numDimensions, int *size);
extern emxArray_struct0_T *emxCreateWrapperND_struct0_T(struct0_T *data, int
  numDimensions, int *size);
extern emxArray_struct0_T *emxCreateWrapper_struct0_T(struct0_T *data, int rows,
  int cols);
extern emxArray_struct0_T *emxCreate_struct0_T(int rows, int cols);
extern void emxDestroyArray_struct0_T(emxArray_struct0_T *emxArray);

#endif

/*
 * File trailer for call_simple_function_emxAPI.h
 *
 * [EOF]
 */
