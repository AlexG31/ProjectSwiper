#ifndef WAVEDEC_API_H_
#define WAVEDEC_API_H_

#include "wavelet2d.h"

// Wavelet decomposition function
// Inputs:
//  signal: time-domain signal
//  dwt_level: levels of decomposition
//  filter_bank: wavelet filter bank of format:[L_D, H_D, L_R, H_R]
// Outputs:
//  coefs: concatenation of dwt coefficients [cAn, cDn, cDn-1 ..., cD1]
//  lengths: length of coefficients in each level.
void wavedec(vector<double>& signal, int dwt_level, 
        vector<vector<double>>& filter_bank,
        vector<double>* coefs,
        vector<int>* lengths);

// Wavelet reconstruction function
// Inputs:
//  coefs: concatenation of dwt coefficients [cAn, cDn, cDn-1 ..., cD1]
//  lengths: length of coefficients in each level.
//  filter_bank: wavelet filter bank of format:[L_D, H_D, L_R, H_R]
// Outputs:
//  sig_out: reconstructed signal.
void waverec(vector<double>& coefs,vector<int>& lengths,
        vector<vector<double>>& filter_bank,
        vector<double>* sig_out);



#endif // WAVEDEC_API_H_
