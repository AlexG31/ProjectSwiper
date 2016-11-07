/*
 * File: rand.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "rand.h"
#include "call_simple_function_emxutil.h"
#include "call_simple_function_data.h"

/* Variable Definitions */
static unsigned int c_state[625];

/* Function Declarations */
static void twister_state_vector(unsigned int mt[625], double seed);

/* Function Definitions */

/*
 * Arguments    : unsigned int mt[625]
 *                double seed
 * Return Type  : void
 */
static void twister_state_vector(unsigned int mt[625], double seed)
{
  unsigned int r;
  int mti;
  if (seed < 4.294967296E+9) {
    if (seed >= 0.0) {
      r = (unsigned int)seed;
    } else {
      r = 0U;
    }
  } else if (seed >= 4.294967296E+9) {
    r = MAX_uint32_T;
  } else {
    r = 0U;
  }

  mt[0] = r;
  for (mti = 0; mti < 623; mti++) {
    r = (r ^ r >> 30U) * 1812433253U + (1 + mti);
    mt[1 + mti] = r;
  }

  mt[624] = 624U;
}

/*
 * Arguments    : double varargin_1
 *                double varargin_2
 *                emxArray_real_T *r
 * Return Type  : void
 */
void b_rand(double varargin_1, double varargin_2, emxArray_real_T *r)
{
  int i0;
  int k;
  int b_k;
  unsigned int mti;
  unsigned int y;
  int32_T exitg1;
  unsigned int u[2];
  int kk;
  unsigned int b_y;
  unsigned int c_y;
  unsigned int d_y;
  double b_r;
  boolean_T isvalid;
  boolean_T exitg2;
  if (method == 4U) {
    i0 = r->size[0] * r->size[1];
    r->size[0] = (int)varargin_1;
    r->size[1] = (int)varargin_2;
    emxEnsureCapacity((emxArray__common *)r, i0, (int)sizeof(double));
    i0 = (int)varargin_1 * (int)varargin_2;
    for (k = 0; k < i0; k++) {
      b_k = (int)(state / 127773U);
      mti = 16807U * (state - b_k * 127773U);
      y = 2836U * b_k;
      if (mti < y) {
        state = (mti - y) + 2147483647U;
      } else {
        state = mti - y;
      }

      r->data[k] = (double)state * 4.6566128752457969E-10;
    }
  } else if (method == 5U) {
    i0 = r->size[0] * r->size[1];
    r->size[0] = (int)varargin_1;
    r->size[1] = (int)varargin_2;
    emxEnsureCapacity((emxArray__common *)r, i0, (int)sizeof(double));
    i0 = (int)varargin_1 * (int)varargin_2;
    for (k = 0; k < i0; k++) {
      mti = 69069U * b_state[0] + 1234567U;
      y = b_state[1] ^ b_state[1] << 13;
      y ^= y >> 17;
      y ^= y << 5;
      b_state[0] = mti;
      b_state[1] = y;
      r->data[k] = (double)(mti + y) * 2.328306436538696E-10;
    }
  } else {
    if (!state_not_empty) {
      memset(&c_state[0], 0, 625U * sizeof(unsigned int));
      twister_state_vector(c_state, 5489.0);
      state_not_empty = true;
    }

    i0 = r->size[0] * r->size[1];
    r->size[0] = (int)varargin_1;
    r->size[1] = (int)varargin_2;
    emxEnsureCapacity((emxArray__common *)r, i0, (int)sizeof(double));
    i0 = (int)varargin_1 * (int)varargin_2;
    for (k = 0; k < i0; k++) {
      /* ========================= COPYRIGHT NOTICE ============================ */
      /*  This is a uniform (0,1) pseudorandom number generator based on:        */
      /*                                                                         */
      /*  A C-program for MT19937, with initialization improved 2002/1/26.       */
      /*  Coded by Takuji Nishimura and Makoto Matsumoto.                        */
      /*                                                                         */
      /*  Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,      */
      /*  All rights reserved.                                                   */
      /*                                                                         */
      /*  Redistribution and use in source and binary forms, with or without     */
      /*  modification, are permitted provided that the following conditions     */
      /*  are met:                                                               */
      /*                                                                         */
      /*    1. Redistributions of source code must retain the above copyright    */
      /*       notice, this list of conditions and the following disclaimer.     */
      /*                                                                         */
      /*    2. Redistributions in binary form must reproduce the above copyright */
      /*       notice, this list of conditions and the following disclaimer      */
      /*       in the documentation and/or other materials provided with the     */
      /*       distribution.                                                     */
      /*                                                                         */
      /*    3. The names of its contributors may not be used to endorse or       */
      /*       promote products derived from this software without specific      */
      /*       prior written permission.                                         */
      /*                                                                         */
      /*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS    */
      /*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT      */
      /*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR  */
      /*  A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT  */
      /*  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  */
      /*  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT       */
      /*  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,  */
      /*  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY  */
      /*  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT    */
      /*  (INCLUDING  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE */
      /*  OF THIS  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  */
      /*                                                                         */
      /* =============================   END   ================================= */
      do {
        exitg1 = 0;
        for (b_k = 0; b_k < 2; b_k++) {
          mti = c_state[624] + 1U;
          if (mti >= 625U) {
            for (kk = 0; kk < 227; kk++) {
              y = (c_state[kk] & 2147483648U) | (c_state[1 + kk] & 2147483647U);
              if ((int)(y & 1U) == 0) {
                b_y = y >> 1U;
              } else {
                b_y = y >> 1U ^ 2567483615U;
              }

              c_state[kk] = c_state[397 + kk] ^ b_y;
            }

            for (kk = 0; kk < 396; kk++) {
              y = (c_state[227 + kk] & 2147483648U) | (c_state[228 + kk] &
                2147483647U);
              if ((int)(y & 1U) == 0) {
                c_y = y >> 1U;
              } else {
                c_y = y >> 1U ^ 2567483615U;
              }

              c_state[227 + kk] = c_state[kk] ^ c_y;
            }

            y = (c_state[623] & 2147483648U) | (c_state[0] & 2147483647U);
            if ((int)(y & 1U) == 0) {
              d_y = y >> 1U;
            } else {
              d_y = y >> 1U ^ 2567483615U;
            }

            c_state[623] = c_state[396] ^ d_y;
            mti = 1U;
          }

          y = c_state[(int)mti - 1];
          c_state[624] = mti;
          y ^= y >> 11U;
          y ^= y << 7U & 2636928640U;
          y ^= y << 15U & 4022730752U;
          y ^= y >> 18U;
          u[b_k] = y;
        }

        b_r = 1.1102230246251565E-16 * ((double)(u[0] >> 5U) * 6.7108864E+7 +
          (double)(u[1] >> 6U));
        if (b_r == 0.0) {
          if ((c_state[624] >= 1U) && (c_state[624] < 625U)) {
            isvalid = true;
          } else {
            isvalid = false;
          }

          if (isvalid) {
            isvalid = false;
            b_k = 1;
            exitg2 = false;
            while ((!exitg2) && (b_k < 625)) {
              if (c_state[b_k - 1] == 0U) {
                b_k++;
              } else {
                isvalid = true;
                exitg2 = true;
              }
            }
          }

          if (!isvalid) {
            twister_state_vector(c_state, 5489.0);
          }
        } else {
          exitg1 = 1;
        }
      } while (exitg1 == 0);

      r->data[k] = b_r;
    }
  }
}

/*
 * File trailer for rand.c
 *
 * [EOF]
 */
