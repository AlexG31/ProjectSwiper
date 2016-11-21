#include "wavedec_api.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>

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

// Rewrite dwt1 to accept customized wavelet filter coefficients.
static void dwt1_sym(
    vector<vector<double>> filter_bank,
    vector<double> &signal,
    vector<double> &cA,
    vector<double> &cD) {

    vector<double> lp1, hp1, lp2, hp2;
    lp1 = filter_bank[0];
    hp1 = filter_bank[1];
    lp2 = filter_bank[2];
    hp2 = filter_bank[3];

    // Get filter coefs base on wname.
    //filtcoef(wname,lp1,hp1,lp2,hp2);

    int D = 2; // Downsampling Factor is 2
    int lf = lp1.size();
    symm_ext(signal,lf-1);

    vector<double> cA_undec;
    //sig value
    convfft(signal,lp1,cA_undec);
    cA_undec.erase(cA_undec.begin(),cA_undec.begin()+lf);
    cA_undec.erase(cA_undec.end()-lf+1,cA_undec.end());
    downsamp(cA_undec, D, cA);


    //High Pass Branch Computation
    vector<double> cD_undec;
    convfft(signal,hp1,cD_undec);
    cD_undec.erase(cD_undec.begin(),cD_undec.begin()+lf);
    cD_undec.erase(cD_undec.end()-lf+1,cD_undec.end());
    downsamp(cD_undec,D,cD);

    //filtcoef(wname,lp1,hp1,lp2,hp2);

    return ;
}

// Rewrite the idwt1_sym to accept filter_bank input.
static void idwt1_sym_m(
        vector<vector<double>> filter_bank,
        vector<double> &idwt_output,
        vector<double> &app,
        vector<double> &detail) {

    int U = 2; // Upsampling Factor
    vector<double> lpd1,hpd1, lpr1, hpr1;

    //filtcoef(wname,lpd1,hpd1,lpr1,hpr1);
    lpd1 = filter_bank[0];
    hpd1 = filter_bank[1];
    lpr1 = filter_bank[2];
    hpr1 = filter_bank[3];

    int lf = lpr1.size();

    // Operations in the Low Frequency branch of the Synthesis Filter Bank
    vector<double> X_lp;
    vector<double> cA_up;
    upsamp(app, U,cA_up );
    cA_up.pop_back();
    convfftm(cA_up, lpr1, X_lp);



    // Operations in the High Frequency branch of the Synthesis Filter Bank

    vector<double> X_hp;
    vector<double> cD_up;
    upsamp(detail, U, cD_up);
    cD_up.pop_back();
    convfftm(cD_up, hpr1, X_hp);


    vecsum(X_lp,X_hp,idwt_output);

    idwt_output.erase(idwt_output.begin(),idwt_output.begin()+lf-2);
    idwt_output.erase(idwt_output.end()-(lf - 2),idwt_output.end());

   return ;
}

// API functions
void wavedec(vector<double>& signal, int dwt_level, 
        vector<vector<double>>& filter_bank,
        vector<double>* coefs,
        vector<int>* lengths) {

    if (signal.empty()) {
        cout << "Error: signal input is empty()!" << endl;
        return;
    }

    // Init output buffers.
    lengths->clear();
    coefs->clear();
    
    // Put the lengths in reverse order, than reverse it at end.
    lengths->push_back(signal.size());

    vector<vector<double>> coef_vector;
    vector<double> cA, cD;
    cA = signal;

    // Dwt decomposition for dwt_level levels.
    for (int i = 0; i < dwt_level; ++i) {
        vector<double> next_cA;
        cD.clear();

        dwt1_sym(filter_bank, cA, next_cA, cD);
        
        // Store cDi & its length.
        coef_vector.push_back(cD);
        lengths->push_back(cD.size());

        cA = next_cA;
    }
    
    // Form coefs
    coefs->insert(coefs->end(), cA.begin(), cA.end());
    for (int i = dwt_level - 1; i >= 0; --i) {
        auto& cDi_vec = coef_vector[i];
        coefs->insert(coefs->end(), cDi_vec.begin(), cDi_vec.end());
    }
    
    // Reverse the order of lengths->
    lengths->push_back(cA.size());
    reverse(lengths->begin(), lengths->end());
    
    return;
}

void waverec(vector<double>& coefs,vector<int>& lengths,
        vector<vector<double>>& filter_bank,
        vector<double>* sig_out) {
    
    // Init sig_out
    sig_out->clear();
    
    
    int len_lengths = lengths.size();
    int dwt_level = len_lengths - 2;

    // Padding zeros in coefs.
    int common_length = 0;
    for (int i = 0; i < len_lengths - 1; ++i) common_length += lengths[i];

    if (coefs.size() < common_length) {
        int padding_count = common_length - coefs.size();
        coefs.insert(coefs.end(), padding_count, 0);
    }

    if (len_lengths < 3) {
        cout << "Error: lengths.size() should >= 3!" << endl;
        return;
    }

    int start_index = 0;
    vector<double> cA, cD;
    cA.assign(coefs.begin() + start_index, coefs.begin() + start_index + lengths[0]);
    start_index += lengths[0];

    for (int i = 0; i < dwt_level; ++i) {
        cD.assign(coefs.begin() + start_index, coefs.begin() + start_index + lengths[i + 1]);
        start_index += lengths[i + 1];

        // cA & cD should have equal length.
        //if (cA.size() != cD.size()) {
            
            //cout << cA.size() << ", cD.size() = " << cD.size() << endl;
            //cout << "Error: cA and cD have different length!" << endl;
            //for (const auto& val: lengths) cout << val << endl;

            //return ;
        //}
        
        vector<double> next_cA;
        idwt1_sym_m(filter_bank, next_cA, cA, cD);
        cA = next_cA;
    }
    
    sig_out->assign(cA.begin(), cA.end());

    return;
}
