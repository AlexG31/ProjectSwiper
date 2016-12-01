#include <cmath>
#include <iostream>
#include <string>
#include <complex>
#include <stdlib.h>
#include <assert.h>
#include <fstream>

#include "wavelet2d.h"

using namespace std;

// Function Declaration

void* dwt1_udf(
        vector<vector<double>>& filter_bank,
        vector<double> &signal,
        vector<double> &cA,
        vector<double> &cD);

void* idwt1_udf(vector<vector<double>>& filter_bank,
        vector<double> &X,
        vector<double> &cA,
        vector<double> &cD);



// Function Implementation
// Inputs:
//  J: DWT level
void* wavedec_udf(
        vector<double> &sig,
        int J,
        vector<vector<double>>& filter_bank,
        vector<double> &dwt_output,
        vector<double> &flag,
        vector<int> &length) {

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
        // NOTE: Keep consistent with matlab wavedec function.
        length.push_back(temp_len);
        flag.push_back(double(J));

    orig = sig;


        //  Storing Filter Values for GnuPlot
             //vector<double> lp1,hp1,lp2,hp2;
             //filtcoef(nm,lp1,hp1,lp2,hp2);


    for (int iter = 0; iter < J; iter++) {
        dwt1_udf(filter_bank, orig, appx_sig, det_sig);
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

void* dwt1_udf(vector<vector<double>>& filter_bank,
        vector<double> &signal,
        vector<double> &cA,
        vector<double> &cD) {

        vector<double> lpd, hpd, lpr, hpr;
        assert(filter_bank.size() == 4);

        lpd = filter_bank[0];
        hpd = filter_bank[1];
        lpr = filter_bank[2];
        hpr = filter_bank[3];

    /*
     * Self-defined filter bank.
     */
    
    //lpd = vector<double>{0,0.0378284555073,- 0.0238494650196,- 0.110624404418,0.377402855613,0.852698679009,0.377402855613,- 0.110624404418,- 0.0238494650196,0.0378284555073};
    //hpd = vector<double>{0,- 0.0645388826287,0.0406894176092,0.418092273222,- 0.788485616406,0.418092273222,0.0406894176092,- 0.0645388826287,0,0};
    //lpr = vector<double>{0,- 0.0645388826287,- 0.0406894176092,0.418092273222,0.788485616406,0.418092273222,- 0.0406894176092,- 0.0645388826287,0,0};
    //hpr = vector<double>{- 0.0238494650196,0.110624404418,0.377402855613,- 0.852698679009,0.377402855613,0.110624404418,- 0.0238494650196,- 0.0378284555073};



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

                //filtcoef(wname,lpd,hpd,lpr,hpr);

  return 0;
}



void* waverec_udf_noflag(
        vector<double> &dwtop,
        vector<int> &length,
        vector<vector<double>>& filter_bank,
        vector<double> &idwt_output) {

        // Level number of idwt
        int J = static_cast<int>(length.size()) - 2;

        //cout << "J = " << J << endl;
        //cout << "dwtop.size() = " << dwtop.size() << endl;

            vector<double> app;
            vector<double> detail;
            unsigned int app_len = length[0];
            unsigned int det_len = length[1];

        vector<double>::iterator dwt;
        dwt = dwtop.begin();
        app.assign(dwt,dwtop.begin()+app_len);
        detail.assign(dwtop.begin()+app_len, dwtop.begin()+ 2* app_len);

            for (int i = 0; i < J; i++) {

                idwt1_udf(filter_bank,idwt_output, app,detail);
                app_len +=det_len;
                app.clear();
                detail.clear();
                        if ( i < J - 1 ) {
                            det_len = length[i+2];
                            for (unsigned int l = 0; l < det_len;l++) {

                                double temp = dwtop[app_len + l];
                                detail.push_back(temp);
                            }
                            app = idwt_output;

                            if (app.size() >= detail.size()){
                                int t = app.size() - detail.size();
                               int lent = (int) floor((double)t/2.0);
                               app.erase(app.begin()+detail.size()+lent,app.end());
                               app.erase(app.begin(),app.begin()+lent);
                            }
                        }
            }


            // Remove ZeroPadding

            // Remove or Add ZeroPadding
            //cout << "idwt_output.size() = " 
                 //<< idwt_output.size() << endl;

            if (idwt_output.size() > dwtop.size()) {
                //cout << "IDWT: Erasing zeros."
                     //<< idwt_output.size() - dwtop.size()
                     //<< endl;

                int zerop = static_cast<int>(idwt_output.size()) -
                    static_cast<int>(dwtop.size());
                idwt_output.erase(idwt_output.end()- zerop,idwt_output.end());
            } else if (idwt_output.size() < dwtop.size()) {
                //cout << "IDWT: Padding zeros." 
                     //<< dwtop.size() - idwt_output.size()
                     //<< endl;

                int zerop = static_cast<int>(idwt_output.size()) -
                    static_cast<int>(dwtop.size());
                for (int i = 0; i < zerop; ++i) {
                    idwt_output.push_back(0);
                }
            }

            return 0;
}

void* waverec_udf(vector<double> &dwtop,
        vector<double> &flag,
        vector<vector<double>>& filter_bank,
        vector<double> &idwt_output,
        vector<int> &length) {

        int J =(int) flag[1];

        vector<double> app;
        vector<double> detail;
        unsigned int app_len = length[0];
        unsigned int det_len = length[1];

        vector<double>::iterator dwt;
        dwt = dwtop.begin();
        app.assign(dwt, dwtop.begin()+app_len);
        detail.assign(dwtop.begin()+app_len, dwtop.begin()+ 2* app_len);

            for (int i = 0; i < J; i++) {

                idwt1_udf(filter_bank,idwt_output, app,detail);
                app_len += det_len;
                app.clear();
                detail.clear();
                        if ( i < J - 1 ) {
                            det_len = length[i+2];
                            for (unsigned int l = 0; l < det_len;l++) {

                                double temp = dwtop[app_len + l];
                                detail.push_back(temp);
                            }
                            app = idwt_output;

                            if (app.size() >= detail.size()){
                                int t = app.size() - detail.size();
                               int lent = (int) floor((double)t/2.0);
                               app.erase(app.begin()+detail.size()+lent,app.end());
                               app.erase(app.begin(),app.begin()+lent);
                            }
                        }




//            int value1 = (int) ceil((double)(app.size() - det_len)/2.0);
//           int value2 = (int) floor((double)(app.size() - det_len)/2.0);

//            app.erase(app.end() -value2,app.end());
//           app.erase(app.begin(),app.begin()+value1);

            }


            // Remove or Add ZeroPadding
            int zerop = (int)flag[0];
            idwt_output.erase(idwt_output.end()- zerop,idwt_output.end());

            return 0;
}



void* idwt1_udf(vector<vector<double>>& filter_bank,
        vector<double> &X,
        vector<double> &cA,
        vector<double> &cD) {

        vector<double> lpd1,hpd1, lpr1, hpr1;

        lpd1 = filter_bank[0];
        hpd1 = filter_bank[1];
        lpr1 = filter_bank[2];
        hpr1 = filter_bank[3];
        //filtcoef(wname,lpd1,hpd1,lpr1,hpr1);

        int len_lpfilt = lpr1.size();
        int len_hpfilt = hpr1.size();
        int len_avg = (len_lpfilt + len_hpfilt) / 2;
        unsigned int N = 2 * cD.size();
        int U = 2; // Upsampling Factor

        // Operations in the Low Frequency branch of the Synthesis Filter Bank

        vector<double> cA_up;
        vector<double> X_lp;
       // int len1 = cA_up.size();
        upsamp(cA, U, cA_up);

        per_ext(cA_up,len_avg/2);


        convfft(cA_up, lpr1, X_lp);


        // Operations in the High Frequency branch of the Synthesis Filter Bank

        vector<double> cD_up;
        vector<double> X_hp;
        upsamp(cD, U, cD_up);
        per_ext(cD_up,len_avg/2);


        convfft(cD_up, hpr1, X_hp);

   // Remove periodic extension

     //   X.erase(X.begin(),X.begin()+len_avg+len_avg/2-1);
     //   X.erase(X.end()-len_avg-len_avg/2,X.end());


        X_lp.erase(X_lp.begin()+N+len_avg-1,X_lp.end());
        X_lp.erase(X_lp.begin(),X_lp.begin()+len_avg-1);

        X_hp.erase(X_hp.begin()+N+len_avg-1,X_hp.end());
        X_hp.erase(X_hp.begin(),X_hp.begin()+len_avg-1);


        vecsum(X_lp,X_hp,X);


    return 0;
}
