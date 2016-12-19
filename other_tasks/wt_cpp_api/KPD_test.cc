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
#include "wt_detect.h"
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

// Output labeled results to file.
template <typename T1, typename T2>
static void OutputLabeledResultsToFile(const string& file_name,
                                       vector<pair<T1, T2>>& results) {
    
    fstream fout(file_name.c_str(), fstream::out);
    fout << results.size() << endl;
    for (const auto& item: results) {
        fout << item.first << " " << item.second << endl;
    }

    fout.close();
}

// debug function
static void OutputS_rec(vector<vector<double>>& s_rec) {
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
static void FormatKpdInput(vector<vector<double>>& s_rec_vec,
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

// Resampling input signal
static void Resample(vector<double>& sig_in, int fs_in, int fs_out,
                     vector<double>* sig_out) {
    // TODO: upsample
    if (fs_out >= fs_in) return;
    if (fs_out == 0 || fs_in == 0) return ;

    sig_out->clear();

    // Downsampling
    int len_sig_original = sig_in.size();
    int len_sig_new = static_cast<long long>(len_sig_original) * fs_out / fs_in;
    
    for (int i = 0; i < len_sig_new; ++i) {
        double pos = (double)i * fs_in / fs_out;
        double lower_pos = floor(pos);
        double upper_pos = ceil(pos);

        double val_left = sig_in[static_cast<int>(lower_pos)];
        double val_right = val_left;
        if (static_cast<int>(upper_pos) < len_sig_original) {
            val_right = sig_in[static_cast<int>(upper_pos)];
        }

        double val = val_left + (val_right - val_left) * (pos - lower_pos);
        sig_out->push_back(val);
    }
    return;
}

// The testing API
static void Testing_local(vector<double>& signal_in, double fs,
        vector<pair<char, int>>* result_out) {
    
    // Resampling
    vector<double> signal_resampled;
    int fs_input = static_cast<int>(round(fs));
    if (fs_input > 360) {
        Resample(signal_in, fs_input, 360, &signal_resampled);
    } else {
        signal_resampled = signal_in;
    }

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
    int len_signal = signal_resampled.size();

    // Wavelet transform
    DTCWT(signal_resampled, 9, Wavelet_Remain, filter_bank, &s_rec);
    // Cutoff tail part of the signal.
    for (auto& vec: s_rec) {
        vec.resize(signal_resampled.size());
    }

    //OutputS_rec(s_rec);

    // Detection result
    vector<pair<char, int>> ret;
    unique_ptr<double[]> s_rec_in(new double[len_signal * 10]());
    FormatKpdInput(s_rec, s_rec_in.get(), 10, len_signal);
    
    call_simple_function(s_rec_in.get(),
            len_signal,
            360.0,
            result_out);
}


static void TEST1(string signal_file_name) {
    // Read ECG signal from file.
    vector<double> sig;
    string file_name = signal_file_name;

    cout << "Testing() input file name:" 
         << file_name
         << endl;
    ReadSignalFromFile(file_name, &sig);

    // Output vector
    vector<pair<char, int>> detect_result;
    Testing(sig, 250.0, &detect_result); 

    vector<int> qrs_results;
    for (auto& item: detect_result) {
        if (item.first == 'R') {
            qrs_results.push_back(item.second);
        }
    }

    //OutputCoefToFile("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/c_output/result.dat", qrs_results);
    OutputLabeledResultsToFile("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/c_output/result.dat", detect_result);
}

int main(int argv, char** argc) {

    srand(time(NULL));
    TEST1(string(argc[1]));

    return 0;
}

