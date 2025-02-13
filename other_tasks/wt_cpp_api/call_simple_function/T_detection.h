/*
 * File: T_detection.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
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

// vector version of T_detection.
extern void T_detection(emxArray_real_T *T_detector, double fs, const vector<int>& x_qrs_vec,
                 double x_start, emxArray_real_T *T_Location_cur_out,
                 emxArray_real_T *P_Location_cur_out);
#endif

/*
 * File trailer for T_detection.h
 *
 * [EOF]
 */
