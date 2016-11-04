/*
 * File: call_simple_function_emxutil.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

#ifndef __CALL_SIMPLE_FUNCTION_EMXUTIL_H__
#define __CALL_SIMPLE_FUNCTION_EMXUTIL_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"

/* Function Declarations */
extern void b_emxInit_int32_T(emxArray_int32_T **pEmxArray, int numDimensions);
extern void b_emxInit_real_T(emxArray_real_T **pEmxArray, int numDimensions);
extern void emxEnsureCapacity(emxArray__common *emxArray, int oldNumel, int
  elementSize);
extern void emxFree_int32_T(emxArray_int32_T **pEmxArray);
extern void emxFree_real_T(emxArray_real_T **pEmxArray);
extern void emxFree_struct0_T(emxArray_struct0_T **pEmxArray);
extern void emxInit_int32_T(emxArray_int32_T **pEmxArray, int numDimensions);
extern void emxInit_real_T(emxArray_real_T **pEmxArray, int numDimensions);
extern void emxInit_struct0_T(emxArray_struct0_T **pEmxArray, int numDimensions);

#endif

/*
 * File trailer for call_simple_function_emxutil.h
 *
 * [EOF]
 */
