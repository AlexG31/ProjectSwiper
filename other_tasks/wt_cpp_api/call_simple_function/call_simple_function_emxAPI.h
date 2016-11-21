/*
 * File: call_simple_function_emxAPI.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
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
extern emxArray_real_T *emxCreateND_real_T(int numDimensions, int *size);
extern emxArray_real_T *emxCreateWrapperND_real_T(double *data, int
  numDimensions, int *size);
extern emxArray_real_T *emxCreateWrapper_real_T(double *data, int rows, int cols);
extern emxArray_real_T *emxCreate_real_T(int rows, int cols);
extern void emxDestroyArray_real_T(emxArray_real_T *emxArray);

#endif

/*
 * File trailer for call_simple_function_emxAPI.h
 *
 * [EOF]
 */
