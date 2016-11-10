/*
 * File: T_detection.c
 *
 * MATLAB Coder version            : 2.6
 * C/C++ source code generated on  : 01-Nov-2016 21:21:14
 */

/* Include files */
#include "rt_nonfinite.h"
#include "call_simple_function.h"
#include "T_detection.h"
#include "call_simple_function_emxutil.h"
#include "gaussian_function.h"
#include "eml_sort.h"
#include "floor.h"
#include "rdivide.h"
#include "mean.h"
#include "power.h"

/* Function Definitions */

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
void T_detection(emxArray_real_T *T_detector, double fs, const emxArray_real_T
                 *x_QRS, double x_start, emxArray_real_T *T_Location_cur,
                 emxArray_real_T *P_Location_cur)
{
  emxArray_real_T *Win_Gaussian;
  emxArray_real_T *r2;
  double mtmp;
  int i7;
  int cdiff;
  emxArray_real_T *T_position_pos;
  double t_detect_win;
  double t_win_mf;
  emxArray_real_T *b_Win_Gaussian;
  int ftmp;
  int absb;
  int mm;
  emxArray_real_T *T_detector_win_ori;
  emxArray_real_T *T_detector_win;
  emxArray_real_T *X_max;
  emxArray_real_T *c_Win_Gaussian;
  int i8;
  int i9;
  int lttmp;
  int apnd;
  double b_fs[2];
  double kk;
  double d2;
  boolean_T exitg1;
  emxInit_real_T(&Win_Gaussian, 2);
  emxInit_real_T(&r2, 2);

  /* % T wave detection */
  /*  The input signal would be normalized at first */
  power(T_detector, Win_Gaussian);
  mtmp = mean(Win_Gaussian);
  i7 = r2->size[0] * r2->size[1];
  r2->size[0] = 1;
  r2->size[1] = T_detector->size[1];
  emxEnsureCapacity((emxArray__common *)r2, i7, (int)sizeof(double));
  cdiff = T_detector->size[0] * T_detector->size[1];
  for (i7 = 0; i7 < cdiff; i7++) {
    r2->data[i7] = 100.0 * T_detector->data[i7];
  }

  emxInit_real_T(&T_position_pos, 2);
  rdivide(r2, sqrt(mtmp), T_detector);

  /*  Definelength of T wave detecting window (half) */
  t_detect_win = floor(fs * 150.0 / 1000.0);
  i7 = T_position_pos->size[0] * T_position_pos->size[1];
  T_position_pos->size[0] = 1;
  T_position_pos->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)T_position_pos, i7, (int)sizeof(double));
  i7 = T_Location_cur->size[0] * T_Location_cur->size[1];
  T_Location_cur->size[0] = 0;
  T_Location_cur->size[1] = 0;
  emxEnsureCapacity((emxArray__common *)T_Location_cur, i7, (int)sizeof(double));
  i7 = Win_Gaussian->size[0] * Win_Gaussian->size[1];
  Win_Gaussian->size[0] = 1;
  Win_Gaussian->size[1] = T_detector->size[1];
  emxEnsureCapacity((emxArray__common *)Win_Gaussian, i7, (int)sizeof(double));
  cdiff = T_detector->size[0] * T_detector->size[1];
  emxFree_real_T(&r2);
  for (i7 = 0; i7 < cdiff; i7++) {
    Win_Gaussian->data[i7] = T_detector->data[i7];
  }

  b_floor(Win_Gaussian);
  if (Win_Gaussian->size[1] == 0) {
    t_win_mf = rtNaN;
  } else {
    emxInit_real_T(&b_Win_Gaussian, 2);
    i7 = b_Win_Gaussian->size[0] * b_Win_Gaussian->size[1];
    b_Win_Gaussian->size[0] = 1;
    b_Win_Gaussian->size[1] = Win_Gaussian->size[1];
    emxEnsureCapacity((emxArray__common *)b_Win_Gaussian, i7, (int)sizeof(double));
    cdiff = Win_Gaussian->size[0] * Win_Gaussian->size[1];
    for (i7 = 0; i7 < cdiff; i7++) {
      b_Win_Gaussian->data[i7] = Win_Gaussian->data[i7];
    }

    eml_sort(b_Win_Gaussian, Win_Gaussian);
    t_win_mf = Win_Gaussian->data[0];
    cdiff = 1;
    mtmp = Win_Gaussian->data[0];
    ftmp = 1;
    absb = 1;
    emxFree_real_T(&b_Win_Gaussian);
    while (absb - 1 <= Win_Gaussian->size[1] - 2) {
      if (Win_Gaussian->data[absb] == mtmp) {
        ftmp++;
      } else {
        if (ftmp > cdiff) {
          t_win_mf = mtmp;
          cdiff = ftmp;
        }

        mtmp = Win_Gaussian->data[absb];
        ftmp = 1;
      }

      absb++;
    }

    if (ftmp > cdiff) {
      t_win_mf = mtmp;
    }
  }

  /* % Run the algorithm beat by beat */
  mm = 0;
  emxInit_real_T(&T_detector_win_ori, 2);
  emxInit_real_T(&T_detector_win, 2);
  emxInit_real_T(&X_max, 2);
  emxInit_real_T(&c_Win_Gaussian, 2);
  while (mm <= x_QRS->size[1] - 2) {
    /*     %% T wave detect */
    /*  T_detector in each beat */
    if (x_QRS->data[mm] > x_QRS->data[mm + 1]) {
      i7 = 1;
      i8 = 1;
    } else {
      i7 = (int)x_QRS->data[mm];
      i8 = (int)x_QRS->data[mm + 1] + 1;
    }

    i9 = T_detector_win_ori->size[0] * T_detector_win_ori->size[1];
    T_detector_win_ori->size[0] = 1;
    T_detector_win_ori->size[1] = i8 - i7;
    emxEnsureCapacity((emxArray__common *)T_detector_win_ori, i9, (int)sizeof
                      (double));
    cdiff = i8 - i7;
    for (i9 = 0; i9 < cdiff; i9++) {
      T_detector_win_ori->data[T_detector_win_ori->size[0] * i9] =
        T_detector->data[(i7 + i9) - 1];
    }

    /*  lttmp: length of T (temp) */
    lttmp = i8 - i7;

    /*  Gaussian window would outline the T wave : sigma , ave */
    /*  sigma : fs/5 mean */
    /*  ave : the minimum of fs/3 and lttmp/2 */
    if (i8 - i7 < 1) {
      cdiff = -1;
      apnd = i8 - i7;
    } else {
      ftmp = (int)floor(((double)lttmp - 1.0) + 0.5);
      apnd = ftmp + 1;
      cdiff = ((ftmp - i8) + i7) + 1;
      absb = i8 - i7;
      if (1 >= absb) {
        absb = 1;
      }

      if (fabs(cdiff) < 4.4408920985006262E-16 * (double)absb) {
        ftmp++;
        apnd = i8 - i7;
      } else if (cdiff > 0) {
        apnd = ftmp;
      } else {
        ftmp++;
      }

      if (ftmp >= 0) {
        cdiff = ftmp - 1;
      } else {
        cdiff = -1;
      }
    }

    i9 = Win_Gaussian->size[0] * Win_Gaussian->size[1];
    Win_Gaussian->size[0] = 1;
    Win_Gaussian->size[1] = cdiff + 1;
    emxEnsureCapacity((emxArray__common *)Win_Gaussian, i9, (int)sizeof(double));
    if (cdiff + 1 > 0) {
      Win_Gaussian->data[0] = 1.0;
      if (cdiff + 1 > 1) {
        Win_Gaussian->data[cdiff] = apnd;
        ftmp = cdiff / 2;
        for (absb = 1; absb < ftmp; absb++) {
          Win_Gaussian->data[absb] = 1.0 + (double)absb;
          Win_Gaussian->data[cdiff - absb] = apnd - absb;
        }

        if (ftmp << 1 == cdiff) {
          Win_Gaussian->data[ftmp] = (1.0 + (double)apnd) / 2.0;
        } else {
          Win_Gaussian->data[ftmp] = 1.0 + (double)ftmp;
          Win_Gaussian->data[ftmp + 1] = apnd - ftmp;
        }
      }
    }

    mtmp = fs / 4.0;
    ftmp = (int)floor((double)(i8 - i7) / 2.0);
    apnd = 1;
    if (rtIsNaN(mtmp)) {
      apnd = 2;
      mtmp = ftmp;
    }

    if ((apnd < 2) && (ftmp < mtmp)) {
      mtmp = ftmp;
    }

    b_fs[0] = fs / 5.0;
    b_fs[1] = mtmp;
    i9 = c_Win_Gaussian->size[0] * c_Win_Gaussian->size[1];
    c_Win_Gaussian->size[0] = 1;
    c_Win_Gaussian->size[1] = Win_Gaussian->size[1];
    emxEnsureCapacity((emxArray__common *)c_Win_Gaussian, i9, (int)sizeof(double));
    cdiff = Win_Gaussian->size[0] * Win_Gaussian->size[1];
    for (i9 = 0; i9 < cdiff; i9++) {
      c_Win_Gaussian->data[i9] = Win_Gaussian->data[i9];
    }

    gaussian_function(c_Win_Gaussian, b_fs, Win_Gaussian);
    i9 = T_detector_win->size[0] * T_detector_win->size[1];
    T_detector_win->size[0] = 1;
    T_detector_win->size[1] = T_detector_win_ori->size[1];
    emxEnsureCapacity((emxArray__common *)T_detector_win, i9, (int)sizeof(double));
    cdiff = T_detector_win_ori->size[0] * T_detector_win_ori->size[1];
    for (i9 = 0; i9 < cdiff; i9++) {
      T_detector_win->data[i9] = T_detector_win_ori->data[i9] *
        Win_Gaussian->data[i9];
    }

    i9 = X_max->size[0] * X_max->size[1];
    X_max->size[0] = 1;
    X_max->size[1] = 0;
    emxEnsureCapacity((emxArray__common *)X_max, i9, (int)sizeof(double));
    i9 = Win_Gaussian->size[0] * Win_Gaussian->size[1];
    Win_Gaussian->size[0] = 1;
    Win_Gaussian->size[1] = 0;
    emxEnsureCapacity((emxArray__common *)Win_Gaussian, i9, (int)sizeof(double));

    /*  Calculated the location of T */
    if (i8 - i7 > 2.0 * t_detect_win) {
      i7 = (int)(((double)lttmp - t_detect_win) + (1.0 - (1.0 + t_detect_win)));
      for (cdiff = 0; cdiff < i7; cdiff++) {
        kk = (1.0 + t_detect_win) + (double)cdiff;
        mtmp = kk - t_detect_win;
        d2 = kk + t_detect_win;
        if (mtmp > d2) {
          i8 = 1;
          i9 = 1;
        } else {
          i8 = (int)mtmp;
          i9 = (int)d2 + 1;
        }

        apnd = 1;
        mtmp = T_detector_win->data[i8 - 1];
        absb = 1;
        if (i9 - i8 > 1) {
          if (rtIsNaN(mtmp)) {
            ftmp = 2;
            exitg1 = false;
            while ((!exitg1) && (ftmp <= i9 - i8)) {
              apnd = ftmp;
              if (!rtIsNaN(T_detector_win->data[(i8 + ftmp) - 2])) {
                mtmp = T_detector_win->data[(i8 + ftmp) - 2];
                absb = ftmp;
                exitg1 = true;
              } else {
                ftmp++;
              }
            }
          }

          if (apnd < i9 - i8) {
            for (ftmp = apnd + 1; ftmp <= i9 - i8; ftmp++) {
              if (T_detector_win->data[(i8 + ftmp) - 2] > mtmp) {
                mtmp = T_detector_win->data[(i8 + ftmp) - 2];
                absb = ftmp;
              }
            }
          }
        }

        if ((absb == t_detect_win + 1.0) && (mtmp > t_win_mf)) {
          ftmp = X_max->size[1];
          i8 = X_max->size[0] * X_max->size[1];
          X_max->size[1] = ftmp + 1;
          emxEnsureCapacity((emxArray__common *)X_max, i8, (int)sizeof(double));
          X_max->data[ftmp] = kk;
          ftmp = Win_Gaussian->size[1];
          i8 = Win_Gaussian->size[0] * Win_Gaussian->size[1];
          Win_Gaussian->size[1] = ftmp + 1;
          emxEnsureCapacity((emxArray__common *)Win_Gaussian, i8, (int)sizeof
                            (double));
          Win_Gaussian->data[ftmp] = mtmp;
        }
      }

      /*            plot(T_detector_win);hold on; plot(X_max, T_detector_win(X_max),'ro');plot(X_min, T_detector_win(X_min), 'k*') */
      /*  */
      /*            plot(100*Win_Gaussian, 'g'); hold off; */
    }

    /*  Location of positive T */
    mtmp = Win_Gaussian->data[0];
    absb = 0;
    if (Win_Gaussian->size[1] > 1) {
      for (ftmp = 1; ftmp + 1 <= Win_Gaussian->size[1]; ftmp++) {
        if (Win_Gaussian->data[ftmp] > mtmp) {
          mtmp = Win_Gaussian->data[ftmp];
          absb = ftmp;
        }
      }
    }

    /*  Location of negtive T */
    /*  Location of T with maximum x */
    /*     %% P_wave detection */
    /*   QT_interval is  normally between 120 and 200ms in duration */
    /*  Gaussion window for P wave detection */
    /*  p_detect_stat��start of sliding P detecting window */
    /*  Adjust of P wave detecting area according to the form of the next QRS */
    /*  T_detector_win(end) indicates wheahter the next R peak is positive or */
    /*  negtive */
    /*  P wave detection */
    /*  Label the T, P location back to entire window */
    ftmp = T_position_pos->size[1];
    i7 = T_position_pos->size[0] * T_position_pos->size[1];
    T_position_pos->size[1] = ftmp + 1;
    emxEnsureCapacity((emxArray__common *)T_position_pos, i7, (int)sizeof(double));
    T_position_pos->data[ftmp] = x_QRS->data[mm] + X_max->data[absb];
    i7 = T_Location_cur->size[0] * T_Location_cur->size[1];
    T_Location_cur->size[0] = 1;
    T_Location_cur->size[1] = T_position_pos->size[1];
    emxEnsureCapacity((emxArray__common *)T_Location_cur, i7, (int)sizeof(double));
    cdiff = T_position_pos->size[0] * T_position_pos->size[1];
    for (i7 = 0; i7 < cdiff; i7++) {
      T_Location_cur->data[i7] = T_position_pos->data[i7] + x_start;
    }

    mm++;
  }

  emxFree_real_T(&c_Win_Gaussian);
  emxFree_real_T(&X_max);
  emxFree_real_T(&T_detector_win);
  emxFree_real_T(&Win_Gaussian);
  emxFree_real_T(&T_detector_win_ori);
  emxFree_real_T(&T_position_pos);

  /*  plot(P_detector_win);hold on; plot(T_detector_win,'g');hold off */
  /*  If the location is equal to -1, it means none of the wave is detected */
  i7 = P_Location_cur->size[0] * P_Location_cur->size[1];
  P_Location_cur->size[0] = 1;
  P_Location_cur->size[1] = 1;
  emxEnsureCapacity((emxArray__common *)P_Location_cur, i7, (int)sizeof(double));
  P_Location_cur->data[0] = -1.0;
  if (((T_Location_cur->size[0] == 0) || (T_Location_cur->size[1] == 0)) == 1) {
    i7 = T_Location_cur->size[0] * T_Location_cur->size[1];
    T_Location_cur->size[0] = 1;
    T_Location_cur->size[1] = 1;
    emxEnsureCapacity((emxArray__common *)T_Location_cur, i7, (int)sizeof(double));
    T_Location_cur->data[0] = -1.0;
  }
}

/*
 * File trailer for T_detection.c
 *
 * [EOF]
 */
