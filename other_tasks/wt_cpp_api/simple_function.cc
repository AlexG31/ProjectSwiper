/*
 * File: simple_function.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include <stdio.h>
#include <iostream>

#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "simple_function.h"
#include "call_simple_function_emxutil.h"
#include "T_detection.h"
#include "QRS_detection.h"
#include "sum.h"
#include "abs.h"

using namespace std;

/* Function Definitions */

/*
 * % Test QRS & P & T wave
 * L_sig = floor((length(data_raw)-fs)/(fs*10));
 * Arguments    : const emxArray_real_T *s_rec
 *                double L_sig
 *                double fs
 *                emxArray_struct0_T *y_out
 * Return Type  : void
 */
void simple_function(const emxArray_real_T *s_rec, double L_sig, double fs,
                     emxArray_struct0_T *y_out)
{
  cout << "Simple_function: Input parameters: "
       << L_sig << ", "
       << fs << ", "
       << endl;

  emxArray_real_T *QRS_Location;
  double L_overlap;
  int i1;
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
  double x_start;
  double x_stop;
  int i2;
  int iy;
  int loop_ub;
  int ixstart;
  unsigned int sz[2];
  int ix;
  struct0_T cur_node;
  emxInit_real_T(&QRS_Location, 2);

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
  i1 = QRS_Location->size[0] * QRS_Location->size[1];
  QRS_Location->size[0] = 1;
  QRS_Location->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)QRS_Location, i1, (int)sizeof(double));

  /*  Output list */
  i1 = y_out->size[0] * y_out->size[1];

  y_out->size[0] = 1;
  y_out->size[1] = 0;


  emxEnsureCapacity((emxArray__common *)y_out, i1, (int)sizeof(struct0_T));
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

  while (jj <= (int)L_sig - 1) {
    x_start = 1.0 + ((1.0 + (double)jj) - 1.0) * fs * 10.0;
    x_stop = (((1.0 + (double)jj) - 1.0) * fs * 10.0 + fs * 10.0) + L_overlap;

    /*  ECG with wavelet sub-levels 1 to 8, is equal to high pass filter */
    /*  QRS_detector is used to detect qrs complex, whose energy is */
    /*  concentrate at 10 - 50 Hz */
    if (x_start > x_stop) {
      i1 = 0;
      i2 = 0;
    } else {
      i1 = (int)x_start - 1;
      i2 = (int)x_stop;
    }

    iy = b_s_rec->size[0] * b_s_rec->size[1];
    b_s_rec->size[0] = 3;
    b_s_rec->size[1] = i2 - i1;
    emxEnsureCapacity((emxArray__common *)b_s_rec, iy, (int)sizeof(double));
    loop_ub = i2 - i1;
    for (i2 = 0; i2 < loop_ub; i2++) {
      for (iy = 0; iy < 3; iy++) {
        b_s_rec->data[iy + b_s_rec->size[0] * i2] = s_rec->data[(iy +
          s_rec->size[0] * (i1 + i2)) + 2];
      }
    }

    b_abs(b_s_rec, r0);
    sum(r0, QRS_detector);

    /*  QRS_detector is used to detect T and P wave, whose energy is */
    /*  concentrate at 1 - 10 Hz */
    if (x_start > x_stop) {
      i1 = 1;
      i2 = 1;
    } else {
      i1 = (int)x_start;
      i2 = (int)x_stop + 1;
    }

    iy = c_s_rec->size[0] * c_s_rec->size[1];
    c_s_rec->size[0] = 5;
    c_s_rec->size[1] = i2 - i1;
    emxEnsureCapacity((emxArray__common *)c_s_rec, iy, (int)sizeof(double));
    loop_ub = i2 - i1;
    for (iy = 0; iy < loop_ub; iy++) {
      for (ixstart = 0; ixstart < 5; ixstart++) {
        c_s_rec->data[ixstart + c_s_rec->size[0] * iy] = s_rec->data[(ixstart +
          s_rec->size[0] * ((i1 + iy) - 1)) + 3];
      }
    }

    for (iy = 0; iy < 2; iy++) {
      sz[iy] = (unsigned int)c_s_rec->size[iy];
    }

    iy = T_detector->size[0] * T_detector->size[1];
    T_detector->size[0] = 1;
    T_detector->size[1] = (int)sz[1];
    emxEnsureCapacity((emxArray__common *)T_detector, iy, (int)sizeof(double));
    if (i2 - i1 == 0) {
      i1 = T_detector->size[0] * T_detector->size[1];
      T_detector->size[0] = 1;
      emxEnsureCapacity((emxArray__common *)T_detector, i1, (int)sizeof(double));
      i1 = T_detector->size[0] * T_detector->size[1];
      T_detector->size[1] = (int)sz[1];
      emxEnsureCapacity((emxArray__common *)T_detector, i1, (int)sizeof(double));
      loop_ub = (int)sz[1];
      for (i1 = 0; i1 < loop_ub; i1++) {
        T_detector->data[i1] = 0.0;
      }
    } else {
      ix = -1;
      iy = -1;
      for (loop_ub = 1; loop_ub <= i2 - i1; loop_ub++) {
        ixstart = ix + 1;
        ix++;
        x_stop = s_rec->data[(ixstart % 5 + s_rec->size[0] * ((i1 + ixstart / 5)
          - 1)) + 3];
        for (ixstart = 0; ixstart < 4; ixstart++) {
          ix++;
          x_stop += s_rec->data[(ix % 5 + s_rec->size[0] * ((i1 + ix / 5) - 1))
            + 3];
        }

        iy++;
        T_detector->data[iy] = x_stop;
      }
    }

    /*   QRS complex detection algorithm */
    i1 = b_QRS_detector->size[0] * b_QRS_detector->size[1];
    b_QRS_detector->size[0] = 1;
    b_QRS_detector->size[1] = QRS_detector->size[1];
    emxEnsureCapacity((emxArray__common *)b_QRS_detector, i1, (int)sizeof(double));
    loop_ub = QRS_detector->size[0] * QRS_detector->size[1];
    for (i1 = 0; i1 < loop_ub; i1++) {
      b_QRS_detector->data[i1] = QRS_detector->data[i1];
    }


    QRS_detection(b_QRS_detector, fs, QRS_detector, x_QRS);

    

    /*  QRS_Location_cur contains all QRS locations detected this 12s' window */
    i1 = QRS_detector->size[0] * QRS_detector->size[1];
    QRS_detector->size[0] = 1;
    QRS_detector->size[1] = x_QRS->size[1];
    emxEnsureCapacity((emxArray__common *)QRS_detector, i1, (int)sizeof(double));
    loop_ub = x_QRS->size[0] * x_QRS->size[1];
    for (i1 = 0; i1 < loop_ub; i1++) {
      QRS_detector->data[i1] = x_QRS->data[i1] + x_start;
    }

    cout << "Before T & P detection" << endl;
    /*   T and P wave detection        */
    //T_detection(T_detector, fs, x_QRS, x_start, T_Location_cur, P_Location_cur);

    cout << "After T & P detection" << endl;

    /*cout << "Detection Complete." << endl;*/

    /*  This part is gona to detect the repetitive detection in 2s' */
    /*  overlap between two adjacent windows */
    if (1.0 + (double)jj == 1.0) {
      ix = QRS_Location->size[1];
      ixstart = QRS_detector->size[1];
      i1 = QRS_Location->size[0] * QRS_Location->size[1];
      QRS_Location->size[1] = ix + ixstart;
      emxEnsureCapacity((emxArray__common *)QRS_Location, i1, (int)sizeof(double));
      for (i1 = 0; i1 < ixstart; i1++) {
        QRS_Location->data[ix + i1] = QRS_detector->data[i1];
      }

      /* plot( ECG_ori , 'g' ); hold on; plot(QRS_Location_cur-x_start, ECG_ori(QRS_Location_cur-x_start),'r.'); */
      /* plot(T_Location_cur-x_start, ECG_ori(T_Location_cur-x_start),'bo'); */
      /* plot(P_Location_cur-x_start, ECG_ori(P_Location_cur-x_start),'ko'); hold off; */
      /* waitforbuttonpress */
      /*  Output: QRS detection result */
    } else {
      /*  ERROR: What happens if there's no QRS detected? */
      if (QRS_detector->size[1] == 0) {
      } else {
        if (QRS_detector->data[0] - QRS_Location->data[QRS_Location->size[1] - 1]
            > floor(fs / 20.0)) {
          ix = QRS_Location->size[1];
          ixstart = QRS_detector->size[1];
          i1 = QRS_Location->size[0] * QRS_Location->size[1];
          QRS_Location->size[1] = ix + ixstart;
          emxEnsureCapacity((emxArray__common *)QRS_Location, i1, (int)sizeof
                            (double));
          for (i1 = 0; i1 < ixstart; i1++) {
            QRS_Location->data[ix + i1] = QRS_detector->data[i1];
          }
        } else {
          if (2 > QRS_detector->size[1]) {
            i1 = 1;
            i2 = 1;
          } else {
            i1 = 2;
            i2 = QRS_detector->size[1] + 1;
          }

          ix = QRS_Location->size[1];
          ixstart = i2 - i1;
          iy = QRS_Location->size[0] * QRS_Location->size[1];
          QRS_Location->size[1] = ix + ixstart;
          emxEnsureCapacity((emxArray__common *)QRS_Location, iy, (int)sizeof
                            (double));
          iy = c_QRS_detector->size[0] * c_QRS_detector->size[1];
          c_QRS_detector->size[0] = 1;
          c_QRS_detector->size[1] = i2 - i1;
          emxEnsureCapacity((emxArray__common *)c_QRS_detector, iy, (int)sizeof
                            (double));
          loop_ub = i2 - i1;
          for (i2 = 0; i2 < loop_ub; i2++) {
            c_QRS_detector->data[c_QRS_detector->size[0] * i2] =
              QRS_detector->data[(i1 + i2) - 1];
          }

          for (i1 = 0; i1 < ixstart; i1++) {
            QRS_Location->data[ix + i1] = c_QRS_detector->data[i1];
          }
        }

        /* plot( ECG_ori , 'g' ); hold on; plot(QRS_Location_cur-x_start, ECG_ori(QRS_Location_cur-x_start),'r.'); */
        /* plot(T_Location_cur-x_start, ECG_ori(T_Location_cur-x_start),'bo'); */
        /* plot(P_Location_cur-x_start, ECG_ori(P_Location_cur-x_start),'ko'); hold off; */
        /* waitforbuttonpress */
        /*  Output: QRS detection result */
      }
    }

    jj++;
  }

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
  for (ixstart = 0; ixstart < QRS_Location->size[1]; ixstart++) {
    cur_node.label = 'R';
    cur_node.val = QRS_Location->data[ixstart];
    ix = y_out->size[1];
    i1 = y_out->size[0] * y_out->size[1];
    y_out->size[1] = ix + 1;
    emxEnsureCapacity((emxArray__common *)y_out, i1, (int)sizeof(struct0_T));
    y_out->data[ix] = cur_node;
  }

  emxFree_real_T(&QRS_Location);
}

/*
 * File trailer for simple_function.c
 *
 * [EOF]
 */
