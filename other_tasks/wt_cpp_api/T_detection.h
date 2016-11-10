/*
 * File: T_detection.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

#ifndef __T_DETECTION_H__
#define __T_DETECTION_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"

/* Function Declarations */
extern void T_detection(emxArray_real_T *T_detector, double fs, const
  emxArray_real_T *x_QRS, double x_start, emxArray_real_T *T_Location_cur,
  emxArray_real_T *P_Location_cur);

#endif

/*
 * File trailer for T_detection.h
 *
 * [EOF]
 */
