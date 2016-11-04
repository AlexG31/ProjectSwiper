
#include <iostream>
#include <vector>
#include <string>
#include <assert.h>
#include <utility>

#include "simple_function.h"
#include "call_simple_function_emxutil.h"

using std::vector;
using std::string;
using std::make_pair;
using std::pair;
using std::cout;
using std::endl;

void KPD(const vector<vector<double>>&s_rec, int sig_len, double 
  fs, vector<pair<char,double>>*y_out) {
    
    // fs > 0
    assert(fs > 1);
    double L_sig = int((sig_len - fs)/(fs*10.0)); 

    // simple_function inputs.
    emxArray_real_T* s_rec_in;
    emxInit_real_T(&s_rec_in, 2);

    int n_dim = s_rec.size();
    int n_sig = s_rec[0].size();
    int total_size = n_dim * n_sig + 1000;

    s_rec_in->data = new double[total_size]();
    s_rec_in->size[0] = n_dim;
    s_rec_in->size[1] = n_sig;

    s_rec_in->allocatedSize = total_size;
    s_rec_in->canFreeData = true;

    for (int i = 0; i < n_dim; ++i) {
        for (int j = 0; j < n_sig; ++j) {
            s_rec_in->data[i + s_rec_in->size[0] * j] = s_rec[i][j];
        }
    }

    emxArray_struct0_T* ret;
    emxInit_struct0_T(&ret, 2);

    simple_function(s_rec_in, L_sig, fs, ret);
    
    y_out->clear();
    int total_ret_size = 1;
    total_ret_size = ret->size[0] * ret->size[1];

    for (int i = 0; i < total_ret_size; ++i) {
        y_out->push_back(make_pair(ret->data[i].label, ret->data[i].val));
    }

    // Free mem.
    emxFree_real_T(&s_rec_in);
    emxFree_struct0_T(&ret);

    return;
}

void TEST1() {
    vector<vector<double>> s_rec(10, vector<double>(1000, 0.23));
    vector<pair<char, double>> ret;
    KPD(s_rec, 1000, 360, &ret);
    std::cout << "ret.size = " << ret.size() << std::endl;
}

int main() {
    TEST1();

return 0;}


