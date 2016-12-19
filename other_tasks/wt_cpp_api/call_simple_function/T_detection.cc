/*
 * File: T_detection.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "T_detection.h"
#include "call_simple_function_emxutil.h"
#include "eml_sort.h"
#include "floor.h"
#include "rdivide.h"
#include "mean.h"
#include "power.h"

#include <iostream>
#include <fstream>
#include <assert.h>
#include <cmath>
#include <vector>
#include <unordered_map>
#include <memory>
#include <algorithm>

using namespace std;

#define debug false

#define eps 1e-6
#define math_e 2.71828182846
#define k_BucketThreshold  2147483647.0
/* Function Definitions */

void NormalizeT_detector(emxArray_real_T *T_detector, double BucketThreshold= 2147483647.0);
int mode(emxArray_real_T *T_detector);
void copy_data(double* , int, double*, int, int);
double *gaussian_function(int lttmp, double g_mean, double g_std);
double mean(double* buffer, int buffer_length);
double find_max_in_buffer(double* buffer, int buffer_length, int& );
double find_min_in_buffer(double* buffer, int buffer_length, int& );
double std_error(double* buffer, int buffer_length);

/*
 * T_DETECTION Summary of this function goes here
 *    Detailed explanation goes here
 *  In this function, T wave would be detected first according to the
 *  calculated QRS location beat by beat, After the T wave detection, P wave
 *  would be detected between the T wave to the next QRS complex
 * Arguments    : emxArray_real_T *T_detector
 *                double fs
 *                const emxArray_real_T *x_QRS
 *                double x_start
 *                emxArray_real_T *T_Location_cur
 *                emxArray_real_T *P_Location_cur
 * Return Type  : void
 */

void ShowData_T(emxArray_real_T* result, string name = "data") {
    cout << name + "->size = "
         << result->allocatedSize
         << endl;

    for (int i = 0; i < result->allocatedSize; ++i) {
        cout << "val = "
             << result->data[i]
             << endl;
    }
}

void OutputData(double* buffer, int len) {
    fstream fs("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/tmp.out",
            fstream::out);

    fs << len << endl;
    for (int i = 0; i < len; ++i) {
        fs << fixed;
        //fs << setprecision(17);
        fs.precision(17);
        fs << buffer[i] << endl;
    }

    fs.close();
}

void T_detection(emxArray_real_T *T_detector, double fs, const emxArray_real_T
                 *x_QRS, double x_start, emxArray_real_T *T_Location_cur_out,
                 emxArray_real_T *P_Location_cur_out)
{
    NormalizeT_detector(T_detector);
    // debug
    OutputData(T_detector->data, T_detector->size[0] * T_detector->size[1]);

    int t_detect_win = floor(fs * 150 / 1000);
    
    assert(x_QRS->numDimensions == 2);

    int lqrs = max(x_QRS->size[0], x_QRS->size[1]);
    
    vector<double> T_position_pos, T_Location_cur, T_position_neg;

    vector<int> P_position_cur_tmp;
    //p_X_max=[];

    vector<double> P_Location_cur;
    
    int t_win_mf = mode(T_detector);

    for (int mm = 1; mm <= lqrs - 1; ++mm) {
        // debug
        
        // [Matlab]T_detector_win_ori = T_detector(x_QRS(mm) : x_QRS(mm+1));
        int x_QRS_left = x_QRS->data[mm - 1];
        int x_QRS_right = x_QRS->data[mm];
        // debug
        //cout << "x_QRS_left = "
             //<< x_QRS_left
             //<< ", x_QRS_right = "
             //<< x_QRS_right
             //<< endl;

        int segment_length = x_QRS_right - x_QRS_left + 1;
        unique_ptr<double[]> T_detector_win_ori(new double[segment_length]);
        copy_data(T_detector_win_ori.get(), 0,
                T_detector->data, x_QRS_left - 1, segment_length);
        
        // [Matlab] lttmp= length(T_detector_win_ori);
        int lttmp = segment_length;
        
        // debug 

        unique_ptr<double[]> Win_Gaussian(
                gaussian_function(lttmp, fs/5, min(fs/4, floor(lttmp/2.0)))) ;


        unique_ptr<double[]> T_detector_win(new double[segment_length]);
        for (int i = 0; i < segment_length; ++i) {
            T_detector_win[i] = T_detector_win_ori[i] * Win_Gaussian[i];
        }
        //if (debug) {
            //OutputData(Win_Gaussian.get(), segment_length);
            //return;
        //}

        double t_win_ave = mean(T_detector_win.get(), segment_length);
        
        // [Matlab] X_max = [];  Y_max = [];  X_min = [];  Y_min = [];
        vector<int> x_max_vector, x_min_vector;
        vector<double> y_max_vector, y_min_vector;

        // % Calculated the location of T
        if (lttmp > 2 * t_detect_win) {

            // debug
            //cout << "kk from "
                 //<< 1 + t_detect_win
                 //<< " to "
                 //<< lttmp - t_detect_win
                 //<< endl;

            for (int kk = 1 + t_detect_win; kk <= lttmp - t_detect_win; ++kk) {
                // debug
                //cout << "kk = " << kk << endl;

                int det_local_len = 2 * t_detect_win + 1;
                unique_ptr<double[]> t_det_local(new double[det_local_len]());
                copy_data(t_det_local.get(), 0,
                        T_detector_win.get(),
                        kk - t_detect_win - 1,
                        det_local_len);

                
                // [matlab] [y_max x_max] = max( t_det_local );
                int x_max = -1;
                double y_max = find_max_in_buffer(t_det_local.get(), det_local_len, x_max);
                int x_min = -1;
                double y_min = find_min_in_buffer(t_det_local.get(), det_local_len, x_min);
                
                double t_local_std = std_error(t_det_local.get(),
                        det_local_len) ;
                

                // debug
                //if (kk == 99) {
                    //OutputData(t_det_local.get(), det_local_len);
                    //cout << "x_min = " << x_min << endl;
                    //cout << "t_detect_win = " << t_detect_win << endl;
                    //cout << "y_min = " << y_min << endl;
                    //cout << "t_win_mf = " << t_win_mf << endl;
                    //return;
                //}

                if (x_max == t_detect_win + 1 && y_max > t_win_mf + eps) {
                    
                    x_max_vector.push_back(kk);
                    //X_max = [ X_max , kk ];
                    
                    y_max_vector.push_back(y_max);
                    //Y_max = [ Y_max , y_max ];
                }
                else if (x_min == t_detect_win + 1 && y_min + eps < -t_win_mf) {
                        
                    x_min_vector.push_back(kk);
                    //X_min = [ X_min , kk ];
                    
                    y_min_vector.push_back(y_max);
                    //Y_min = [ Y_min , y_max ];
                }
            }
        }

        //% Location of T with maximum x
        int x_T = 0;
        int max_T_count = 0;
        bool is_empty_x_t_p = true;
        bool is_empty_x_t_n = true;
        int x_t_p = -1;
        int x_t_n = -1;

        if (y_max_vector.empty() == false) {
            auto X_maxmax_iter = max_element(y_max_vector.begin(),
                    y_max_vector.end());
            int X_maxmax = X_maxmax_iter - y_max_vector.begin();
            //[Y_maxmax X_maxmax] = max(Y_max);
            x_t_p = x_max_vector[X_maxmax];
            is_empty_x_t_p = false;
            x_T = x_t_p;

            ++max_T_count;
        }
        
        //% Location of negtive T
        if (y_min_vector.empty() == false) {
            auto X_minmin_iter = min_element(y_min_vector.begin(),
                    y_min_vector.end());
            int X_minmin = X_minmin_iter - y_min_vector.begin();

            //[Y_minmin X_minmin] = min(Y_min);
            x_t_n = x_min_vector[X_minmin];

            is_empty_x_t_n = false;

            if (max_T_count == 0 || x_T < x_t_n) x_T = x_t_n;

            ++max_T_count;

        }
        

        int p_detect_win = floor(60.0 / 1000 * fs);

        // Default value when x_T is empty
        int p_detect_stat = lttmp - 5 * p_detect_win;
        // isempty(x_T)
        if (max_T_count == 0) {
            Win_Gaussian.reset(gaussian_function(
                    lttmp, fs/10, max(lttmp - fs/3.6, floor(2.0*lttmp/3))));
        } else {
            Win_Gaussian.reset(
                    gaussian_function(lttmp, fs/10,
                        x_T + floor((lttmp - x_T) / 2))) ;
            //% p_detect_stat：start of sliding P detecting window
            if (lttmp > 6 * p_detect_win) {
                p_detect_stat = lttmp - 5 * p_detect_win;
            } else {
                p_detect_stat = 0;
            }
        }

        // [Matlab] Win_Gaussian = gaussian_function( 1: lttmp,
        //      [fs/10 x_T+floor((lttmp-x_T)/2)]) ;
        
        unique_ptr<double[]> P_detector_win(new double[lttmp]());
        for (int i = 0; i < lttmp; ++i) {
            P_detector_win[i] = T_detector_win_ori[i] * Win_Gaussian[i];
        }
        
        // debug
        //OutputData(P_detector_win.get(), lttmp);
        //return;

        int p_detect_stop = lttmp - p_detect_win;

        //% Adjust of P wave detecting area according to the form of the next QRS
        //% T_detector_win(end) indicates wheahter the next R peak is positive or
        //% negtive

        if (T_detector_win[segment_length - 1] + eps < 0) {
            p_detect_stat = max( p_detect_stat - 4 * p_detect_win, 0) ;
            p_detect_stop = max( p_detect_stop - 2 * p_detect_win, 0) ;
        }
        
        //% P wave detection
        vector<int>p_X_max;

        if (p_detect_stop > p_detect_stat && p_detect_stat > 3 * p_detect_win) {
            
            for (int kk = p_detect_stat; kk <= p_detect_stop; ++kk) {
                
                // Find max& min values of p_det_local
                double y_max, y_min;
                int x_max = -1, x_min = -1;

                int p_det_local_len = 2 * p_detect_win + 1;
                unique_ptr<double[]> p_det_local(new double[p_det_local_len]());
                for (int i = 0; i < p_det_local_len; ++i) {
                    int p_detector_win_ind = i + kk - p_detect_win - 1;
                    p_det_local[i] = P_detector_win[p_detector_win_ind];
                    
                    // Find min& max values
                    double cur_val = p_det_local[i];
                    if (x_max == -1 || cur_val > y_max) {
                        x_max = i;
                        y_max = cur_val;
                    }
                    if (x_min == -1 || cur_val < y_min) {
                        y_min = cur_val;
                        x_min = i;
                    }
                }
                //p_det_local = P_detector_win(kk - p_detect_win : kk + p_detect_win);
                
                //[y_max x_max] = max(p_det_local );
                
                //[y_min x_min] = min(p_det_local );
                
                double t_local_std = std_error(p_det_local.get(), p_det_local_len);
                
                //if (kk == 237) {
                    //cout << "kk = " << kk << endl;
                    //cout << "x_max = " << x_max << endl;
                    //cout << "p_detect_win = " << p_detect_win
                         //<< endl;
                    //cout << "y_max = "
                         //<< y_max << endl;
                    //cout << "t_win_mf = " << t_win_mf << endl;
                    //return ;
                //}
                if (x_max  == p_detect_win + 1 &&
                        y_max > t_win_mf + eps) {
                    
                    p_X_max.push_back(kk);
                    
                    //p_Y_max = y_max ;
                }
            }
        }
        //else {
            //p_X_max=[];
        //}

        // debug

        if (p_X_max.empty() == false) {
            int p_X_max_len = p_X_max.size();
            int cur_p_position = x_QRS->data[mm - 1] + p_X_max[p_X_max_len - 1];

            P_position_cur_tmp.push_back(
                               x_QRS->data[mm - 1] + p_X_max[p_X_max_len - 1]);
            
            // NOTE: This vector contains C indexes
            P_Location_cur.push_back(cur_p_position + x_start);
        }

        if (is_empty_x_t_p == false) {
            
            //T_position_pos = [ T_position_pos x_QRS(mm) + x_t_p ];
            int cur_tp_position = x_QRS->data[mm - 1] + x_t_p;
            T_position_pos.push_back(cur_tp_position);
            
            // NOTE: This vector contains C indexes
            T_Location_cur.push_back(cur_tp_position + x_start - 1);
            
            if (is_empty_x_t_p == false && x_t_p + eps < -0.7 * x_t_n) {
                
                int cur_tn_position = x_QRS->data[mm - 1] + x_t_n;
                T_position_neg.push_back(cur_tn_position);
                //T_position_neg = [T_position_neg x_QRS(mm) + x_t_n ];
                
            }
        }
        else {
            
            if (false == is_empty_x_t_n) {
                
                int cur_tn_position = x_QRS->data[mm - 1] + x_t_n;
                T_position_neg.push_back(cur_tn_position);
                //T_position_neg =[ T_position_neg x_QRS(mm) + x_t_n ];
                
                // NOTE: This vector contains C indexes
                T_Location_cur.push_back(cur_tn_position + x_start - 1);
                
            }
        }

    } // end of for loop: mm

    // Output to struct
    
    T_Location_cur_out->size[0] = T_Location_cur.size();
    T_Location_cur_out->size[1] = 1;
    emxEnsureCapacity((emxArray__common *)T_Location_cur_out, 0,
            (int)sizeof(double));
    int t_ind = 0;
    for (const auto& t_pos: T_Location_cur) {
        T_Location_cur_out->data[t_ind++] = t_pos;
    }

    P_Location_cur_out->size[0] = P_Location_cur.size();
    P_Location_cur_out->size[1] = 1;
    emxEnsureCapacity((emxArray__common *)P_Location_cur_out, 0,
            (int)sizeof(double));
    int p_ind = 0;
    for (const auto& p_pos: P_Location_cur) {
        P_Location_cur_out->data[p_ind++] = p_pos; 
    }


    //cout << "=====Statistics of my TP function=====" << endl;
    //cout << "size of T results: "
         //<< T_Location_cur.size() 
         //<< endl;
    //cout << "size of P results: "
         //<< P_Location_cur.size()
         //<< endl;

    return;
}

// vector version of T_detection.
void T_detection(emxArray_real_T *T_detector, double fs, const vector<int>& x_qrs_vec,
                 double x_start, emxArray_real_T *T_Location_cur_out,
                 emxArray_real_T *P_Location_cur_out)
{
    NormalizeT_detector(T_detector);
    // debug
    OutputData(T_detector->data, T_detector->size[0] * T_detector->size[1]);

    int t_detect_win = floor(fs * 150 / 1000);
    

    int lqrs = x_qrs_vec.size();
    
    vector<double> T_position_pos, T_Location_cur, T_position_neg;

    vector<int> P_position_cur_tmp;
    //p_X_max=[];

    vector<double> P_Location_cur;
    
    int t_win_mf = mode(T_detector);

    for (int mm = 1; mm <= lqrs - 1; ++mm) {
        // debug
        
        // [Matlab]T_detector_win_ori = T_detector(x_QRS(mm) : x_QRS(mm+1));
        //int x_QRS_left = x_QRS->data[mm - 1];
        //int x_QRS_right = x_QRS->data[mm];
        int x_QRS_left = x_qrs_vec[mm - 1];
        int x_QRS_right = x_qrs_vec[mm];

        int segment_length = x_QRS_right - x_QRS_left + 1;
        unique_ptr<double[]> T_detector_win_ori(new double[segment_length]);
        copy_data(T_detector_win_ori.get(), 0,
                T_detector->data, x_QRS_left - 1, segment_length);
        
        // [Matlab] lttmp= length(T_detector_win_ori);
        int lttmp = segment_length;
        
        // debug 

        unique_ptr<double[]> Win_Gaussian(
                gaussian_function(lttmp, fs/5, min(fs/4, floor(lttmp/2.0)))) ;


        unique_ptr<double[]> T_detector_win(new double[segment_length]);
        for (int i = 0; i < segment_length; ++i) {
            T_detector_win[i] = T_detector_win_ori[i] * Win_Gaussian[i];
        }
        //if (debug) {
            //OutputData(Win_Gaussian.get(), segment_length);
            //return;
        //}

        double t_win_ave = mean(T_detector_win.get(), segment_length);
        
        // [Matlab] X_max = [];  Y_max = [];  X_min = [];  Y_min = [];
        vector<int> x_max_vector, x_min_vector;
        vector<double> y_max_vector, y_min_vector;

        // % Calculated the location of T
        if (lttmp > 2 * t_detect_win) {

            // debug
            //cout << "kk from "
                 //<< 1 + t_detect_win
                 //<< " to "
                 //<< lttmp - t_detect_win
                 //<< endl;

            for (int kk = 1 + t_detect_win; kk <= lttmp - t_detect_win; ++kk) {
                // debug
                //cout << "kk = " << kk << endl;

                int det_local_len = 2 * t_detect_win + 1;
                unique_ptr<double[]> t_det_local(new double[det_local_len]());
                copy_data(t_det_local.get(), 0,
                        T_detector_win.get(),
                        kk - t_detect_win - 1,
                        det_local_len);

                
                // [matlab] [y_max x_max] = max( t_det_local );
                int x_max = -1;
                double y_max = find_max_in_buffer(t_det_local.get(), det_local_len, x_max);
                int x_min = -1;
                double y_min = find_min_in_buffer(t_det_local.get(), det_local_len, x_min);
                
                double t_local_std = std_error(t_det_local.get(),
                        det_local_len) ;
                

                // debug
                //if (kk == 99) {
                    //OutputData(t_det_local.get(), det_local_len);
                    //cout << "x_min = " << x_min << endl;
                    //cout << "t_detect_win = " << t_detect_win << endl;
                    //cout << "y_min = " << y_min << endl;
                    //cout << "t_win_mf = " << t_win_mf << endl;
                    //return;
                //}

                if (x_max == t_detect_win + 1 && y_max > t_win_mf + eps) {
                    
                    x_max_vector.push_back(kk);
                    //X_max = [ X_max , kk ];
                    
                    y_max_vector.push_back(y_max);
                    //Y_max = [ Y_max , y_max ];
                }
                else if (x_min == t_detect_win + 1 && y_min + eps < -t_win_mf) {
                        
                    x_min_vector.push_back(kk);
                    //X_min = [ X_min , kk ];
                    
                    y_min_vector.push_back(y_max);
                    //Y_min = [ Y_min , y_max ];
                }
            }
        }

        //% Location of T with maximum x
        int x_T = 0;
        int max_T_count = 0;
        bool is_empty_x_t_p = true;
        bool is_empty_x_t_n = true;
        int x_t_p = -1;
        int x_t_n = -1;

        if (y_max_vector.empty() == false) {
            auto X_maxmax_iter = max_element(y_max_vector.begin(),
                    y_max_vector.end());
            int X_maxmax = X_maxmax_iter - y_max_vector.begin();
            //[Y_maxmax X_maxmax] = max(Y_max);
            x_t_p = x_max_vector[X_maxmax];
            is_empty_x_t_p = false;
            x_T = x_t_p;

            ++max_T_count;
        }
        
        //% Location of negtive T
        if (y_min_vector.empty() == false) {
            auto X_minmin_iter = min_element(y_min_vector.begin(),
                    y_min_vector.end());
            int X_minmin = X_minmin_iter - y_min_vector.begin();

            //[Y_minmin X_minmin] = min(Y_min);
            x_t_n = x_min_vector[X_minmin];

            is_empty_x_t_n = false;

            if (max_T_count == 0 || x_T < x_t_n) x_T = x_t_n;

            ++max_T_count;

        }
        

        int p_detect_win = floor(60.0 / 1000 * fs);

        // Default value when x_T is empty
        int p_detect_stat = lttmp - 5 * p_detect_win;
        // isempty(x_T)
        if (max_T_count == 0) {
            Win_Gaussian.reset(gaussian_function(
                    lttmp, fs/10, max(lttmp - fs/3.6, floor(2.0*lttmp/3))));
        } else {
            Win_Gaussian.reset(
                    gaussian_function(lttmp, fs/10,
                        x_T + floor((lttmp - x_T) / 2))) ;
            //% p_detect_stat：start of sliding P detecting window
            if (lttmp > 6 * p_detect_win) {
                p_detect_stat = lttmp - 5 * p_detect_win;
            } else {
                p_detect_stat = 0;
            }
        }

        // [Matlab] Win_Gaussian = gaussian_function( 1: lttmp,
        //      [fs/10 x_T+floor((lttmp-x_T)/2)]) ;
        
        unique_ptr<double[]> P_detector_win(new double[lttmp]());
        for (int i = 0; i < lttmp; ++i) {
            P_detector_win[i] = T_detector_win_ori[i] * Win_Gaussian[i];
        }
        
        // debug
        //OutputData(P_detector_win.get(), lttmp);
        //return;

        int p_detect_stop = lttmp - p_detect_win;

        //% Adjust of P wave detecting area according to the form of the next QRS
        //% T_detector_win(end) indicates wheahter the next R peak is positive or
        //% negtive

        if (T_detector_win[segment_length - 1] + eps < 0) {
            p_detect_stat = max( p_detect_stat - 4 * p_detect_win, 0) ;
            p_detect_stop = max( p_detect_stop - 2 * p_detect_win, 0) ;
        }
        
        //% P wave detection
        vector<int>p_X_max;

        if (p_detect_stop > p_detect_stat && p_detect_stat > 3 * p_detect_win) {
            
            for (int kk = p_detect_stat; kk <= p_detect_stop; ++kk) {
                
                // Find max& min values of p_det_local
                double y_max, y_min;
                int x_max = -1, x_min = -1;

                int p_det_local_len = 2 * p_detect_win + 1;
                unique_ptr<double[]> p_det_local(new double[p_det_local_len]());
                for (int i = 0; i < p_det_local_len; ++i) {
                    int p_detector_win_ind = i + kk - p_detect_win - 1;
                    p_det_local[i] = P_detector_win[p_detector_win_ind];
                    
                    // Find min& max values
                    double cur_val = p_det_local[i];
                    if (x_max == -1 || cur_val > y_max) {
                        x_max = i;
                        y_max = cur_val;
                    }
                    if (x_min == -1 || cur_val < y_min) {
                        y_min = cur_val;
                        x_min = i;
                    }
                }
                //p_det_local = P_detector_win(kk - p_detect_win : kk + p_detect_win);
                
                //[y_max x_max] = max(p_det_local );
                
                //[y_min x_min] = min(p_det_local );
                
                double t_local_std = std_error(p_det_local.get(), p_det_local_len);
                
                //if (kk == 237) {
                    //cout << "kk = " << kk << endl;
                    //cout << "x_max = " << x_max << endl;
                    //cout << "p_detect_win = " << p_detect_win
                         //<< endl;
                    //cout << "y_max = "
                         //<< y_max << endl;
                    //cout << "t_win_mf = " << t_win_mf << endl;
                    //return ;
                //}
                if (x_max  == p_detect_win + 1 &&
                        y_max > t_win_mf + eps) {
                    
                    p_X_max.push_back(kk);
                    
                    //p_Y_max = y_max ;
                }
            }
        }
        //else {
            //p_X_max=[];
        //}

        // debug

        if (p_X_max.empty() == false) {
            int p_X_max_len = p_X_max.size();
            int cur_p_position = x_qrs_vec[mm - 1] + p_X_max[p_X_max_len - 1];

            P_position_cur_tmp.push_back(
                               x_qrs_vec[mm - 1] + p_X_max[p_X_max_len - 1]);
            
            // NOTE: This vector contains C indexes
            P_Location_cur.push_back(cur_p_position + x_start);
        }

        if (is_empty_x_t_p == false) {
            
            //T_position_pos = [ T_position_pos x_QRS(mm) + x_t_p ];
            int cur_tp_position = x_qrs_vec[mm - 1] + x_t_p;
            T_position_pos.push_back(cur_tp_position);
            
            // NOTE: This vector contains C indexes
            T_Location_cur.push_back(cur_tp_position + x_start - 1);
            
            if (is_empty_x_t_p == false && x_t_p + eps < -0.7 * x_t_n) {
                
                int cur_tn_position = x_qrs_vec[mm - 1] + x_t_n;
                T_position_neg.push_back(cur_tn_position);
                //T_position_neg = [T_position_neg x_QRS(mm) + x_t_n ];
                
            }
        }
        else {
            
            if (false == is_empty_x_t_n) {
                
                int cur_tn_position = x_qrs_vec[mm - 1] + x_t_n;
                T_position_neg.push_back(cur_tn_position);
                //T_position_neg =[ T_position_neg x_QRS(mm) + x_t_n ];
                
                // NOTE: This vector contains C indexes
                T_Location_cur.push_back(cur_tn_position + x_start - 1);
                
            }
        }

    } // end of for loop: mm

    // Output to struct
    
    T_Location_cur_out->size[0] = T_Location_cur.size();
    T_Location_cur_out->size[1] = 1;
    emxEnsureCapacity((emxArray__common *)T_Location_cur_out, 0,
            (int)sizeof(double));
    int t_ind = 0;
    for (const auto& t_pos: T_Location_cur) {
        T_Location_cur_out->data[t_ind++] = t_pos;
    }

    P_Location_cur_out->size[0] = P_Location_cur.size();
    P_Location_cur_out->size[1] = 1;
    emxEnsureCapacity((emxArray__common *)P_Location_cur_out, 0,
            (int)sizeof(double));
    int p_ind = 0;
    for (const auto& p_pos: P_Location_cur) {
        P_Location_cur_out->data[p_ind++] = p_pos; 
    }

    return;
}
/*
 * File trailer for T_detection.c
 *
 * [EOF]
 */

// BucketThreshold: avoid overflow
void NormalizeT_detector(emxArray_real_T *T_detector,
        double BucketThreshold) {
    
    //cout << "T_detector size[0] = " << T_detector->size[0] << endl;
    //cout << "T_detector size[1] = " << T_detector->size[1] << endl;

    assert(T_detector->numDimensions == 2);
    int T_len = max(T_detector->size[0], T_detector->size[1]);
    if (T_len == 0) return;
    
    // mean(T_detector.^2)
    double mean_T_detector = 0;
    double sum_val = 0;
    
    for (int i = 0; i < T_len; ++i) {
        double val = T_detector->data[i];
        val *= val;

        if (val > BucketThreshold || sum_val > BucketThreshold) {
            mean_T_detector += sum_val / T_len;
            sum_val = 0;
        }
        
        sum_val += val;
    }

    if (abs(sum_val) > eps) mean_T_detector += sum_val / T_len;
    
    double base_val = sqrt(mean_T_detector);
    
    if (abs(base_val) < eps) return;
    
    for (int i = 0; i < T_len; ++i) {
        double &val = T_detector->data[i];

        val = 100.0 * val / base_val;
    }
    
    return;
}

// Find most frequent element.
// IF multiple values are found, return the smallest value.
int mode(emxArray_real_T *T_detector) {

    assert(T_detector->numDimensions == 2);
    int T_len = max(T_detector->size[0], T_detector->size[1]);
    if (T_len == 0) return 0;
    
    // mean(T_detector.^2)
    int most_frequent_val = 0;
    int most_frequency = 0;

    unordered_map<int, int> hash_count;

    for (int i = 0; i < T_len; ++i) {
        int val = floor(T_detector->data[i]);
        
        if (hash_count.count(val) == 0) hash_count[val] = 0;
        ++hash_count[val]; 

        int cur_freq = hash_count[val];
        if (cur_freq > most_frequency ||
                (cur_freq == most_frequency && val < most_frequent_val)) {
                most_frequent_val = val;
                most_frequency = cur_freq;
        }
    }
    return most_frequent_val;
}

// Caller MUST guarentee there's enough space in each array.
void copy_data(double* to_buffer, int to_start,
    double* from_buffer, int from_start, int buffer_len) {

    for (int i = 0; i < buffer_len; ++i) {
        int to_ind = i + to_start;
        int from_ind = i + from_start;
        to_buffer[to_ind] = from_buffer[from_ind];
    }
}

// Return gaussian array based on 1:lttmp
double *gaussian_function(int lttmp, double g_std, double g_mean) {
    //cout << "Gaussian:" << endl;
    //cout << "g_mean :" << g_mean << endl;
    //cout << "g_std: " << g_std << endl;

    int buffer_len = lttmp;
    double *g_buffer = new double[buffer_len]();

    if (abs(g_std) < eps) {
        cout << "Warning: std value equal to zero!" << endl;
        return g_buffer;
    }

    for (int i = 1; i <= lttmp; ++i) {
        double val = i;
        double y = pow(math_e, -(val - g_mean) * (val - g_mean) /
                (2 * g_std * g_std));
        g_buffer[i - 1] = y;
    }
    return g_buffer;
}

double mean(double* buffer, int buffer_length) {
    double BucketThreshold = 2147483647.0;

    int T_len = buffer_length;
    double mean_T_detector = 0;
    double sum_val = 0;
    
    for (int i = 0; i < T_len; ++i) {
        double val = buffer[i];

        if (val > BucketThreshold || sum_val > BucketThreshold) {
            mean_T_detector += sum_val / T_len;
            sum_val = 0;
        }
        sum_val += val;
    }

    if (abs(sum_val) > eps) mean_T_detector += sum_val / T_len;
    return mean_T_detector;
}

double find_max_in_buffer(double* buffer, int buffer_length, int& max_ind) {
    assert(buffer_length > 0);
    double max_val = buffer[0];
    max_ind = 0;
    for (int i = 1; i < buffer_length; ++i) {
        double val = buffer[i];
        if (val - eps > max_val) {
            max_val = val;
            max_ind = i;
        }
    }

    // Matlab index
    max_ind++;

    return max_val;
}

double find_min_in_buffer(double* buffer, int buffer_length, int& min_ind) {
    assert(buffer_length > 0);
    double min_val = buffer[0];
    min_ind = 0;
    for (int i = 1; i < buffer_length; ++i) {
        double val = buffer[i];
        if (val  + eps < min_val) {
            min_val = val;
            min_ind = i;
        }
    }

    // Matlab index
    min_ind++;

    return min_val;
}

double std_error(double* buffer, int buffer_length) {
    double mean_val = mean(buffer, buffer_length);
    
    double cur_sum = 0;
    double cur_mean_square = 0;

    for (int i = 0; i < buffer_length; ++i) {
        double val = (buffer[i] - mean_val) * (buffer[i] - mean_val);
        if (val > k_BucketThreshold - eps ||
                cur_sum > k_BucketThreshold - eps) {
            cur_mean_square += cur_sum / buffer_length;
            cur_sum = 0;
        }
        cur_sum += val;
    }
    if (abs(cur_sum) > eps) cur_mean_square += cur_sum / buffer_length;
    
    return sqrt(cur_mean_square);
}
