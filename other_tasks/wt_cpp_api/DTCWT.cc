/* Include files */
#include <cmath>
#include <vector>
#include <iostream>
#include <fstream>
#include <string>
#include <complex>
#include <assert.h>

#include "DTCWT.h"
#include "Qshift.h"
#include "wavelib/src/shared/wavedec_api.h"

using std::vector;
using std::complex;

typedef complex<double> ComplexDouble;

// debug
template <typename T> 
static void PrintVec(vector<T>& vec) {
    cout << "[";
    for (const auto& val: vec) {
        cout << val << ", ";
    }
    cout << "]" << endl;
}

// Output data to txt file
template <typename T>
static void OutputData(vector<T>& vec) {
    fstream fs("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/tmp.out",
            fstream::out);

    int len = vec.size();
    fs << len << endl;
    for (int i = 0; i < len; ++i) {
        fs << vec[i] << endl;
    }

    fs.close();
}


// Convert complex vector to real value vector.
void KeepItReal(vector<ComplexDouble>& complex_filter,
        vector<double>* real_output) {
    
    real_output->clear();
    for (const auto& val: complex_filter) {
        real_output->push_back(val.real());
    }
}

inline int ToCIndex(int index) {
    return index - 1;
}

// Matlab sum function.
template <typename T>
T sum(vector<T> arr, int L, int R) {

    T ans = 0;
    for (int i = L; i <= R; ++i) {
        ans += arr[i];
    }
    return ans;
}

// Matlab zeros function.
inline vector<vector<double>> zeros(int h, int w) {
    vector<vector<double>> ret(h, vector<double>(w, 0));
    return ret;
}


// Matlab slice = operator
// [Usage]: This function copys elements in range [lb, rb] into vector a
//      in range [la, ra]
template <typename T>
void vector_copy(vector<T>& a, int la, int ra, vector<T>& b, int lb, int rb) {
    assert(ra >= la);
    assert(ra - la == rb - lb);

    // assign space first
    if (ra >= a.size()) {
        int zero_padding_size = ra - a.size() + 1;
        a.insert(a.end(), zero_padding_size, 0);
    }

    for (int i = 0; i <= ra - la; ++i) {
        //cout << "copy b["
             //<< i + lb
             //<< "] to a["
             //<< i + la
             //<< "]"
             //<< endl;
        a[i + la] = b[i + lb];
    }
}

void Get_S_rec(vector<vector<double>>& Sa_rec,
        vector<vector<double>>& Sb_rec,
        vector<vector<double>>* S_rec) {
    int h = Sa_rec.size();
    int w = Sa_rec[0].size();
    for (int i = 0; i < h; ++i) {
        vector<double> row;
        for (int j = 0; j < w; ++j) {
            row.push_back((Sa_rec[i][j] + Sb_rec[i][j]) / 2.0);
        }
        S_rec->push_back(row);
    }    
}

void DTCWT(vector<double>& Signal,
            int DecLevel,
            vector<int>& Wavelet_Remain, 
            vector<vector<double>> filter_bank,
            vector<vector<double>>* s_rec
            ) {

    int len_Wavelet_Remain = Wavelet_Remain.size();

    int L = Signal.size();
    vector<double> HL{0.03516384, 0, -0.08832942, 0.23389032, 0.76027237,
        0.58751830, 0, -0.11430184, 0, 0};

    // Filters
    vector<vector<ComplexDouble>> H_filters;
    vector<double> H00a, H01a, H10a, H11a, H00b, H01b, H10b, H11b;
    Qshift(HL, &H_filters);   

    KeepItReal(H_filters[0], &H00a);
    KeepItReal(H_filters[1], &H01a);
    KeepItReal(H_filters[2], &H10a);
    KeepItReal(H_filters[3], &H11a);
    KeepItReal(H_filters[4], &H00b);
    KeepItReal(H_filters[5], &H01b);
    KeepItReal(H_filters[6], &H10b);
    KeepItReal(H_filters[7], &H11b);
    
    // debug
    //cout << "H00a" << endl;
    ////PrintVec(H_filters[0]);
    //PrintVec(H00a);
    //cout << " H01a" << endl;
    ////PrintVec(H_filters[1]);
    //PrintVec(H01a);
    //cout << " H10a" << endl;
    //PrintVec(H10a);
    //cout << " H11a" << endl;
    //PrintVec(H11a);
    //cout << " H00b" << endl;
    //PrintVec(H00b);
    //cout << " H01b" << endl;
    //PrintVec(H01b);
    //cout << " H10b" << endl;
    //PrintVec(H10b);
    //cout << " H11b" << endl;
    //PrintVec(H11b);

    // Wavedec
    vector<double> C1;
    vector<int> L1;

    vector<double> backup_sig = Signal;
    wavedec(Signal, 1, filter_bank, &C1, &L1);
    
    // Signal Check
    for (int i = 0; i < backup_sig.size(); ++i)
        if (backup_sig[i] != Signal[i]) {
            cout << endl;
            cout << "Signal changed!" << endl;
            break;
        }


    vector<double> Ca1;
    vector<int> La1;
    vector<vector<double>> filter_bank_a1{H00a, H01a, {}, {}};
    wavedec(Signal, Wavelet_Remain[len_Wavelet_Remain - 1],
            filter_bank_a1, &Ca1, &La1);


    vector<double> Cb1;
    vector<int> Lb1;
    vector<vector<double>> filter_bank_b1{H00b, H01b, {}, {}};
    wavedec(Signal, Wavelet_Remain[len_Wavelet_Remain - 1],
            filter_bank_b1, &Cb1, &Lb1);
    

    // Ones
    vector<int> La1_sum(La1.size(), 1);
    int len_La1 = La1.size();
    
    // Let ii < La1.size() since La1[end] is len(signal)
    for (int ii = 2; ii <= La1.size(); ++ii) {
        La1_sum[ToCIndex(ii)] = sum(La1, ToCIndex(1), ToCIndex(ii-1));
    }


    // Sa_rec & Sb_rec init
    vector<vector<double>> Sa_rec = zeros(Wavelet_Remain.size() + 1, Signal.size());
    vector<vector<double>> Sb_rec = zeros(Wavelet_Remain.size() + 1, Signal.size());


    int len_La1_sum = La1_sum.size();
    for (int jj = 1; jj <= Wavelet_Remain.size(); ++jj) {
        auto C_tmp = vector<double>(La1_sum[len_La1_sum - 1], 0);

        auto St = len_La1 - Wavelet_Remain[ToCIndex(jj)];
        auto Sp = len_La1 - Wavelet_Remain[ToCIndex(jj)] + 1;

        //cout << "St = " << St
             //<< ", "
             //<< "Sp = " << Sp
             //<< endl;
        //cout << "Copying to :"
             //<< La1_sum[ToCIndex(St)]
             //<< ", "
             //<< La1_sum[ToCIndex(Sp)] - 1
             //<< endl;

        vector_copy<double>(
                C_tmp,
                La1_sum[ToCIndex(St)],
                La1_sum[ToCIndex(Sp)] - 1,
                Ca1,
                La1_sum[ToCIndex(St)],
                La1_sum[ToCIndex(Sp)] - 1
                );

        // Length check
        // length(C_tmp)
        // La1
        
        vector<vector<double>> filter_bank_ra1{{}, {}, H10a, H11a};

        //cout << "C_tmp " << endl;
        //for (int i = La1_sum[ToCIndex(St)]; i < La1_sum[ToCIndex(Sp)] - 1; ++i) {
            //cout << "["
                 //<< i
                 //<< "] = "
                 //<< C_tmp[i]
                 //<< ", Ca1[i] = "
                 //<< Ca1[i]
                 //<< endl;
        //}

        waverec(C_tmp, La1, filter_bank_ra1, &Sa_rec[ToCIndex(jj)]);
        
        //if (jj == 4) {
            //cout << "output data: toCindex = " << ToCIndex(jj) << endl;
            //OutputData(Sa_rec[ToCIndex(jj)]);
            ////cout << "La1 : " << endl;
            ////PrintVec(La1);
            //return;
        //}
        //
        //Sa_rec(jj,:) = waverec(C_tmp,La1,H10a,H11a);
        
        C_tmp = vector<double>(La1_sum[len_La1_sum - 1], 0);

        St = len_La1 - Wavelet_Remain[ToCIndex(jj)];
        Sp = len_La1 - Wavelet_Remain[ToCIndex(jj)] + 1;
        //St = La1.size() - Wavelet_Remain(jj);
        //Sp = La1.size() - Wavelet_Remain(jj) + 1;

        //C_tmp(La1_sum(St)+1:La1_sum(Sp))= Cb1(La1_sum(St)+1:La1_sum(Sp));
        vector_copy<double>(
                C_tmp,
                La1_sum[ToCIndex(St)],
                La1_sum[ToCIndex(Sp)] - 1,
                Cb1,
                La1_sum[ToCIndex(St)],
                La1_sum[ToCIndex(Sp)] - 1
                );

        // waverec
        vector<vector<double>> filter_bank_rb1{{}, {}, H10b, H11b};
        waverec(C_tmp, La1, filter_bank_rb1, &Sb_rec[ToCIndex(jj)]);
        //Sb_rec(jj,:)=waverec(C_tmp,La1,H10b,H11b);
        //if (jj == 1) {
            //cout << "output data: toCindex = " << ToCIndex(jj) << endl;
            ////OutputData(C_tmp);
            ////OutputData(Sb_rec[ToCIndex(jj)]);
            //cout << "La1 : " << endl;
            //PrintVec(La1);
            //return;
        //}
    }

    auto C_tmp = vector<double>(La1_sum[len_La1_sum - 1], 0);

    //C_tmp(1:La1_sum(2))= Ca1(1:La1_sum(2));
    vector_copy<double>(
            C_tmp,
            0,
            ToCIndex(La1_sum[1]),
            Ca1,
            0,
            ToCIndex(La1_sum[1])
            );

    int remain_index = Wavelet_Remain.size() + 1;
    // waverec
    vector<vector<double>> filter_bank_ra1{{}, {}, H10a, H11a};
    waverec(C_tmp, La1, filter_bank_ra1, &Sa_rec[ToCIndex(remain_index)]);

    C_tmp = vector<double>(La1_sum[len_La1_sum - 1], 0);
    vector_copy<double>(
            C_tmp,
            0,
            ToCIndex(La1_sum[1]),
            Cb1,
            0,
            ToCIndex(La1_sum[1])
            );
    vector<vector<double>> filter_bank_rb1{{}, {}, H10b, H11b};
    waverec(C_tmp, La1, filter_bank_rb1, &Sa_rec[ToCIndex(remain_index)]);
    //Sb_rec(jj+1,:)=waverec(C_tmp,La1,H10b,H11b);
    //S_rec=(Sa_rec+Sb_rec)./2;

    //debug
    //cout << Sa_rec.size() << ", " << Sb_rec.size() << endl;
    //for (int i = 0; i < Sa_rec.size(); ++i) {
        //cout << Sa_rec[i].size() 
             //<< ",  Sb_rec[i].size() = "
             //<< Sb_rec[i].size() << endl;
    //}

    Get_S_rec(Sa_rec, Sb_rec, s_rec);
}
