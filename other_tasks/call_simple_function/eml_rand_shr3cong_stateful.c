/*
 * File: eml_rand_shr3cong_stateful.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "eml_rand_shr3cong_stateful.h"
#include "call_simple_function_data.h"

/* Function Definitions */

/*
 * Arguments    : void
 * Return Type  : void
 */
void eml_rand_shr3cong_stateful_init(void)
{
  int i11;
  for (i11 = 0; i11 < 2; i11++) {
    b_state[i11] = 362436069U + 158852560U * i11;
  }
}

/*
 * File trailer for eml_rand_shr3cong_stateful.c
 *
 * [EOF]
 */
