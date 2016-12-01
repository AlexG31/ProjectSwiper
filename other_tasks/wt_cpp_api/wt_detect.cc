#include <cmath>
#include <iostream>
#include <string>
#include <complex>
#include <stdlib.h>
#include <vector>
#include <memory>
#include <fstream>
#include <ctime>

#include "wavelet_udfs.h"
#include "DTCWT.h"
#include "call_simple_function/call_simple_function_emxutil.h"
#include "call_simple_function/call_simple_function_types.h"
#include "call_simple_function/call_simple_function.h"

using namespace std;

// Test functions.
template <typename T>
static void ReadSignalFromFile(const string& file_name, vector<T>* sig_out) {
    fstream fin(file_name.c_str(), fstream::in);
    int sig_len;

    fin >> sig_len;
    sig_out->clear();
    for (int i = 0; i < sig_len; ++i) {
        T tmp;
        fin >> tmp;
        sig_out->push_back(tmp);
    }
    
    fin.close();
}

template <typename T>
static void OutputCoefToFile(const string& file_name, vector<T>& coef) {
    
    fstream fout(file_name.c_str(), fstream::out);
    fout << coef.size() << endl;
    for (const auto& val: coef) {
        fout << val << endl;
    }

    fout.close();
}

// debug function
void OutputS_rec(vector<vector<double>>& s_rec) {
    int len_s_rec = s_rec.size();
    string file_name_prefix = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
                              "wt_cpp_api/s_rec/";

    for (int i = 0; i < len_s_rec; ++i) {
        OutputCoefToFile(file_name_prefix + "s_rec" + to_string(i) + ".txt",
                s_rec[i]);
    }
}

// Convert c++ vector into double* for c code.
// Input :
//  row & col may exceed s_rec_vec's size
void FormatKpdInput(vector<vector<double>>& s_rec_vec,
        double* s_rec_out,
        int row,
        int col) {
    // Assume s_rec_out have pre-allocted enough memory.
    int vec_row = s_rec_vec.size();

    for (int i = 0; i < row; ++i) {
        int vec_col = s_rec_vec[i].size();
        for (int j = 0; j < col; ++j) {
            double val = 0;
            // only fill data with in s_rec_vec's range
            if (i < vec_row && j < vec_col) val = s_rec_vec[i][j];
            s_rec_out[i + row * j] = val;
        }
    }
    return;
}

// The testing API
void Testing(vector<double>& signal_in, double fs,
        vector<pair<char, int>>* result_out) {
    
    // Filter Coefficients
    vector<double> Lp1_D{0,0.0378284555072640,-0.0238494650195568,
        -0.110624404418437,0.377402855612831,0.852698679008894,
        0.377402855612831,-0.110624404418437,-0.0238494650195568,
        0.0378284555072640};
    vector<double> Hp1_D{0,-0.0645388826286971,0.0406894176091641,
        0.418092273221617,-0.788485616405583,0.418092273221617,
        0.0406894176091641,-0.0645388826286971,0,0};
    vector<double> Lp1_R{0,-0.0645388826286971,-0.0406894176091641,
        0.418092273221617,0.788485616405583,0.418092273221617,
        -0.0406894176091641,-0.0645388826286971,0,0};
    vector<double> Hp1_R{0, -0.0378284555072640, -0.0238494650195568,
        0.110624404418437, 0.377402855612831, -0.852698679008894,
        0.377402855612831, 0.110624404418437, -0.0238494650195568,
        -0.0378284555072640};
    vector<vector<double>> filter_bank{Lp1_D, Hp1_D, Lp1_R, Hp1_R};

    // Input for DTCWT
    vector<int> Wavelet_Remain;
    for (int i = 1; i <= 9; ++i) {
        Wavelet_Remain.push_back(i);
    }

    // Cut signal segment
    vector<vector<double>> s_rec;
    int len_signal = signal_in.size();

    // Wavelet transform
    DTCWT(signal_in, 9, Wavelet_Remain, filter_bank, &s_rec);

    // Detection result
    vector<pair<char, int>> ret;
    unique_ptr<double[]> s_rec_in(new double[len_signal * 10]());
    FormatKpdInput(s_rec, s_rec_in.get(), 10, len_signal);
    
    emxArray_real_T *y_out;
    emxInit_real_T(&y_out, 2);
    call_simple_function(s_rec_in.get(),
            len_signal,
            360.0,
            y_out,
            result_out);
}

// [Debug] Testing function For Testing api
void Testing() {
    
    string file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/mit-100.txt";

    cout << "Testing() input file name:" 
         << file_name
         << endl;
    
    vector<double> sig;
    ReadSignalFromFile(file_name, &sig);

    vector<double> coef, flag;
    vector<int> L;

    auto start_time = time(NULL);
    cout << "start_time = " << start_time << endl;
    cout << "Clock_per_sec:" << CLOCKS_PER_SEC << endl;

    // Filter banks.
    vector<double> Lp1_D{0,0.0378284555072640,-0.0238494650195568,
        -0.110624404418437,0.377402855612831,0.852698679008894,
        0.377402855612831,-0.110624404418437,-0.0238494650195568,
        0.0378284555072640};
    vector<double> Hp1_D{0,-0.0645388826286971,0.0406894176091641,
        0.418092273221617,-0.788485616405583,0.418092273221617,
        0.0406894176091641,-0.0645388826286971,0,0};
    vector<double> Lp1_R{0,-0.0645388826286971,-0.0406894176091641,
        0.418092273221617,0.788485616405583,0.418092273221617,
        -0.0406894176091641,-0.0645388826286971,0,0};
    vector<double> Hp1_R{0, -0.0378284555072640, -0.0238494650195568,
        0.110624404418437, 0.377402855612831, -0.852698679008894,
        0.377402855612831, 0.110624404418437, -0.0238494650195568,
        -0.0378284555072640};
    vector<vector<double>> filter_bank{Lp1_D, Hp1_D, Lp1_R, Hp1_R};

    // Input for DTCWT
    vector<int> Wavelet_Remain;
    for (int i = 1; i <= 9; ++i) {
        Wavelet_Remain.push_back(i);
    }

    vector<vector<double>> s_rec;
    // Cut signal segment
    vector<double> sig_segment(sig.begin(), sig.end());
    DTCWT(sig_segment, 9, Wavelet_Remain, filter_bank, &s_rec);
    //return;

    // debug output
    OutputS_rec(s_rec);

    cout << "DTCWT time cost:"
         << time(NULL) - start_time 
         << "secs"
         << endl;
    start_time = time(NULL);

    //
    // Detection result
    vector<pair<char, int>> ret;
    cout << "s_rec.size() = " 
         << s_rec.size()
         << ", "
         << s_rec[0].size() << endl;
    //KPD(s_rec, s_rec[0].size(), 360.0, &ret);
    unique_ptr<double[]> s_rec_in(new double[6500000]());
    FormatKpdInput(s_rec, s_rec_in.get(), 10, 650000);
    
    emxArray_real_T *y_out;


    emxInit_real_T(&y_out, 2);
    call_simple_function(s_rec_in.get(),
            650000,
            360.0,
            y_out,
            &ret);

    cout << "simple function time:"
         << time(NULL) - start_time 
         << "secs"
         << endl;



    cout << "=======================" << endl;
    cout << "Result.size() = " << ret.size() << endl;

    for (const auto& item: ret) {
        cout << "Result: "
             << item.first
             << "   -> "
             << item.second
             << endl;
    }

    return ;
}

static void TEST1() {
    // Read ECG signal from file.
    vector<double> sig;
    string file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/mit-101.txt";

    cout << "Testing() input file name:" 
         << file_name
         << endl;
    ReadSignalFromFile(file_name, &sig);

    // Output vector;
    vector<pair<char, int>> detect_result;
    Testing(sig, 360.0, &detect_result); 
    cout << "=======================" << endl;
    cout << "Result.size() = " << detect_result.size() << endl;

    for (const auto& item: detect_result) {
        cout << "Result: "
             << item.first
             << "   -> "
             << item.second
             << endl;
    }
}

int main() {

    TEST1();

    return 0;
}

