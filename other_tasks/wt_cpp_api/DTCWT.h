/*
 * File: DTCWT.h
 */

#ifndef __DTCWT_H__
#define __DTCWT_H__

/* Include files */
#include <math.h>
#include <vector>

using std::vector;

/* Function Declarations */
extern void DTCWT(vector<double>& Signal,
            int DecLevel,
            vector<int>&, 
            vector<vector<double>>*);


#endif

/*
 * File trailer for DTCWT.h
 *
 * [EOF]
 */
