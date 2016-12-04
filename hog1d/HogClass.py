#encoding:utf8
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

curfolderpath = os.path.dirname(os.path.realpath(__file__))
project_home_path = os.path.dirname(curfolderpath)
sys.path.append(project_home_path)

# Import packages in this project
from QTdata.loadQTdata import QTloader

class HogClass(object):
    def __init__(self, segment_len = 100):
        '''
        Inputs:
            segment_len: segment_length of each cell.
        '''
        self.segment_len = segment_len

    def ComputeHog(self, sig_in, diff_step = 4, debug_plot = False):
        '''Compute 1-dim hog.'''
        segment_len = self.segment_len
        
        len_sig = len(sig_in)

        # Hog array
        hog_arr = list()

        # Baseline array
        h0_arr = list()

        cur_ind = 0
        while cur_ind < len_sig:
            right_ind = min(len_sig - 1, cur_ind + segment_len - 1)

            # Compute diffs in this segment
            diff_arr = [sig_in[di + diff_step] - sig_in[di]
                            for di in xrange(cur_ind, right_ind - diff_step + 1)]
            hog_arr.append(diff_arr)
            h0_arr.append(np.mean(sig_in[cur_ind:right_ind+1]))
            # plt.hist(diff_arr)
            # plt.show()
            
            cur_ind += segment_len

        # Show Hog
        if debug_plot == True :
            self.VisualizeHogArray(hog_arr, h0_arr = h0_arr)

        return hog_arr

    def VisualizeHogArray(self, hog_arr, h0_arr = None):
        '''Visualize hog array of k.'''
        segment_len = self.segment_len
        h0 = segment_len / 2
        if h0_arr is None:
            h0_arr = [h0,] * len(hog_arr)

        h0_arr = np.array(h0_arr) * 10.0

        cur_ind = 0
        len_hog_arr = len(hog_arr)

        # Plot
        plt.figure(2)
        for hog_i in xrange(0, len_hog_arr):
            right_ind = cur_ind + segment_len - 1

            # Plot hog direction line
            alpha = 1.0 / len(hog_arr[hog_i])
            x1 = cur_ind
            x2 = right_ind
            for k_val in hog_arr[hog_i]:
                y1 = h0_arr[hog_i] - k_val * segment_len / 2.0
                y2 = h0_arr[hog_i] + k_val * segment_len / 2.0
                plt.plot([x1, x2], [y1, y2], alpha = alpha, lw = 2,
                            color = 'black')

            # update cur_ind
            cur_ind += segment_len

        # plt.show()
            
        
        
        
def Test():
    '''Test function for HOG1D class.'''
    qt = QTloader()
    sig_struct  = qt.load('sel30')
    sig = sig_struct['sig']
    sig = sig[0:500]

    # Plot ECG signal
    # plt.figure(1)
    # plt.plot(sig)
    # plt.show()

    # HOG 1d class
    hoger = HOG1D(segment_len = 15)
    hoger.ComputeHog(sig)

    plt.figure(2)
    plt.plot(np.array(sig) * 10)
    plt.grid(True)
    plt.show()

    
            
            


