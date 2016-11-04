/*
 * File: QRS_detection.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "QRS_detection.h"
#include "mean.h"
#include "call_simple_function_emxutil.h"

/* Function Definitions */

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
  emxArray_real_T *Baseline;
  int i4;
  double qrs_detect_win;
  int ixstart;
  double b_Baseline;
  int mm;
  emxArray_real_T *b_QRS_detector;
  double b_mm;
  double d0;
  double d1;
  int i5;
  int i6;
  emxArray_int32_T *r1;
  int itmp;
  int ix;
  boolean_T exitg1;
  emxInit_real_T(&Baseline, 2);
  i4 = x_QRS->size[0] * x_QRS->size[1];
  x_QRS->size[0] = 1;
  x_QRS->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)x_QRS, i4, (int)sizeof(double));
  i4 = y_QRS->size[0] * y_QRS->size[1];
  y_QRS->size[0] = 1;
  y_QRS->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)y_QRS, i4, (int)sizeof(double));

  /*  The duriation of QRS complex is normally around 150ms - 300ms */
  /*  qrs_detect_win is a half of QRS detection window (150ms)   */
  qrs_detect_win = floor(fs * 150.0 / 1000.0);
  i4 = Baseline->size[0] * Baseline->size[1];
  Baseline->size[0] = 1;
  emxEnsureCapacity((emxArray__common *)Baseline, i4, (int)sizeof(double));
  ixstart = QRS_detector->size[1];
  i4 = Baseline->size[0] * Baseline->size[1];
  Baseline->size[1] = ixstart;
  emxEnsureCapacity((emxArray__common *)Baseline, i4, (int)sizeof(double));
  ixstart = QRS_detector->size[1];
  for (i4 = 0; i4 < ixstart; i4++) {
    Baseline->data[i4] = 1.0;
  }

  /*  Calculate the local (4s) baseline of QRS_detector  */
  b_Baseline = 2.0 * fs + 1.0;
  i4 = (int)(((double)QRS_detector->size[1] - 2.0 * fs) + (1.0 - b_Baseline));
  mm = 0;
  emxInit_real_T(&b_QRS_detector, 2);
  while (mm <= i4 - 1) {
    b_mm = b_Baseline + (double)mm;
    d0 = b_mm - fs * 2.0;
    d1 = b_mm + fs * 2.0;
    if (d0 > d1) {
      i5 = 0;
      i6 = 0;
    } else {
      i5 = (int)d0 - 1;
      i6 = (int)d1;
    }

    ixstart = b_QRS_detector->size[0] * b_QRS_detector->size[1];
    b_QRS_detector->size[0] = 1;
    b_QRS_detector->size[1] = i6 - i5;
    emxEnsureCapacity((emxArray__common *)b_QRS_detector, ixstart, (int)sizeof
                      (double));
    ixstart = i6 - i5;
    for (i6 = 0; i6 < ixstart; i6++) {
      b_QRS_detector->data[b_QRS_detector->size[0] * i6] = QRS_detector->data[i5
        + i6];
    }

    Baseline->data[(int)b_mm - 1] = mean(b_QRS_detector);
    mm++;
  }

  emxFree_real_T(&b_QRS_detector);

  /*   Earge prolongation */
  b_Baseline = 2.0 * fs;
  if (1.0 > b_Baseline) {
    ixstart = 0;
  } else {
    ixstart = (int)b_Baseline;
  }

  emxInit_int32_T(&r1, 2);
  i4 = r1->size[0] * r1->size[1];
  r1->size[0] = 1;
  r1->size[1] = ixstart;
  emxEnsureCapacity((emxArray__common *)r1, i4, (int)sizeof(int));
  for (i4 = 0; i4 < ixstart; i4++) {
    r1->data[r1->size[0] * i4] = i4;
  }

  b_Baseline = Baseline->data[(int)(2.0 * fs + 1.0) - 1];
  ixstart = r1->size[0] * r1->size[1];
  for (i4 = 0; i4 < ixstart; i4++) {
    Baseline->data[r1->data[i4]] = b_Baseline;
  }

  b_Baseline = ((double)QRS_detector->size[1] - 2.0 * fs) + 1.0;
  if (b_Baseline > QRS_detector->size[1]) {
    i4 = 0;
    i5 = 0;
  } else {
    i4 = (int)b_Baseline - 1;
    i5 = QRS_detector->size[1];
  }

  i6 = r1->size[0] * r1->size[1];
  r1->size[0] = 1;
  r1->size[1] = i5 - i4;
  emxEnsureCapacity((emxArray__common *)r1, i6, (int)sizeof(int));
  ixstart = i5 - i4;
  for (i5 = 0; i5 < ixstart; i5++) {
    r1->data[r1->size[0] * i5] = i4 + i5;
  }

  b_Baseline = Baseline->data[(int)((double)QRS_detector->size[1] - 2.0 * fs) -
    1];
  ixstart = r1->size[0] * r1->size[1];
  for (i4 = 0; i4 < ixstart; i4++) {
    Baseline->data[r1->data[i4]] = b_Baseline;
  }

  emxFree_int32_T(&r1);

  /*   plot(T_detector);hold on;plot(QRS_detector,'g');hold off; */
  /*  Sliding the detecting window amoung entire ECG detector, */
  /*  if the local maximum is located in the middle of the window and larger  */
  /*  than it's correspondding baseline, it would be recongnized as QRS complex */
  i4 = (int)(((double)QRS_detector->size[1] - qrs_detect_win) + (1.0 -
              (qrs_detect_win + 1.0)));
  for (mm = 0; mm < i4; mm++) {
    b_mm = (qrs_detect_win + 1.0) + (double)mm;
    b_Baseline = b_mm - qrs_detect_win;
    d0 = b_mm + qrs_detect_win;
    if (b_Baseline > d0) {
      i5 = 1;
      i6 = 1;
    } else {
      i5 = (int)b_Baseline;
      i6 = (int)d0 + 1;
    }

    ixstart = 1;
    b_Baseline = QRS_detector->data[i5 - 1];
    itmp = 1;
    if (i6 - i5 > 1) {
      if (rtIsNaN(b_Baseline)) {
        ix = 2;
        exitg1 = false;
        while ((!exitg1) && (ix <= i6 - i5)) {
          ixstart = ix;
          if (!rtIsNaN(QRS_detector->data[(i5 + ix) - 2])) {
            b_Baseline = QRS_detector->data[(i5 + ix) - 2];
            itmp = ix;
            exitg1 = true;
          } else {
            ix++;
          }
        }
      }

      if (ixstart < i6 - i5) {
        while (ixstart + 1 <= i6 - i5) {
          if (QRS_detector->data[(i5 + ixstart) - 1] > b_Baseline) {
            b_Baseline = QRS_detector->data[(i5 + ixstart) - 1];
            itmp = ixstart + 1;
          }

          ixstart++;
        }
      }
    }

    if ((b_Baseline > 2.0 * Baseline->data[(int)b_mm - 1]) && (itmp ==
         qrs_detect_win + 1.0)) {
      ixstart = x_QRS->size[1];
      i5 = x_QRS->size[0] * x_QRS->size[1];
      x_QRS->size[1] = ixstart + 1;
      emxEnsureCapacity((emxArray__common *)x_QRS, i5, (int)sizeof(double));
      x_QRS->data[ixstart] = b_mm;
      ixstart = y_QRS->size[1];
      i5 = y_QRS->size[0] * y_QRS->size[1];
      y_QRS->size[1] = ixstart + 1;
      emxEnsureCapacity((emxArray__common *)y_QRS, i5, (int)sizeof(double));
      y_QRS->data[ixstart] = b_Baseline;
    }
  }

  emxFree_real_T(&Baseline);
}

/*
 * File trailer for QRS_detection.c
 *
 * [EOF]
 */
