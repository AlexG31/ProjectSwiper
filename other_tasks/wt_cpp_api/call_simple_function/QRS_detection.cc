/*
 * File: QRS_detection.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 11-Nov-2016 14:17:02
 */

/* Include files */
#include "rt_nonfinite.h"
#include "iostream"
#include "call_simple_function.h"
#include "QRS_detection.h"
#include "cmath"
#include "call_simple_function_emxutil.h"

using namespace std;

#define eps 1e-6
/* Function Definitions */
static double mean(double* buffer, int buffer_length) {
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

/*
 * QRS_DETECTION Summary of this function goes here
 *    Detailed explanation goes here
 * Arguments    : const emxArray_real_T *QRS_detector
 *                double fs
 *                emxArray_real_T *y_QRS
 *                emxArray_real_T *x_QRS
 * Return Type  : void
 */
void QRS_detection(const emxArray_real_T *QRS_detector, double fs,
                   emxArray_real_T *y_QRS, emxArray_real_T *x_QRS)
{
  // Return if input is empty
  int len_QRS_detector = QRS_detector->size[0] * QRS_detector->size[1];
  if (len_QRS_detector == 0 || abs(fs) < eps) return ;


  emxArray_real_T *Baseline;
  emxInit_real_T(&Baseline, 2);
  Baseline->size[0] = 1;
  Baseline->size[1] = 0;

  double qrs_detect_win;
  int ixstart;
  int mm;
  double d0;
  double d1;
  int i4;
  int i5;
  int ix;
  x_QRS->size[0] = 1;
  x_QRS->size[1] = 0;
  y_QRS->size[0] = 1;
  y_QRS->size[1] = 0;

  /*  The duriation of QRS complex is normally around 150ms - 300ms */
  /*  qrs_detect_win is a half of QRS detection window (150ms)   */
  qrs_detect_win = floor(fs * 150.0 / 1000.0);

  // zeros(1,len_QRS_detector);
  Baseline->size[1] = len_QRS_detector;
  Baseline->size[0] = 1;
  emxEnsureCapacity((emxArray__common *)Baseline, 0,
                    (int)sizeof(double));
  for (int i = 0; i < len_QRS_detector; ++i) {
    Baseline->data[i] = 1.0;
  }
  
  /*  Calculate the local (4s) baseline of QRS_detector  */
  int lower_Baseline = 2.0 * fs + 1.0;
  int upper_Baseline = len_QRS_detector - 2 * fs;


  for (mm = lower_Baseline; mm <= upper_Baseline; ++mm) {
      int data_bias =  mm - (int)fs * 2 - 1;
      Baseline->data[mm - 1] = mean(QRS_detector->data + data_bias,
                                    4 * (int)fs + 1);
  }


  /*   Earge prolongation */
  double val_before = Baseline->data[2 * (int)fs];
  for (int i = 0; i < 2 * (int)fs - 1; ++i) {
      Baseline->data[i] = val_before;
  } 
  double val_after = Baseline->data[len_QRS_detector - 2 * (int)fs - 1];
  for (int i = len_QRS_detector - 2*(int)fs; i < len_QRS_detector; ++i) {
      Baseline->data[i] = val_after;
  } 


  /*   plot(T_detector);hold on;plot(QRS_detector,'g');hold off; */
  /*  Sliding the detecting window amoung entire ECG detector, */
  /*  if the local maximum is located in the middle of the window and larger  */
  /*  than it's correspondding baseline, it would be recongnized as QRS complex */
  int mm_len = (int)(((double)QRS_detector->size[1] - qrs_detect_win) + (1.0 -
              (qrs_detect_win + 1.0)));
  for (mm = 0; mm < mm_len; mm++) {
    int matlab_mm = mm + qrs_detect_win + 1;
    // Upper bound
    int upper_bound = qrs_detect_win + matlab_mm;
    int lower_bound = matlab_mm - qrs_detect_win;


    // Empty QRS_det_local
    if (upper_bound < lower_bound) continue;

    double y_max = 0;
    int x_max = -1;

    for (int j = lower_bound - 1; j < upper_bound; ++j) {
        if (x_max == -1 || y_max < eps + QRS_detector->data[j]) {
            x_max = j - lower_bound + 2;
            y_max = QRS_detector->data[j];
        }
    }


    if ((y_max > 2.0 * Baseline->data[(int)matlab_mm - 1]) + eps && (x_max ==
        static_cast<int>(round(qrs_detect_win)) + 1)) {
        int cur_qrs_len = x_QRS->size[1];
        i4 = x_QRS->size[0] * x_QRS->size[1];
        x_QRS->size[1] = cur_qrs_len + 1;
        emxEnsureCapacity((emxArray__common *)x_QRS, i4, (int)sizeof(double));
        x_QRS->data[cur_qrs_len] = matlab_mm;

        cur_qrs_len = y_QRS->size[1];
        i4 = y_QRS->size[0] * y_QRS->size[1];
        y_QRS->size[1] = cur_qrs_len + 1;
        emxEnsureCapacity((emxArray__common *)y_QRS, i4, (int)sizeof(double));
        y_QRS->data[cur_qrs_len] = y_max;
    }
  }

  emxFree_real_T(&Baseline);

}

/*
 * File trailer for QRS_detection.c
 *
 * [EOF]
 */
