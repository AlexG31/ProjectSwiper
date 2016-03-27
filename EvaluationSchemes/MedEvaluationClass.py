#encoding:utf-8
"""
ECG Medical Evaluation Module
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import math
import pickle
import random
import time
import pdb

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
print 'projhomepath:',projhomepath
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import QTdata.loadQTdata as QTdb
from RFclassifier.evaluation import ECGstatistics
import RFclassifier.ECGRF as ECGRF 


class MedEvaluation:
    def __init__(self,testresultlist):
        self.testresultlist = testresultlist
    def RRhistogram(self):
        # get RR interval histogram data & plot the histogram
        # filtering
        self.resultfilter()
        Rlist,Rlabellist = zip(*filter(lambda x:x[1]=='Ronset',self.testresultlist))
        RRintervalList = []
        for ind,Rpos in enumerate(Rlist):
            if ind>0:
                RRintervalList.append(Rlist[ind] - Rlist[ind-1])
        # plot result
        plt.figure(1)
        plt.hist(RRintervalList,50)
        plt.show()    
        pdb.set_trace()
    def resultfilter(self):
        #
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        group_min_thres = 1

        recres = self.testresultlist
        # filtered test result
        frecres = []
        # in var
        prev_label = None
        posGroup = []
        #----------------------
        # [pos,label] in recres
        #----------------------
        for pos,label in recres:
            if prev_label is not None:
                if label != prev_label:
                    frecres.append((prev_label,posGroup))
                    posGroup = []
                
            prev_label = label
            posGroup.append(pos)
        
        # last one
        if len(posGroup)>0:
            frecres.append((prev_label,posGroup))
        # [(label,[poslist])]
        frecres = [x for x in frecres if len(x[1]) > group_min_thres]
        frecres = [(int(np.mean(x[1])),x[0]) \
                for x in frecres]
                
        # change self record result
        self.testresultlist = frecres
        return frecres



