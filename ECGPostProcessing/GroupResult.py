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

class GroupClassificationResult:
    def __init__(self,recres):
        self.recres = recres
        pass
    def resultfilter(self,recres = None):
        # 根据不同label的边界来分组，应该根据位置来分组！
        #
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        # default parameter
        if recres is None:
            recres = self.recres
        group_min_thres = 1

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
                
        return frecres



