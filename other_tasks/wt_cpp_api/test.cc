#include <cmath>
#include <iostream>
#include <string>
#include <complex>
#include <stdlib.h>
#include <vector>
#include <fstream>

#include "wavelet_udfs.h"
#include "DTCWT.h"

using namespace std;

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

void Test2() {
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

    wavedec_udf(sig, 5, filter_bank, coef, flag, L);

    cout << "sig size = " << sig.size() << endl;
    cout << "Wavedec coef size = " << coef.size() << endl;
    

    // Output coefs
    int debug_count = 10;
    for (const auto& val: coef) {
        cout << val << ", ";
        if (debug_count-- < 0) break;
    }
    cout << endl;


    cout << "L size = " << L.size() << endl;


    // Output length array.
    for (const auto& val: L) {
        cout << val << ", ";
    }
    cout << endl;


    cout << "flag size = " << flag.size() << endl;
    cout << flag[0] << endl;
    cout << flag[1] << endl;

    // Output to File
    string output_file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/coef_out.txt";
    OutputCoefToFile(output_file_name, coef);

    output_file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/len_out.txt";
    OutputCoefToFile(output_file_name, L);
}

void Test3() {
    string file_name;

    vector<double> coef, flag;
    vector<int> L;

    // Read input signal from file
    file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/coef_out.txt";
    ReadSignalFromFile(file_name, &coef);
    file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/len_out.txt";
    ReadSignalFromFile(file_name, &L);

    vector<double> sig;

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

    for (const auto& layer : filter_bank) {
        cout << "filter bank layer size= "
             << layer.size()
             << endl;
    }

    waverec_udf_noflag(coef, L, filter_bank, sig);

    cout << "sig size = " << sig.size() << endl;
    

    // Output coefs
    int debug_count = 10;
    for (const auto& val: sig) {
        cout << val << ", ";
        if (debug_count-- < 0) break;
    }
    cout << endl;

    // Output to File
    string output_file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/rec_sig_out.txt";
    OutputCoefToFile(output_file_name, sig);
}

void Test4() {
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

    cout << "s_rec size = " << s_rec.size() << endl;
    for (int i = 0; i < s_rec.size(); ++i) {
        cout << "s_rec["
             << i
             << "].size() = " << s_rec[i].size() << endl;
        string output_file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
                "wt_cpp_api/ecg-samples/s_rec_" +
                string(1, 'a' + i) + 
                "_out.txt";
        OutputCoefToFile(output_file_name, s_rec[i]);
    }
}

int main() {

    Test4();

return 0;}
