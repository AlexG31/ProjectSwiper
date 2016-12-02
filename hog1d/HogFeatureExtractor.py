#encoding:utf-8
"""
Extrace Hog1d feature
Author : Gaopengfei
"""
import os
import sys
import json
import math
import pickle
import pywt
import bisect
import logging
import random
import time
import pdb

import numpy as np
import matplotlib.pyplot as plt

# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = curfolderpath
projhomepath = os.path.dirname(projhomepath)

# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

from QTdata.loadQTdata import QTloader

# Global logger
log = logging.getLogger()

# HOG 1D Feature Extractor for QT database
class HogFeatureExtractor(object):
    def __init__(self, target_label = 'P'):
        '''Hog 1D feature extractor.
        Inputs:
            target_label: label to detect. eg. 'T[(onset)|(offset)]{0,1}', 'P'
        '''
        self.qt = QTloader()

        # Training Samples.
        self.signal_segments = []
        self.target_biases = []

        self.target_label = target_label

    def GetTrainingSamples(self, sig_in, expert_labels):
        '''Form Hog1D feature.'''
        # Make sure the x indexes are in ascending order.
        expert_labels.sort(key = lambda x: x[0])

        for expert_index in xrange(0, len(expert_labels)):
            pos, label = expert_labels[expert_index]
            if label != 'R':
                continue

            # Cut out the ECG segment that end with current R peak.
            signal_segment, target_bias = self.CutSegment(sig_in,
                                                     expert_labels,
                                                     expert_index,
                                                     fixed_window_length = 250)
            self.signal_segments.append(signal_segment)
            self.target_biases.append(target_bias)

            plt.plot(signal_segment)
            plt.plot(target_bias, np.mean(signal_segment), marker = 'd', markersize = 12)
            plt.show()

    def Train(self):
        '''Training with Qt data.'''
        reclist = self.qt.getreclist()
        for rec_name in reclist:
            sig_struct = self.qt.load(rec_name)
            raw_signal = sig_struct['sig']
            
            # Expert samples from Qt database
            expert_labels = self.qt.getExpert(rec_name)

            # Collect training vectors
            self.GetTrainingSamples(raw_signal, expert_labels)
            
            break
    def CutSegment(self, sig_in, expert_labels, expert_index,
                   fixed_window_length = 250 * 1):
        '''Get equal length signal_segments ends at expert_index.
        Inputs:
            sig_in: Input ECG signal.
            expert_labels: Annotation list of form [(pos, label), ...]
            expert_index: The index of the element in expert_labels that
                has label 'R'.
            fixed_window_length : return signal's length
        Returns:
            signal_segment: Cropped signal segment.
            target_bias: The bias respect to the expert_index's position.
        '''
        current_R_pos = expert_labels[expert_index][0]
        ecg_segment = np.zeros(fixed_window_length)
        left_bound = max(0, current_R_pos - fixed_window_length + 1)
        len_ecg_data = current_R_pos - left_bound + 1
        ecg_segment[fixed_window_length - len_ecg_data:] = np.array(
                                        sig_in[left_bound: current_R_pos + 1])
        
        
        previous_R_pos = None
        previous_P_pos = None
        for ind in xrange(expert_index - 1, -1, -1):
            cur_pos, cur_label = expert_labels[ind]
            if cur_label == 'R' and previous_R_pos is None:
                previous_R_pos = cur_pos
            if cur_label == 'P' and previous_P_pos is None:
                previous_P_pos = cur_pos
        
        # Eliminate previous R wave
        #
        # plt.plot(ecg_segment)
        # if previous_R_pos is not None:
            # local_previous_R_pos = previous_R_pos - current_R_pos + fixed_window_length - 1
            # if local_previous_R_pos >= 0:
                # plt.plot(fixed_window_length - (current_R_pos - previous_R_pos), np.mean(ecg_segment), marker = 'd', markersize = 12)
        # plt.show()

        if previous_P_pos is not None:
            local_previous_P_pos = previous_P_pos - current_R_pos + fixed_window_length - 1
        else :
            local_previous_P_pos = None
        
        return ecg_segment, local_previous_P_pos
        


if __name__ == '__main__':

    hog = HogFeatureExtractor()
    hog.Train()
