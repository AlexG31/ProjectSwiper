#include <cmath>
#include <iostream>
#include <string>
#include <complex>
#include <stdlib.h>
#include <vector>
#include <fstream>

#include "wavelet_udfs.h"
#include "DTCWT.h"
#include "call_simple_function_emxutil.h"
#include "KPD.h"

using namespace std;

// Test functions.
template <typename T>
void ReadSignalFromFile(const string& file_name, vector<T>* sig_out) {
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
void OutputCoefToFile(const string& file_name, vector<T>& coef) {
    
    fstream fout(file_name.c_str(), fstream::out);
    fout << coef.size() << endl;
    for (const auto& val: coef) {
        fout << val << endl;
    }

    fout.close();
}

void Testing(vector<double>& signal_in, double fs,
        vector<pair<char, int>>* result_out) {
    
    vector<double> coef, flag;
    vector<int> L;

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

    vector<int> Wavelet_Remain;
    for (int i = 1; i <= 9; ++i) {
        Wavelet_Remain.push_back(i);
    }

    vector<vector<double>> s_rec;
    DTCWT(signal_in, 9, Wavelet_Remain, &s_rec);

    // Detect QRS, P, T positions
    KPD(s_rec, s_rec[0].size(), 360.0, result_out);
    cout << "Result.size() = " << result_out->size() << endl;

}

// Testing function For Testing api
void Testing() {
    
    string file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/sig_in.txt";

    vector<double> sig;
    ReadSignalFromFile(file_name, &sig);

    vector<double> coef, flag;
    vector<int> L;

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

    vector<int> Wavelet_Remain;
    for (int i = 1; i <= 9; ++i) {
        Wavelet_Remain.push_back(i);
    }

    vector<vector<double>> s_rec;
    DTCWT(sig, 9, Wavelet_Remain, &s_rec);

    // Detect QRS, P, T positions
    vector<pair<char, int>> ret;
    //cout << "s_rec.size() = " 
         //<< s_rec.size()
         //<< ", "
         //<< s_rec[0].size() << endl;
    KPD(s_rec, 10000, 360.0, &ret);
    cout << "Result.size() = " << ret.size() << endl;

    for (const auto& item: ret) {
        cout << "Result: "
             << item.first
             << "   -> "
             << item.second
             << endl;
    }

}

int main() {

    Testing();

    return 0;
}

