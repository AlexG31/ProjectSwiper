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
#include <vector>
#include <utility>

using namespace std;

#define eps 1e-6


double abs(double val) {
    return val < -eps ? -val: val;
}

void ShowData(emxArray_real_T* result, string name = "data") {
    cout << name + "->size = "
         << result->allocatedSize
         << endl;

    for (int i = 0; i < result->allocatedSize; ++i) {
        cout << "val = "
             << result->data[i]
             << endl;
    }
}

// Get T_detector from 10 levels of s_rec
void GetT_detector10(const double s_rec[6500000], int jj_matlab,
          double fs, emxArray_real_T *T_detector);


/* Function Definitions */

/*
 * Arguments    : const double s_rec[6500000]
 *                double sig_len
 *                double fs
 *                emxArray_real_T *y_out
 * Return Type  : void
 */
void call_simple_function(const double s_rec[6500000], double sig_len, double fs,
  emxArray_real_T *y_out, vector<pair<char, int>>* result_out)
{

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
  /* y_out = struct('label', '.', 'val', double(0)); */
  /* if numel(s_rec) == 0 */
  /* y_out = []; */
  /* return; */
  /* end */
  /* % ========================================= */
  /* if numel(s_rec_struct) == 0 */
  /* y_out = []; */
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
  jj = 0;
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
    
    GetT_detector10(s_rec, jj + 1, fs, T_detector);
    //if (i1 - i0 == 0) {
      //i0 = T_detector->size[0] * T_detector->size[1];
      //T_detector->size[0] = 1;
      //emxEnsureCapacity((emxArray__common *)T_detector, i0, (int)sizeof(double));
      //i0 = T_detector->size[0] * T_detector->size[1];
      //T_detector->size[1] = sz[1];
      //emxEnsureCapacity((emxArray__common *)T_detector, i0, (int)sizeof(double));
      //loop_ub = sz[1];
      //for (i0 = 0; i0 < loop_ub; i0++) {
        //T_detector->data[i0] = 0.0;
      //}
    //} else {
      //ix = -1;
      //iy = -1;
      //for (loop_ub = 1; loop_ub <= i1 - i0; loop_ub++) {
        //ixstart = ix + 1;
        //ix++;
        //x_stop = s_rec[(ixstart % 5 + 10 * ((i0 + ixstart / 5) - 1)) + 3];
        //for (ixstart = 0; ixstart < 4; ixstart++) {
          //ix++;
          //x_stop += s_rec[(ix % 5 + 10 * ((i0 + ix / 5) - 1)) + 3];
        //}

        //iy++;
        //T_detector->data[iy] = x_stop;
      //}
    //}

    /*   QRS complex detection algorithm */
    i0 = b_QRS_detector->size[0] * b_QRS_detector->size[1];
    b_QRS_detector->size[0] = 1;
    b_QRS_detector->size[1] = QRS_detector->size[1];
    emxEnsureCapacity((emxArray__common *)b_QRS_detector, i0, (int)sizeof(double));
    loop_ub = QRS_detector->size[0] * QRS_detector->size[1];
    for (i0 = 0; i0 < loop_ub; i0++) {
      b_QRS_detector->data[i0] = QRS_detector->data[i0];
    }

    QRS_detection(b_QRS_detector, fs, QRS_detector, x_QRS);

    // Add to output vector.
    auto QRS_cap = x_QRS->allocatedSize;
    for (int i = 0; i < QRS_cap; ++i) {
        int val = x_QRS->data[i];
        if (val <= 0) break;
        result_out->push_back(make_pair('R', val + x_start));
    }

    cout << "x_QRS->allocatedSize = "
         << x_QRS->allocatedSize
         << endl;
    cout << "x_QRS->numDimensions = "
         << x_QRS->numDimensions
         << endl;

    for (int i = 0; i < x_QRS->numDimensions; ++i) {
        cout << "x_QRS->size["
             << i
             << "] = "
             << x_QRS->size[i]
             << endl;
    }

    for (int i = 0; i < x_QRS->allocatedSize; ++i) {
        cout << "val = "
             << x_QRS->data[i]
             << endl;
    }

    /*  QRS_Location_cur contains all QRS locations detected this 12s' window */
    i0 = QRS_detector->size[0] * QRS_detector->size[1];
    QRS_detector->size[0] = 1;
    QRS_detector->size[1] = x_QRS->size[1];
    emxEnsureCapacity((emxArray__common *)QRS_detector, i0, (int)sizeof(double));
    loop_ub = x_QRS->size[0] * x_QRS->size[1];
    for (i0 = 0; i0 < loop_ub; i0++) {
      QRS_detector->data[i0] = x_QRS->data[i0] + x_start;
    }

    /*   T and P wave detection        */
    T_detection(T_detector, fs, x_QRS, x_start, T_Location_cur, P_Location_cur);

    // Add to output vector.
    //auto T_cap = T_Location_cur->allocatedSize;
    //for (int i = 0; i < QRS_cap; ++i) {
        //int val = T_Location_cur->data[i];
        //if (val <= 0) break;
        //result_out->push_back(make_pair('T', val + x_start));
    //}

    ShowData(T_Location_cur, "T_Location_cur");
    ShowData(P_Location_cur, "P_Location_cur");
    /*  This part is gona to detect the repetitive detection in 2s' */
    /*  overlap between two adjacent windows */

    // Skip jj
    cout << "jj = " << jj << endl;
    jj++;
    //if (jj > 1) break;
    continue;

    if (abs((double)jj) < eps) {
      cout << "if (jj  = 0 )" << endl;

      ixstart = QRS_Location->size[1];
      ix = QRS_detector->size[1];
      i0 = QRS_Location->size[0] * QRS_Location->size[1];
      QRS_Location->size[1] = ixstart + ix;
      emxEnsureCapacity((emxArray__common *)QRS_Location, i0, (int)sizeof(double));
      for (i0 = 0; i0 < ix; i0++) {
        QRS_Location->data[ixstart + i0] = QRS_detector->data[i0];
      }

      if (T_Location_cur->data[0] > 0.0) {
        cout << "T_Location = " << T_Location_cur->data[0] << endl;

        i0 = c_T_Location_raw->size[0] * c_T_Location_raw->size[1];
        c_T_Location_raw->size[0] = T_Location_raw->size[0];
        c_T_Location_raw->size[1] = T_Location_raw->size[1] +
          T_Location_cur->size[1];
        emxEnsureCapacity((emxArray__common *)c_T_Location_raw, i0, (int)sizeof
                          (double));
        loop_ub = T_Location_raw->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = T_Location_raw->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            c_T_Location_raw->data[i1 + c_T_Location_raw->size[0] * i0] =
              T_Location_raw->data[i1 + T_Location_raw->size[0] * i0];
          }
        }

        loop_ub = T_Location_cur->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = T_Location_cur->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            c_T_Location_raw->data[i1 + c_T_Location_raw->size[0] * (i0 +
              T_Location_raw->size[1])] = T_Location_cur->data[i1 +
              T_Location_cur->size[0] * i0];
          }
        }

        i0 = T_Location_raw->size[0] * T_Location_raw->size[1];
        T_Location_raw->size[0] = c_T_Location_raw->size[0];
        T_Location_raw->size[1] = c_T_Location_raw->size[1];
        emxEnsureCapacity((emxArray__common *)T_Location_raw, i0, (int)sizeof
                          (double));
        loop_ub = c_T_Location_raw->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = c_T_Location_raw->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            T_Location_raw->data[i1 + T_Location_raw->size[0] * i0] =
              c_T_Location_raw->data[i1 + c_T_Location_raw->size[0] * i0];
          }
        }
      }

      if (P_Location_cur->data[0] > 0.0) {
        i0 = c_P_Location_raw->size[0] * c_P_Location_raw->size[1];
        c_P_Location_raw->size[0] = P_Location_raw->size[0];
        c_P_Location_raw->size[1] = P_Location_raw->size[1] +
          P_Location_cur->size[1];
        emxEnsureCapacity((emxArray__common *)c_P_Location_raw, i0, (int)sizeof
                          (double));
        loop_ub = P_Location_raw->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = P_Location_raw->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            c_P_Location_raw->data[i1 + c_P_Location_raw->size[0] * i0] =
              P_Location_raw->data[i1 + P_Location_raw->size[0] * i0];
          }
        }

        loop_ub = P_Location_cur->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = P_Location_cur->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            c_P_Location_raw->data[i1 + c_P_Location_raw->size[0] * (i0 +
              P_Location_raw->size[1])] = P_Location_cur->data[i1 +
              P_Location_cur->size[0] * i0];
          }
        }

        i0 = P_Location_raw->size[0] * P_Location_raw->size[1];
        P_Location_raw->size[0] = c_P_Location_raw->size[0];
        P_Location_raw->size[1] = c_P_Location_raw->size[1];
        emxEnsureCapacity((emxArray__common *)P_Location_raw, i0, (int)sizeof
                          (double));
        loop_ub = c_P_Location_raw->size[1];
        for (i0 = 0; i0 < loop_ub; i0++) {
          ixstart = c_P_Location_raw->size[0];
          for (i1 = 0; i1 < ixstart; i1++) {
            P_Location_raw->data[i1 + P_Location_raw->size[0] * i0] =
              c_P_Location_raw->data[i1 + c_P_Location_raw->size[0] * i0];
          }
        }
      }

      /*               plot( ECG_ori , 'g' );  */
      /*               hold on; plot(QRS_Location_cur-x_start, ECG_ori(QRS_Location_cur-x_start),'r.'); */
      /*               plot(T_Location_cur-x_start, ECG_ori(T_Location_cur-x_start),'bo'); */
      /*               plot(P_Location_cur-x_start, ECG_ori(P_Location_cur-x_start),'ko'); hold off; */
      /*               waitforbuttonpress */
      /*  Output: QRS detection result */
    } else {
      /*  ERROR: What happens if there's no QRS detected? */
      if (QRS_detector->size[1] == 0) {
      } else {
        if (QRS_detector->data[0] - QRS_Location->data[QRS_Location->size[1] - 1]
            > floor(fs / 20.0)) {
          ixstart = QRS_Location->size[1];
          ix = QRS_detector->size[1];
          i0 = QRS_Location->size[0] * QRS_Location->size[1];
          QRS_Location->size[1] = ixstart + ix;
          emxEnsureCapacity((emxArray__common *)QRS_Location, i0, (int)sizeof
                            (double));
          for (i0 = 0; i0 < ix; i0++) {
            QRS_Location->data[ixstart + i0] = QRS_detector->data[i0];
          }
        } else {
          if (2 > QRS_detector->size[1]) {
            i0 = 1;
            i1 = 1;
          } else {
            i0 = 2;
            i1 = QRS_detector->size[1] + 1;
          }

          ixstart = QRS_Location->size[1];
          ix = i1 - i0;
          iy = QRS_Location->size[0] * QRS_Location->size[1];
          QRS_Location->size[1] = ixstart + ix;
          emxEnsureCapacity((emxArray__common *)QRS_Location, iy, (int)sizeof
                            (double));
          iy = c_QRS_detector->size[0] * c_QRS_detector->size[1];
          c_QRS_detector->size[0] = 1;
          c_QRS_detector->size[1] = i1 - i0;
          emxEnsureCapacity((emxArray__common *)c_QRS_detector, iy, (int)sizeof
                            (double));
          loop_ub = i1 - i0;
          for (i1 = 0; i1 < loop_ub; i1++) {
            c_QRS_detector->data[c_QRS_detector->size[0] * i1] =
              QRS_detector->data[(i0 + i1) - 1];
          }

          for (i0 = 0; i0 < ix; i0++) {
            QRS_Location->data[ixstart + i0] = c_QRS_detector->data[i0];
          }
        }

        if (T_Location_cur->data[0] > 0.0) {
          if (T_Location_cur->data[0] - T_Location_raw->data[-1] > floor(fs /
               20.0)) {
            i0 = b_T_Location_raw->size[0] * b_T_Location_raw->size[1];
            b_T_Location_raw->size[0] = T_Location_raw->size[0];
            b_T_Location_raw->size[1] = T_Location_raw->size[1] +
              T_Location_cur->size[1];
            emxEnsureCapacity((emxArray__common *)b_T_Location_raw, i0, (int)
                              sizeof(double));
            loop_ub = T_Location_raw->size[1];
            for (i0 = 0; i0 < loop_ub; i0++) {
              ixstart = T_Location_raw->size[0];
              for (i1 = 0; i1 < ixstart; i1++) {
                b_T_Location_raw->data[i1 + b_T_Location_raw->size[0] * i0] =
                  T_Location_raw->data[i1 + T_Location_raw->size[0] * i0];
              }
            }

            loop_ub = T_Location_cur->size[1];
            for (i0 = 0; i0 < loop_ub; i0++) {
              ixstart = T_Location_cur->size[0];
              for (i1 = 0; i1 < ixstart; i1++) {
                b_T_Location_raw->data[i1 + b_T_Location_raw->size[0] * (i0 +
                  T_Location_raw->size[1])] = T_Location_cur->data[i1 +
                  T_Location_cur->size[0] * i0];
              }
            }

            i0 = T_Location_raw->size[0] * T_Location_raw->size[1];
            T_Location_raw->size[0] = b_T_Location_raw->size[0];
            T_Location_raw->size[1] = b_T_Location_raw->size[1];
            emxEnsureCapacity((emxArray__common *)T_Location_raw, i0, (int)
                              sizeof(double));
            loop_ub = b_T_Location_raw->size[1];
            for (i0 = 0; i0 < loop_ub; i0++) {
              ixstart = b_T_Location_raw->size[0];
              for (i1 = 0; i1 < ixstart; i1++) {
                T_Location_raw->data[i1 + T_Location_raw->size[0] * i0] =
                  b_T_Location_raw->data[i1 + b_T_Location_raw->size[0] * i0];
              }
            }
          } else {
            i0 = T_Location_cur->size[0] * T_Location_cur->size[1];
            if (2 > i0) {
              i1 = 1;
              i0 = 1;
            } else {
              i1 = 2;
              i0++;
            }

            ixstart = T_Location_raw->size[1];
            ix = i0 - i1;
            iy = T_Location_raw->size[0] * T_Location_raw->size[1];
            T_Location_raw->size[1] = ixstart + ix;
            emxEnsureCapacity((emxArray__common *)T_Location_raw, iy, (int)
                              sizeof(double));
            iy = b_T_Location_cur->size[0] * b_T_Location_cur->size[1];
            b_T_Location_cur->size[0] = 1;
            b_T_Location_cur->size[1] = i0 - i1;
            emxEnsureCapacity((emxArray__common *)b_T_Location_cur, iy, (int)
                              sizeof(double));
            loop_ub = i0 - i1;
            for (i0 = 0; i0 < loop_ub; i0++) {
              b_T_Location_cur->data[b_T_Location_cur->size[0] * i0] =
                T_Location_cur->data[(i1 + i0) - 1];
            }

            for (i0 = 0; i0 < ix; i0++) {
              T_Location_raw->data[ixstart + i0] = b_T_Location_cur->data[i0];
            }
          }
        }

        if (P_Location_cur->data[0] > 0.0) {
          i0 = b_P_Location_raw->size[0] * b_P_Location_raw->size[1];
          b_P_Location_raw->size[0] = P_Location_raw->size[0];
          b_P_Location_raw->size[1] = P_Location_raw->size[1] +
            P_Location_cur->size[1];
          emxEnsureCapacity((emxArray__common *)b_P_Location_raw, i0, (int)
                            sizeof(double));
          loop_ub = P_Location_raw->size[1];
          for (i0 = 0; i0 < loop_ub; i0++) {
            ixstart = P_Location_raw->size[0];
            for (i1 = 0; i1 < ixstart; i1++) {
              b_P_Location_raw->data[i1 + b_P_Location_raw->size[0] * i0] =
                P_Location_raw->data[i1 + P_Location_raw->size[0] * i0];
            }
          }

          loop_ub = P_Location_cur->size[1];
          for (i0 = 0; i0 < loop_ub; i0++) {
            ixstart = P_Location_cur->size[0];
            for (i1 = 0; i1 < ixstart; i1++) {
              b_P_Location_raw->data[i1 + b_P_Location_raw->size[0] * (i0 +
                P_Location_raw->size[1])] = P_Location_cur->data[i1 +
                P_Location_cur->size[0] * i0];
            }
          }

          i0 = P_Location_raw->size[0] * P_Location_raw->size[1];
          P_Location_raw->size[0] = b_P_Location_raw->size[0];
          P_Location_raw->size[1] = b_P_Location_raw->size[1];
          emxEnsureCapacity((emxArray__common *)P_Location_raw, i0, (int)sizeof
                            (double));
          loop_ub = b_P_Location_raw->size[1];
          for (i0 = 0; i0 < loop_ub; i0++) {
            ixstart = b_P_Location_raw->size[0];
            for (i1 = 0; i1 < ixstart; i1++) {
              P_Location_raw->data[i1 + P_Location_raw->size[0] * i0] =
                b_P_Location_raw->data[i1 + b_P_Location_raw->size[0] * i0];
            }
          }
        }

        /*               plot( ECG_ori , 'g' );  */
        /*               hold on; plot(QRS_Location_cur-x_start, ECG_ori(QRS_Location_cur-x_start),'r.'); */
        /*               plot(T_Location_cur-x_start, ECG_ori(T_Location_cur-x_start),'bo'); */
        /*               plot(P_Location_cur-x_start, ECG_ori(P_Location_cur-x_start),'ko'); hold off; */
        /*               waitforbuttonpress */
        /*  Output: QRS detection result */
      }
    }

    jj++;
  }

  cout << "end while" << endl;

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
  /*  y_out = result_position_list; */

  cout << "Before Ensured capacity: " << endl;
  i0 = y_out->size[0] * y_out->size[1];
  cout << "After Ensured capacity: " << endl;
  y_out->size[0] = 1;
  y_out->size[1] = (QRS_Location->size[1] + T_Location_raw->size[1]) +
    P_Location_raw->size[1];
  emxEnsureCapacity((emxArray__common *)y_out, i0, (int)sizeof(double));

  cout << "Ensured capacity: " << y_out->allocatedSize << endl;
  cout << "size: " 
       << y_out->size[0]
       << ", "
       << y_out->size[1]
       << endl;
  loop_ub = QRS_Location->size[1];
  cout << "QRS:" << loop_ub << endl;

  for (i0 = 0; i0 < loop_ub; i0++) {
    y_out->data[y_out->size[0] * i0] = QRS_Location->data[QRS_Location->size[0] *
      i0];
  }

  loop_ub = T_Location_raw->size[1];
  cout << "Before T output." 
       << loop_ub
       << endl;
  for (i0 = 0; i0 < loop_ub; i0++) {
    ixstart = T_Location_raw->size[0];
    for (i1 = 0; i1 < ixstart; i1++) {
      y_out->data[i1 + y_out->size[0] * (i0 + QRS_Location->size[1])] =
        T_Location_raw->data[i1 + T_Location_raw->size[0] * i0];
    }
  }

  loop_ub = P_Location_raw->size[1];
  cout << "Before P output." 
       << loop_ub
       << endl;
  for (i0 = 0; i0 < loop_ub; i0++) {
    ixstart = P_Location_raw->size[0];
    for (i1 = 0; i1 < ixstart; i1++) {
      y_out->data[i1 + y_out->size[0] * ((i0 + QRS_Location->size[1]) +
        T_Location_raw->size[1])] = P_Location_raw->data[i1 +
        P_Location_raw->size[0] * i0];
    }
  }

  emxFree_real_T(&P_Location_raw);
  emxFree_real_T(&T_Location_raw);
  emxFree_real_T(&QRS_Location);
}

// Get T_detector from 10 levels of s_rec
void GetT_detector10(const double s_rec[6500000], int jj_matlab,
          double fs, emxArray_real_T *T_detector) {

    double L_overlap = 2.0 * fs;

    int x_start = round(1.0+(jj_matlab -1)*fs*10) - 1;
    int x_stop = round((jj_matlab -1.0)*fs*10 + fs*10 + L_overlap) - 1;

    T_detector->size[1] = x_stop - x_start + 1;
    T_detector->size[0] = 1;
    emxEnsureCapacity((emxArray__common *)T_detector, 0, (int)sizeof(double));

    // Add levels 4:8(matlab indexes)
    for (int i = x_start; i <= x_stop; ++i) {
        int index_base = i * 10;
        T_detector->data[i] = s_rec[3 + index_base];
        T_detector->data[i] += s_rec[4 + index_base];
        T_detector->data[i] += s_rec[5 + index_base];
        T_detector->data[i] += s_rec[6 + index_base];
        T_detector->data[i] += s_rec[7 + index_base];
    }
    return;
}

/*
 * File trailer for call_simple_function.c
 *
 * [EOF]
 */

