#encoding:utf-8
"""
ECG classification Module
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
import shutil
import numpy as np
import pdb
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import QTdata.loadQTdata as QTdb
import RFclassifier.evaluation as ecgEval
import RFclassifier.ECGRF as ECGRF 
from RFclassifier.ECGRF import timing_for
from QTdata.loadQTdata import QTloader 


def GetQTRegion(recID):
    qt = QTloader()
    sigStruct = qt.load(recID)
    N_sig = len(sigStruct['sig'])
    # get expert labels
    explabels = qt.getexpertlabeltuple(recID)
    Regions = []
    Span_Len = 300
    for pos,label in explabels:
        L = max(0,pos - Span_Len)
        R = min(N_sig-1,pos+Span_Len)
        Regions.append((L,R))
    # merge Regions
    Regions.sort(key = lambda x: x[0])
    curRange = None
    merged_Ranges = []
    for region in Regions:
        if curRange is None:
            curRange = list(region)
        elif region[0]>=curRange[0] and region[0]<=curRange[1]:
            curRange[1] = max(curRange[1],region[1])
        else:
            merged_Ranges.append(curRange)
            curRange = list(region)
    if curRange is not None:
        merged_Ranges.append(curRange)
    ## debug
    #for ind in xrange(0,10):
        #print Regions[ind]
    #for ind in xrange(0,10):
        #print merged_Ranges[ind]
    return merged_Ranges
    

        
if __name__ == '__main__':

    SaveFolder = r'F:\LabGit\ECG_RSWT\TestSchemes\QT_TestRegions'
    qt = QTloader()
    QTreclist = qt.getreclist()
    for recID in QTreclist:
        print 'loading regions for ',recID
        Regions = GetQTRegion(recID)
        with open(os.path.join(SaveFolder,'{}_TestRegions.pkl'.format(recID)),'w') as fout:
            print 'dumping pickle file...'
            pickle.dump(Regions,fout)
