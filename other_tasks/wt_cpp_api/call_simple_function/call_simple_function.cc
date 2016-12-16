/*
 * File: call_simple_function.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "call_simple_function_emxutil.h"
#include "T_detection.h"
#include "QRS_detection.h"
#include "sum.h"
#include "abs.h"

#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <utility>

using namespace std;

#define eps 1e-6


static double abs_double(double val) {
    return val < -eps ? -val: val;
}

static void ShowData(emxArray_real_T* result, string name = "data") {
    cout << name + "->size = "
         << result->allocatedSize
         << endl;

    for (int i = 0; i < result->allocatedSize; ++i) {
        cout << "val = "
             << result->data[i]
             << endl;
    }
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

// Get T_detector from 10 levels of s_rec
static void GetT_detector10(const double *s_rec, int, int,
          double fs, emxArray_real_T *T_detector);

// Remove repeated results
static void RemoveRepeatResults(vector<pair<char, int>>* detection_results,
        int Min_Label_Distance = 10);

/* Function Definitions */

/*
 * Arguments    : const double *s_rec
 *                double sig_len
 *                double fs
 *                emxArray_real_T *y_out
 * Return Type  : void
 */
void call_simple_function(const double *s_rec, double sig_len, double fs,
  vector<pair<char, int>>* result_out) {

  emxArray_real_T *QRS_Location;
  emxArray_real_T *T_Location_raw;
  emxArray_real_T *P_Location_raw;
  double L_sig;
  double L_overlap;
  int i0;
  int jj;
  emxArray_real_T *QRS_detector;
  emxArray_real_T *T_detector;
  emxArray_real_T *x_QRS;
  emxArray_real_T *T_Location_cur;
  emxArray_real_T *P_Location_cur;
  emxArray_real_T *r0;
  emxArray_real_T *b_QRS_detector;
  emxArray_real_T *b_s_rec;
  emxArray_real_T *c_s_rec;
  emxArray_real_T *c_QRS_detector;
  emxArray_real_T *b_T_Location_cur;
  emxArray_real_T *b_T_Location_raw;
  emxArray_real_T *b_P_Location_raw;
  emxArray_real_T *c_T_Location_raw;
  emxArray_real_T *c_P_Location_raw;
  double x_start;
  double x_stop;
  int i1;
  int iy;
  int loop_ub;
  int ixstart;
  int sz[2];
  int ix;
  emxInit_real_T(&QRS_Location, 2);
  emxInit_real_T(&T_Location_raw, 2);
  emxInit_real_T(&P_Location_raw, 2);

  /* % Call simple function to make its parameters variable-sized. */
  L_sig = floor((sig_len - 2.0 * fs) / (fs * 10.0));

  /* % Test QRS & P & T wave */
  /* L_sig = floor((length(data_raw)-fs)/(fs*10));  */
  /* return; */
  /* end */
  /* % Reconstruct s_rec from s_rec_struct */
  /* s_rec = zeros(length(s_rec_struct(1).coef), length(s_rec_struct)) */
  /* for ind = 1:length(s_rec_struct) */
  /* s_rec(:,ind) = s_rec_struct(ind).coef; */
  /* end */
  /* % ========================================= */
  L_overlap = 2.0 * fs;
  i0 = QRS_Location->size[0] * QRS_Location->size[1];
  QRS_Location->size[0] = 1;
  QRS_Location->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)QRS_Location, i0, (int)sizeof(double));
  i0 = T_Location_raw->size[0] * T_Location_raw->size[1];
  T_Location_raw->size[0] = 0;
  T_Location_raw->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)T_Location_raw, i0, (int)sizeof(double));
  i0 = P_Location_raw->size[0] * P_Location_raw->size[1];
  P_Location_raw->size[0] = 0;
  P_Location_raw->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)P_Location_raw, i0, (int)sizeof(double));

  /*  Output list */
  emxInit_real_T(&QRS_detector, 2);
  emxInit_real_T(&T_detector, 2);
  emxInit_real_T(&x_QRS, 2);
  emxInit_real_T(&T_Location_cur, 2);
  emxInit_real_T(&P_Location_cur, 2);
  emxInit_real_T(&r0, 2);
  emxInit_real_T(&b_QRS_detector, 2);
  emxInit_real_T(&b_s_rec, 2);
  emxInit_real_T(&c_s_rec, 2);
  emxInit_real_T(&c_QRS_detector, 2);
  emxInit_real_T(&b_T_Location_cur, 2);
  emxInit_real_T(&b_T_Location_raw, 2);
  emxInit_real_T(&b_P_Location_raw, 2);
  emxInit_real_T(&c_T_Location_raw, 2);
  emxInit_real_T(&c_P_Location_raw, 2);


  jj = 0;
  // jj from 0 to L_sig - 1
  while (jj <= (int)L_sig - 1) {
    x_start = 1.0 + ((1.0 + (double)jj) - 1.0) * fs * 10.0;
    x_stop = (((1.0 + (double)jj) - 1.0) * fs * 10.0 + fs * 10.0) + L_overlap;

    /*  ECG with wavelet sub-levels 1 to 8, is equal to high pass filter */
    /*  QRS_detector is used to detect qrs complex, whose energy is */
    /*  concentrate at 10 - 50 Hz */
    if (x_start > x_stop) {
      i0 = 0;
      i1 = 0;
    } else {
      i0 = (int)x_start - 1;
      i1 = (int)x_stop;
    }

    iy = b_s_rec->size[0] * b_s_rec->size[1];
    b_s_rec->size[0] = 3;
    b_s_rec->size[1] = i1 - i0;
    emxEnsureCapacity((emxArray__common *)b_s_rec, iy, (int)sizeof(double));
    loop_ub = i1 - i0;
    for (i1 = 0; i1 < loop_ub; i1++) {
      for (iy = 0; iy < 3; iy++) {
        b_s_rec->data[iy + b_s_rec->size[0] * i1] = s_rec[(iy + 10 * (i0 + i1))
          + 2];
      }
    }

    b_abs(b_s_rec, r0);
    sum(r0, QRS_detector);

    /*  QRS_detector is used to detect T and P wave, whose energy is */
    /*  concentrate at 1 - 10 Hz */
    if (x_start > x_stop) {
      i0 = 1;
      i1 = 1;
    } else {
      i0 = (int)x_start;
      i1 = (int)x_stop + 1;
    }

    iy = c_s_rec->size[0] * c_s_rec->size[1];
    c_s_rec->size[0] = 5;
    c_s_rec->size[1] = i1 - i0;
    emxEnsureCapacity((emxArray__common *)c_s_rec, iy, (int)sizeof(double));
    loop_ub = i1 - i0;
    for (iy = 0; iy < loop_ub; iy++) {
      for (ixstart = 0; ixstart < 5; ixstart++) {
        c_s_rec->data[ixstart + c_s_rec->size[0] * iy] = s_rec[(ixstart + 10 *
          ((i0 + iy) - 1)) + 3];
      }
    }

    for (iy = 0; iy < 2; iy++) {
      sz[iy] = c_s_rec->size[iy];
    }

    iy = T_detector->size[0] * T_detector->size[1];
    T_detector->size[0] = 1;
    T_detector->size[1] = sz[1];
    emxEnsureCapacity((emxArray__common *)T_detector, iy, (int)sizeof(double));
    
    GetT_detector10(s_rec, x_start, x_stop, fs, T_detector);

    /*   QRS complex detection algorithm */
    // Backup QRS_detector
    i0 = b_QRS_detector->size[0] * b_QRS_detector->size[1];
    b_QRS_detector->size[0] = 1;
    b_QRS_detector->size[1] = QRS_detector->size[1];
    emxEnsureCapacity((emxArray__common *)b_QRS_detector, i0, (int)sizeof(double));
    loop_ub = QRS_detector->size[0] * QRS_detector->size[1];

    vector<double> qrs_detector_vec;
    for (i0 = 0; i0 < loop_ub; i0++) {
      b_QRS_detector->data[i0] = QRS_detector->data[i0];
      qrs_detector_vec.push_back(QRS_detector->data[i0]);
    }
    

    // OUtput
    //QRS_detection(b_QRS_detector, fs, QRS_detector, x_QRS);
    vector<double> x_qrs_vec;
    QRS_detection(qrs_detector_vec, fs, &x_qrs_vec);
    //vector<double> qrs_detector_vec;
    //for (int i = 0; i < x_QRS->size[0] * x_QRS->size[1]; ++i) {
      //qrs_detector_vec.push_back(x_QRS->data[i]);
    //}
    //OutputCoefToFile("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/c_output/result.dat", x_qrs_vec);

    for (auto& val: x_qrs_vec) {
        result_out->emplace_back('R', val + x_start);
    }
    // Add to output vector.
    //auto QRS_cap = x_QRS->size[0] * x_QRS->size[1];
    //for (int i = 0; i < QRS_cap; ++i) {
        //int val = x_QRS->data[i];
        //if (val <= 0) break;
        //result_out->push_back(make_pair('R', val + x_start));
    //}


    /*  QRS_Location_cur contains all QRS locations detected this 12s' window */
    //i0 = QRS_detector->size[0] * QRS_detector->size[1];
    //QRS_detector->size[0] = 1;
    //QRS_detector->size[1] = x_QRS->size[1];
    //emxEnsureCapacity((emxArray__common *)QRS_detector, i0, (int)sizeof(double));
    //loop_ub = x_QRS->size[0] * x_QRS->size[1];
    //for (i0 = 0; i0 < loop_ub; i0++) {
      //QRS_detector->data[i0] = x_QRS->data[i0] + x_start;
    //}

    /*   T and P wave detection        */
    T_detection(T_detector, fs, x_QRS, x_start, T_Location_cur, P_Location_cur);

    // Add to output vector.
    //auto T_cap = T_Location_cur->allocatedSize;
    //for (int i = 0; i < QRS_cap; ++i) {
        //int val = T_Location_cur->data[i];
        //if (val <= 0) break;
        //result_out->push_back(make_pair('T', val + x_start));
    //}

    //ShowData(T_Location_cur, "T_Location_cur");
    //ShowData(P_Location_cur, "P_Location_cur");
    /*  This part is gona to detect the repetitive detection in 2s' */
    /*  overlap between two adjacent windows */

    // Save Outputs
    for (int i = 0; i < T_Location_cur->size[0] * T_Location_cur->size[1];
            ++i) {
        int val = T_Location_cur->data[i];
        if (val <= 0) break;
        result_out->push_back(make_pair('T', val));
    }
    for (int i = 0; i < P_Location_cur->size[0] * P_Location_cur->size[1];
            ++i) {
        int val = P_Location_cur->data[i];
        if (val <= 0) break;
        result_out->push_back(make_pair('P', val));
    }

    //cout << "jj = " << jj << endl;
    jj++;
  }

  // ===============================================
  // Calculate the tail part if len_signal > fs * 12
  // ===============================================
  if (sig_len > static_cast<int>(fs) * 12) {
      
        x_start = sig_len - static_cast<int>(fs) * 12;
        x_stop = sig_len;

        /*  ECG with wavelet sub-levels 1 to 8, is equal to high pass filter */
        /*  QRS_detector is used to detect qrs complex, whose energy is */
        /*  concentrate at 10 - 50 Hz */
        if (x_start > x_stop) {
          i0 = 0;
          i1 = 0;
        } else {
          i0 = (int)x_start - 1;
          i1 = (int)x_stop;
        }

        iy = b_s_rec->size[0] * b_s_rec->size[1];
        b_s_rec->size[0] = 3;
        b_s_rec->size[1] = i1 - i0;
        emxEnsureCapacity((emxArray__common *)b_s_rec, iy, (int)sizeof(double));
        loop_ub = i1 - i0;
        for (i1 = 0; i1 < loop_ub; i1++) {
          for (iy = 0; iy < 3; iy++) {
            b_s_rec->data[iy + b_s_rec->size[0] * i1] = s_rec[(iy + 10 * (i0 + i1))
              + 2];
          }
        }

        b_abs(b_s_rec, r0);
        sum(r0, QRS_detector);

        /*  QRS_detector is used to detect T and P wave, whose energy is */
        /*  concentrate at 1 - 10 Hz */
        if (x_start > x_stop) {
          i0 = 1;
          i1 = 1;
        } else {
          i0 = (int)x_start;
          i1 = (int)x_stop + 1;
        }

        iy = c_s_rec->size[0] * c_s_rec->size[1];
        c_s_rec->size[0] = 5;
        c_s_rec->size[1] = i1 - i0;
        emxEnsureCapacity((emxArray__common *)c_s_rec, iy, (int)sizeof(double));
        loop_ub = i1 - i0;
        for (iy = 0; iy < loop_ub; iy++) {
          for (ixstart = 0; ixstart < 5; ixstart++) {
            c_s_rec->data[ixstart + c_s_rec->size[0] * iy] = s_rec[(ixstart + 10 *
              ((i0 + iy) - 1)) + 3];
          }
        }

        for (iy = 0; iy < 2; iy++) {
          sz[iy] = c_s_rec->size[iy];
        }

        iy = T_detector->size[0] * T_detector->size[1];
        T_detector->size[0] = 1;
        T_detector->size[1] = sz[1];
        emxEnsureCapacity((emxArray__common *)T_detector, iy, (int)sizeof(double));
        
        GetT_detector10(s_rec, x_start, x_stop, fs, T_detector);

        /*   QRS complex detection algorithm */
        i0 = b_QRS_detector->size[0] * b_QRS_detector->size[1];
        b_QRS_detector->size[0] = 1;
        b_QRS_detector->size[1] = QRS_detector->size[1];
        emxEnsureCapacity((emxArray__common *)b_QRS_detector, i0, (int)sizeof(double));
        loop_ub = QRS_detector->size[0] * QRS_detector->size[1];

        vector<double> qrs_detector_vec;
        for (i0 = 0; i0 < loop_ub; i0++) {
          b_QRS_detector->data[i0] = QRS_detector->data[i0];
          qrs_detector_vec.push_back(QRS_detector->data[i0]);
        }
        

        // OUtput
        //QRS_detection(b_QRS_detector, fs, QRS_detector, x_QRS);
        vector<double> x_qrs_vec;
        QRS_detection(qrs_detector_vec, fs, &x_qrs_vec);
        //vector<double> qrs_detector_vec;
        //for (int i = 0; i < x_QRS->size[0] * x_QRS->size[1]; ++i) {
          //qrs_detector_vec.push_back(x_QRS->data[i]);
        //}
        //OutputCoefToFile("/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/c_output/result.dat", x_qrs_vec);

        for (auto& val: x_qrs_vec) {
            result_out->emplace_back('R', val + x_start);
        }
        // Add to output vector.
        //auto QRS_cap = x_QRS->size[0] * x_QRS->size[1];
        //for (int i = 0; i < QRS_cap; ++i) {
            //int val = x_QRS->data[i];
            //if (val <= 0) break;
            //result_out->push_back(make_pair('R', val + x_start));
        //}

        /*  QRS_Location_cur contains all QRS locations detected this 12s' window */
        //i0 = QRS_detector->size[0] * QRS_detector->size[1];
        //QRS_detector->size[0] = 1;
        //QRS_detector->size[1] = x_QRS->size[1];
        //emxEnsureCapacity((emxArray__common *)QRS_detector, i0, (int)sizeof(double));
        //loop_ub = x_QRS->size[0] * x_QRS->size[1];
        //for (i0 = 0; i0 < loop_ub; i0++) {
          //QRS_detector->data[i0] = x_QRS->data[i0] + x_start;
        //}

        /*   T and P wave detection        */
        T_detection(T_detector, fs, x_QRS, x_start, T_Location_cur, P_Location_cur);

        // Save Outputs
        for (int i = 0; i < T_Location_cur->size[0] * T_Location_cur->size[1];
                ++i) {
            int val = T_Location_cur->data[i];
            if (val <= 0) break;
            result_out->push_back(make_pair('T', val));
        }
        for (int i = 0; i < P_Location_cur->size[0] * P_Location_cur->size[1];
                ++i) {
            int val = P_Location_cur->data[i];
            if (val <= 0) break;
            result_out->push_back(make_pair('P', val));
        }
  }


  emxFree_real_T(&c_P_Location_raw);
  emxFree_real_T(&c_T_Location_raw);
  emxFree_real_T(&b_P_Location_raw);
  emxFree_real_T(&b_T_Location_raw);
  emxFree_real_T(&b_T_Location_cur);
  emxFree_real_T(&c_QRS_detector);
  emxFree_real_T(&c_s_rec);
  emxFree_real_T(&b_s_rec);
  emxFree_real_T(&b_QRS_detector);
  emxFree_real_T(&r0);
  emxFree_real_T(&P_Location_cur);
  emxFree_real_T(&T_Location_cur);
  emxFree_real_T(&x_QRS);
  emxFree_real_T(&T_detector);
  emxFree_real_T(&QRS_detector);

  /*  Re-formatting the position lists into structures for c++ codegen. */


  emxFree_real_T(&P_Location_raw);
  emxFree_real_T(&T_Location_raw);
  emxFree_real_T(&QRS_Location);
  // Eliminate repeated results
  RemoveRepeatResults(result_out);
}

// Get T_detector from 10 levels of s_rec
void GetT_detector10(const double *s_rec, int x_start_matlab,
          int x_stop_matlab, double fs,
          emxArray_real_T *T_detector) {

    double L_overlap = 2.0 * fs;

    int x_start = x_start_matlab - 1;
    int x_stop = x_stop_matlab - 1;
    //int x_start = round(1.0+(jj_matlab -1)*fs*10) - 1;
    //int x_stop = round((jj_matlab -1.0)*fs*10 + fs*10 + L_overlap) - 1;

    T_detector->size[1] = x_stop - x_start + 1;
    T_detector->size[0] = 1;
    emxEnsureCapacity((emxArray__common *)T_detector, 0, (int)sizeof(double));

    // Add levels 4:8(matlab indexes)
    int data_count = 0;
    for (int i = x_start; i <= x_stop; ++i) {
        int index_base = i * 10;
        T_detector->data[data_count] = s_rec[3 + index_base];
        T_detector->data[data_count] += s_rec[4 + index_base];
        T_detector->data[data_count] += s_rec[5 + index_base];
        T_detector->data[data_count] += s_rec[6 + index_base];
        T_detector->data[data_count] += s_rec[7 + index_base];

        data_count++;
    }
    return;
}

// Compare results according to label.
static bool label_compare(pair<char,int>& a, pair<char,int>& b) {
    return a.first < b.first;
}

// Remove repeated results.
// MinDistance: The minimum distance between labels
void RemoveRepeatResults(vector<pair<char, int>>* detection_results,
        int Min_Label_Distance) {

    // Make same labels next to each other.
    sort(detection_results->begin(), detection_results->end(), label_compare);

    int len_results = detection_results->size();
    vector<pair<char, int>> uniq_results;

    for (int i = 0; i < len_results; ++i) {
        unsigned char cur_label = (*detection_results)[i].first;

        // Eliminate s
        vector<int> pos_list;
        for (int j = i; j < len_results; ++j) {
            if ((*detection_results)[j].first != (char)cur_label) {
                break;
            }
            pos_list.push_back((*detection_results)[j].second);
        }
        
        // sort same label's position list.
        sort(pos_list.begin(), pos_list.end());

        int rem_pos = pos_list[0];
        uniq_results.push_back(make_pair((char)cur_label, rem_pos));

        int len_pos_list = pos_list.size();
        for (int i = 1; i < len_pos_list; ++i) {
            int cur_pos = pos_list[i];
            if (abs(cur_pos - rem_pos) >= Min_Label_Distance) {
                rem_pos = cur_pos;
                uniq_results.push_back(make_pair((char)cur_label, rem_pos));
            }
            rem_pos = cur_pos;
        }

        i += static_cast<int>(pos_list.size()) - 1;
    }

    detection_results->assign(uniq_results.begin(), uniq_results.end());
    return;
}

/*
 * File trailer for call_simple_function.c
 *
 * [EOF]
 */

