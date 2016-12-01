#include "../shared/wavelet2d.h"
#include "../shared/wavedec_api.h"

#include <iostream>
#include <fstream>
#include <vector>

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

//void* dwt1_sym(string wname, vector<double> &signal, vector<double> &cA, vector<double> &cD) {
static void TEST1() {

    // Read ECG signal.
    string file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/mit-100.txt";
    cout << "Testing() input file name:" 
         << file_name
         << endl;
    
    vector<double> sig;
    ReadSignalFromFile(file_name, &sig);

    // Limit signal length.
    vector<double> sig_segment{1};
    //sig_segment.assign(sig.begin(), sig.begin() + 1000);
    cout << "signal length: " << sig_segment.size() << endl;

    // Decomposed wavelet coefficients.
    vector<double> cA, cD;
    dwt1_sym("db2", sig_segment, cA, cD);

    cout << "cA size = " << cA.size() << endl;
    cout << "cD size = " << cD.size() << endl;

    // Output coef to file.
    string tmp_filename = 
        "/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/"
        "wavelib/src/test/tmp.out";
    OutputCoefToFile(tmp_filename, cD);
    cout << "Coefficients write to file:"
         << tmp_filename
         << endl;
    
    return;
}

static void TEST2() {

    // Read ECG signal.
    string file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/mit-100.txt";
    cout << "Testing() input file name:" 
         << file_name
         << endl;
    
    vector<double> sig;
    ReadSignalFromFile(file_name, &sig);

    // Limit signal length.
    vector<double> sig_segment;
    sig_segment.assign(sig.begin(), sig.begin() + 1000);
    cout << "signal length: " << sig_segment.size() << endl;

    // Filter banks
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

    // Decomposed wavelet coefficients.
    vector<double> cA, cD;
    vector<int> lengths;

    // Call wavedec API
    wavedec(sig_segment, 5, filter_bank, &cA, &lengths);

    // Display wavedec statistics
    cout << "cA size = " << cA.size() << endl;
    cout << "lengths size = " << lengths.size() << endl;
    for (int &val: lengths) {
        cout << val << endl;
    }

    // Call waverec API
    waverec(cA, lengths, filter_bank, &sig_segment);
    cout << "Reconstruction sig size = " << sig_segment.size() << endl;

    // Output coef to file.
    string tmp_filename = 
        "/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/"
        "wavelib/src/test/tmp.out";
    OutputCoefToFile(tmp_filename, sig_segment);
    cout << "Coefficients write to file:"
         << tmp_filename
         << endl;
    
    return;
}

int main() {
    TEST2();
    return 0;
}
