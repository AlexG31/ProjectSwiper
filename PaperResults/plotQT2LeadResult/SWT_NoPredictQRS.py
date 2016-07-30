#encoding:utf-8
"""
Do SWT without QRS region.
Author : Gaopengfei
Date: 2016.7.17
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

class SWT_NoPredictQRS:
    def __init__(self,rawsig,MarkList):
        # Input Format:
        # MarkList should be in the format:
        # [(pos,label),(pos,label),...]
        # 
        # rawsig is a single lead ECG signal
        self.QTdb = QTloader()
        self.rawsig = rawsig
        self.MarkList = MarkList
    def getNonQRSsig(self):
        # QRS width threshold
        QRS_width_threshold = 180

        rawsig = self.rawsig
        expert_marklist = self.MarkList
        
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
                    # print 'Adding:',pos,next_pos
                    # Flattern the signal
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

    def swt(self,wavelet = 'db6',MaxLevel = 9):
        # 
        rawsig = self.getNonQRSsig()
        rawsig = self.crop_data_for_swt(rawsig)

        coeflist = pywt.swt(rawsig,wavelet,MaxLevel)
        cAlist,cDlist = zip(*coeflist)
        self.cAlist = cAlist
        self.cDlist = cDlist


def Convert2ExpertFormat(ResultDict):
    # Result Dict Format:
    # {'P'=[1,2,3,...],
    #  'T'=[2,3,5,...],
    # }
    # ExpertFormat:
    # [(pos,label),(pos,label),...]
    ExpertList = []
    for label,poslist in ResultDict.iteritems():
        if len(poslist) > 0:
            ExpertList.extend(zip(poslist,[label,]*len(poslist)))
    ExpertList.sort(key = lambda x:x[0])
    # pos must be integers.
    ExpertList = map(lambda x:[int(x[0]),x[1]],ExpertList)
    return ExpertList
def TEST_PredictionQRS():
    recname = 'sel873'
    GroupResultFolder = os.path.join(curfolderpath,'MultiLead4','GroupRound1')
    QTdb = QTloader()
    rawsig = QTdb.load(recname)
    rawsig = rawsig['sig']
    with open(os.path.join(GroupResultFolder,'{}.json'.format(recname)),'r') as fin:
        RawResultDict = json.load(fin)
        LeadResult = RawResultDict['LeadResult']
        MarkDict = LeadResult[0]
        MarkList = Convert2ExpertFormat(MarkDict)

        # Display with 2 subplots.
        swt = SWT_NoPredictQRS(rawsig,MarkList)
        swt.swt()

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
    
def TEST_ExpertQRS():
    recname = 'sel103'
    QTdb = QTloader()
    rawsig = QTdb.load(recname)
    rawsig = rawsig['sig']
    MarkList = QTdb.getExpert(recname)

    swt = SWT_NoPredictQRS(rawsig,MarkList)
    swt.swt()

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


if __name__ == '__main__':
    TEST_PredictionQRS()
