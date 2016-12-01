#include <cmath>
#include <iostream>
#include <string>
#include <complex>
#include <stdlib.h>
#include <fstream>

#include "wavelet2d.h"

using namespace std;

// Function Declaration
//
void* dwt1_udf(string wname, vector<double> &signal, vector<double> &cA, vector<double> &cD);

void* dwt_udf(vector<double> &sig, int J, string nm, vector<double> &dwt_output
                , vector<double> &flag, vector<int> &length ) {

        int Max_Iter;
                    Max_Iter = (int) ceil(log( double(sig.size()))/log (2.0)) - 2;

                    if ( Max_Iter < J) {
                      J = Max_Iter;

                    }

    vector<double> original_copy,orig, appx_sig, det_sig;
    original_copy = sig;

    // Zero Pad the Signal to nearest 2^ M value ,where M is an integer.
    unsigned int temp_len = sig.size();
        if ( (temp_len % 2) != 0) {
                double temp =sig[temp_len - 1];
                sig.push_back(temp);
                flag.push_back(1);
                temp_len++;
        } else {
                flag.push_back(0);
        }
        length.push_back(temp_len);
        flag.push_back(double(J));

    orig = sig;


        //  Storing Filter Values for GnuPlot
             vector<double> lp1,hp1,lp2,hp2;
             filtcoef(nm,lp1,hp1,lp2,hp2);

    /*
     * Self-defined filter bank.
     */
    
    //lp1 = vector<double>{0,0.0378284555073,- 0.0238494650196,- 0.110624404418,0.377402855613,0.852698679009,0.377402855613,- 0.110624404418,- 0.0238494650196,0.0378284555073};
    //hp1 = vector<double>{0,- 0.0645388826287,0.0406894176092,0.418092273222,- 0.788485616406,0.418092273222,0.0406894176092,- 0.0645388826287,0,0};
    //lp2 = vector<double>{0,- 0.0645388826287,- 0.0406894176092,0.418092273222,0.788485616406,0.418092273222,- 0.0406894176092,- 0.0645388826287,0,0};
    //hp2 = vector<double>{- 0.0238494650196,0.110624404418,0.377402855613,- 0.852698679009,0.377402855613,0.110624404418,- 0.0238494650196,- 0.0378284555073};

    for (int iter = 0; iter < J; iter++) {
        dwt1_udf(nm,orig, appx_sig, det_sig);
        dwt_output.insert(dwt_output.begin(),det_sig.begin(),det_sig.end());

        int l_temp = det_sig.size();
        length.insert(length.begin(),l_temp);

        if (iter == J-1 ) {
                dwt_output.insert(dwt_output.begin(),appx_sig.begin(),appx_sig.end());
                int l_temp2 = appx_sig.size();
                length.insert(length.begin(),l_temp2);

        }

        orig = appx_sig;
        appx_sig.clear();
        det_sig.clear();

    }

     sig = original_copy;
        return 0;
}

void* dwt1_udf(string wname, vector<double> &signal, vector<double> &cA, vector<double> &cD) {

        vector<double> lpd, hpd, lpr, hpr;

                //filtcoef(wname,lpd,hpd,lpr,hpr);

    /*
     * Self-defined filter bank.
     */
    
    lpd = vector<double>{0,0.0378284555073,- 0.0238494650196,- 0.110624404418,0.377402855613,0.852698679009,0.377402855613,- 0.110624404418,- 0.0238494650196,0.0378284555073};
    hpd = vector<double>{0,- 0.0645388826287,0.0406894176092,0.418092273222,- 0.788485616406,0.418092273222,0.0406894176092,- 0.0645388826287,0,0};
    lpr = vector<double>{0,- 0.0645388826287,- 0.0406894176092,0.418092273222,0.788485616406,0.418092273222,- 0.0406894176092,- 0.0645388826287,0,0};
    hpr = vector<double>{- 0.0238494650196,0.110624404418,0.377402855613,- 0.852698679009,0.377402855613,0.110624404418,- 0.0238494650196,- 0.0378284555073};



                int len_lpfilt = lpd.size();
                int len_hpfilt = hpd.size();
                int len_avg = (len_lpfilt + len_hpfilt) / 2;
                int len_sig = 2 * (int) ceil((double) signal.size() / 2.0);

                // cout << len_lpfilt << "Filter" << endl;
                per_ext(signal,len_avg / 2); // Periodic Extension
                // computations designed to deal with boundary distortions

                // Low Pass Filtering Operations in the Analysis Filter Bank Section
//		int len_cA =(int)  floor(double (len_sig + len_lpfilt -1) / double (2));
                vector<double> cA_undec;
                // convolving signal with lpd, Low Pass Filter, and O/P is stored in cA_undec
                convfft(signal,lpd,cA_undec);
                int D = 2; // Downsampling Factor is 2
                cA_undec.erase(cA_undec.begin(),cA_undec.begin()+len_avg-1);
                cA_undec.erase(cA_undec.end()-len_avg+1,cA_undec.end());
                cA_undec.erase(cA_undec.begin()+len_sig,cA_undec.end());
                cA_undec.erase(cA_undec.begin());


                // Downsampling by 2 gives cA
                downsamp(cA_undec, D, cA);

          //     cA.erase(cA.begin(),cA.begin()+len_avg/2);
          //      cA.erase(cA.end()-len_avg/2,cA.end());

                // High Pass Filtering Operations in the Analysis Filter Bank Section
//		int len_cA =(int)  floor(double (len_sig + len_lpfilt -1) / double (2));

                vector<double> cD_undec;
                // convolving signal with lpd, Low Pass Filter, and O/P is stored in cA_undec
                convfft(signal,hpd,cD_undec);
                cD_undec.erase(cD_undec.begin(),cD_undec.begin()+len_avg-1);
                cD_undec.erase(cD_undec.end()-len_avg+1,cD_undec.end());
                cD_undec.erase(cD_undec.begin()+len_sig,cD_undec.end());
                cD_undec.erase(cD_undec.begin());

                 // Downsampling Factor is 2

                // Downsampling by 2 gives cA
                downsamp(cD_undec, D, cD);

    //            cD.erase(cD.begin(),cD.begin()+len_avg/2);
      //          cD.erase(cD.end()-len_avg/2,cD.end());

                filtcoef(wname,lpd,hpd,lpr,hpr);

  return 0;
}


void Test1() {
    vector<double> sig(10000, 12);
    vector<double> coef, flag;
    vector<int> L;

    dwt(sig, 5, "db2", coef, flag, L);

    cout << "sig size = " << sig.size() << endl;
    cout << "Coef size = " << coef.size() << endl;
    cout << "L size = " << L.size() << endl;
    cout << L[0] << endl;
    cout << "flag size = " << flag.size() << endl;
    cout << flag[0] << endl;
    cout << flag[1] << endl;
}

void ReadSignalFromFile(const string& file_name, vector<double>* sig_out) {
    fstream fin(file_name.c_str(), fstream::in);
    int sig_len;

    fin >> sig_len;
    sig_out->clear();
    for (int i = 0; i < sig_len; ++i) {
        double tmp;
        fin >> tmp;
        sig_out->push_back(tmp);
    }
    
    fin.close();
}

void OutputCoefToFile(const string& file_name, vector<double>& coef) {
    
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

    dwt_udf(sig, 5, "db2", coef, flag, L);

    cout << "sig size = " << sig.size() << endl;
    cout << "Coef size = " << coef.size() << endl;
    cout << "L size = " << L.size() << endl;
    cout << L[0] << endl;
    cout << "flag size = " << flag.size() << endl;
    cout << flag[0] << endl;
    cout << flag[1] << endl;

    string output_file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/"
            "wt_cpp_api/ecg-samples/coef_out.txt";
    OutputCoefToFile(output_file_name, coef);
}

int main() {

    Test2();

return 0;}
