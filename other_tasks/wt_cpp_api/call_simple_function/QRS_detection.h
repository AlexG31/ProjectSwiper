/*
 * File: QRS_detection.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

#ifndef __QRS_DETECTION_H__
#define __QRS_DETECTION_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"

/* Function Declarations */
extern void QRS_detection(const emxArray_real_T *QRS_detector, double fs,
  emxArray_real_T *y_QRS, emxArray_real_T *x_QRS);

#endif

/*
 * File trailer for QRS_detection.h
 *
 * [EOF]
 */
