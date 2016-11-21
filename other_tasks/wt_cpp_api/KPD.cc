#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <assert.h>
#include <utility>

#include "call_simple_function.h"
#include "call_simple_function_emxutil.h"

using std::vector;
using std::string;
using std::make_pair;
using std::pair;
using std::cout;
using std::endl;

//extern void call_simple_function(const double s_rec[6500000], double sig_len,
  //double fs, emxArray_real_T *y_out);

void KPD(const vector<vector<double>>& s_rec,
        int sig_len,
        double fs,
        vector<pair<char, int>>* y_out) {
    
    cout << "ok KPD" << endl;
    printf("Input info:\n  s_rec.size() = %d, sig_len = %d, fs = %f\n",
            s_rec.size(), sig_len, fs);

    // fs > 0
    assert(fs > 1);
    double L_sig = int((sig_len - fs)/(fs*10.0)); 

    // simple_function inputs.
    double s_rec_in[6500000];
    int n_dim = s_rec.size();
    int n_sig = s_rec[0].size();
    int total_size = n_dim * n_sig + 1000;

    for (int i = 0; i < n_dim; ++i) {
        for (int j = 0; j < 650000; ++j) {
            double val = 0;
            if (j < s_rec[i].size()) val = s_rec[i][j];
            s_rec_in[i + j * 10] = val;
        }
    }

    //emxArray_struct0_T* ret;
    //emxInit_struct0_T(&ret, 2);
    emxArray_real_T *ret;
    emxInit_real_T(&ret, 2);

    call_simple_function(s_rec_in, 6500000, fs, ret);
    cout << "After Simple Function " << endl;
    
    y_out->clear();
    int total_ret_size = 1;
    total_ret_size = ret->size[0] * ret->size[1];

    cout << "KPD ret.num_dimensions = " << ret->numDimensions << endl;
    for (int i = 0; i < ret->numDimensions; ++i) {
        cout << ret->size[i] << endl;
    }

    //for (int i = 0; i < total_ret_size; ++i) {
        //y_out->push_back(
                //make_pair(ret->data[i].label, round(ret->data[i].val)));
    //}

    // Free mem.
    emxFree_real_T(&ret);

    return;
}

void TEST1_KPD() {
    vector<vector<double>> s_rec(10, vector<double>(1000, 0.23));
    vector<pair<char, int>> ret;
    KPD(s_rec, 1000, 360, &ret);
    std::cout << "ret.size = " << ret.size() << std::endl;
}

