/*
 * File: KPD.h
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

#ifndef __KPD_H__
#define __KPD_H__

/* Include files */
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "call_simple_function_types.h"
//#include "simple_function.h"

#include <vector>

using std::vector;
using std::pair;

/* Function Declarations */
//extern void KPD(const emxArray_real_T *s_rec, double L_sig, double
  //fs, emxArray_struct0_T *y_out);

extern void KPD(const vector<vector<double>>&s_rec,
        int sig_len,
        double fs,
        vector<pair<char, int>>* y_out);

#endif

/*
 * File trailer for KPD.h
 *
 * [EOF]
 */
