#encoding:utf-8
"""
Test CWT coefficients
Author : Gaopengfei
Date: 2016.6.23
"""
import os
import sys
import json
import math
import pickle
import random
import pywt
import time
import glob
import pdb
from multiprocessing import Pool

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import pi, r_
from scipy import optimize

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
sys.path.append(projhomepath)
# configure file
# conf is a dict containing keys
# my project components
from QTdata.loadQTdata import QTloader
from EvaluationSchemes.csvwriter import CSVwriter


sys.path.append(curfolderpath)
from Evaluation2Leads import Evaluation2Leads

class NonQRS_SWT:
    def __init__(self):
        self.QTdb = QTloader()
    def getNonQRSsig(self,recname):
        # QRS width threshold
        QRS_width_threshold = 180

        sig_struct = self.QTdb.load(recname)
        rawsig = sig_struct['sig']

        expert_marklist = self.QTdb.getexpertlabeltuple(recname)
        
        # Use QRS region to flattern the signal
        expert_marklist = filter(lambda x:'R' in x[1] and len(x[1])>1,expert_marklist)
        # Get QRS region
        expert_marklist.sort(key=lambda x:x[0])
        QRS_regionlist = []
        N_Rlist = len(expert_marklist)
        for ind in xrange(0,N_Rlist-1):
            pos, label = expert_marklist[ind]
            # last one: no match pair
            if ind == N_Rlist - 1:
                break
            elif label != 'Ronset':
                continue
            # get next label
            next_pos,next_label = expert_marklist[ind+1]
            if next_label == 'Roffset':
                if next_pos - pos >=QRS_width_threshold:
                    print 'Warning: no matching Roffset found!'
                else:
                    QRS_regionlist.append([pos,next_pos])
                    print 'Adding:',pos,next_pos
                    # flattern the signal
                    amp_start = rawsig[pos]
                    amp_end = rawsig[next_pos]
                    flat_segment = map(lambda x:amp_start+float(x)*(amp_end-amp_start)/(next_pos-pos),xrange(0,next_pos-pos))
                    for segment_index in xrange(pos,next_pos):
                        rawsig[segment_index] = flat_segment[segment_index-pos]
        return rawsig

    def crop_data_for_swt(self,rawsig):
        # crop rawsig
        base2 = 1
        N_data = len(rawsig)
        if len(rawsig)<=1:
            raise Exception('len(rawsig)={},not enough for swt!',len(rawsig))
        crop_len = base2
        while base2<N_data:
            if base2*2>=N_data:
                crop_len = base2*2
                break
            base2*=2
        # pad zeros
        if N_data< crop_len:
            rawsig += [rawsig[-1],]*(crop_len-N_data)
        return rawsig

    def swt(self,recname,wavelet = 'db6',MaxLevel = 9):
        # 
        rawsig = self.getNonQRSsig(recname)
        rawsig = self.crop_data_for_swt(rawsig)

        coeflist = pywt.swt(rawsig,wavelet,MaxLevel)
        cAlist,cDlist = zip(*coeflist)
        self.cAlist = cAlist
        self.cDlist = cDlist


if __name__ == '__main__':
    recname = 'sel103'
    swt = NonQRS_SWT()
    rawsig = swt.getNonQRSsig(recname)
    swt.swt(recname)

    # cDlist
    wtlist = swt.cDlist[-4]

    plt.figure(1)
    # plot Non QRS ECG & SWT
    plt.subplot(211)
    plt.plot(rawsig)
    plt.plot(wtlist)
    plt.grid(True)
    # plot Original ECG
    rawsig = swt.QTdb.load(recname)
    rawsig = rawsig['sig']
    rawsig = swt.crop_data_for_swt(rawsig)
    coeflist = pywt.swt(rawsig,'db6',9)
    cAlist,cDlist = zip(*coeflist)
    wtlist = cDlist[-4]
    
    
    plt.subplot(212)
    plt.plot(rawsig)
    plt.plot(wtlist)
    plt.grid(True)
    plt.show()


