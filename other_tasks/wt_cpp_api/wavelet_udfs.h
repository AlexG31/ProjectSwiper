#ifndef WAVELET_UDFS_H
#define WAVELET_UDFS_H

#include <vector>
#include <complex>
using namespace std;



// 1D Functions


void* wavedec_udf(
        vector<double> &sig,
        int J,
        vector<vector<double>>& filter_bank,
        vector<double> &dwt_output,
        vector<double> &flag,
        vector<int> &length);


void* waverec_udf_noflag(
        vector<double> &dwtop,
        vector<int> &length,
        vector<vector<double>>& filter_bank,
        vector<double> &idwt_output);


void* waverec_udf(vector<double> &dwtop,
        vector<double> &flag,
        vector<vector<double>>& filter_bank,
        vector<double> &idwt_output,
        vector<int> &length);


#endif/* WAVELET_UDFS_H */
