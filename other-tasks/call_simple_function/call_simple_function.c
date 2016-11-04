/*
 * File: call_simple_function.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "call_simple_function_emxutil.h"
#include "simple_function.h"
#include "rand.h"

/* Function Definitions */

/*
 * Arguments    : double wt_level
 *                double sig_len
 *                double fs
 *                emxArray_struct0_T *y_out
 * Return Type  : void
 */
void call_simple_function(double wt_level, double sig_len, double fs,
  emxArray_struct0_T *y_out)
{
  emxArray_real_T *s_rec;
  emxInit_real_T(&s_rec, 2);

  /* % Call simple function to make its parameters variable-sized. */
  b_rand(wt_level, sig_len, s_rec);
  simple_function(s_rec, floor((sig_len - fs) / (fs * 10.0)), fs, y_out);
  emxFree_real_T(&s_rec);
}

/*
 * File trailer for call_simple_function.c
 *
 * [EOF]
 */
