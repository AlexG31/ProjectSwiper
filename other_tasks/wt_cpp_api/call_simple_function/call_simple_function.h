/*
 * File: call_simple_function.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

#ifndef __CALL_SIMPLE_FUNCTION_H__
#define __CALL_SIMPLE_FUNCTION_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"

#include <vector>
#include <utility>

using std::vector;
using std::pair;

/* Function Declarations */
//extern void call_simple_function(const double s_rec[6500000], double sig_len,
  //double fs, emxArray_real_T *y_out);

extern void call_simple_function(const double s_rec[6500000], double sig_len,
  double fs, emxArray_real_T *y_out, vector<pair<char, int>>* result_out);

#endif

/*
 * File trailer for call_simple_function.h
 *
 * [EOF]
 */
