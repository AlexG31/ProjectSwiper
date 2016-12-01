#encoding:utf-8
"""
ECG classification Module
Author : Gaopengfei
"""
import os
import sys
import json
import math
import pickle
import random
import time
import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = curfolderpath;
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
import RFclassifier.evaluation as ecgEval
import RFclassifier.ECGRF as ECGRF 
import WTdenoise.wtfeature as wtf


def TestingAndSaveResult():
    sel1213 = conf['sel1213']
    time0 = time.time()
    rf = ECGRF.ECGrf()
    rf.training(sel1213[0:1])
    time1 = time.time()
    print 'Training time:',time1-time0
    ## test
    rf.testmdl(reclist = sel1213[0:1])
def leaveonetest():
    sel1213 = conf['sel1213']
    rf = ECGRF.ECGrf()

    # reapeat test
    for i in range(0,len(sel1213)):
        print '====Test Index {} ===='.format(i)
        time0 = time.time()
        traininglist = [x for x in sel1213 \
                if x != sel1213[i]]
        rf.training(traininglist)
        time1 = time.time()
        print 'Training time:',time1-time0
        ## test
        print 'testing:',sel1213[i]
        rf.testmdl(reclist = [sel1213[i],])
    
def testEval(picklefilename):
    with open(picklefilename,'r') as fin:
        Results = pickle.load(fin)
    rfobj = ECGRF.ECGrf()
    fResults = rfobj.resfilter(Results)
    # show filtered results & raw results
    #for recname , recRes in Results:
    #rfobj.plotresult(Results[2],showExpertLabel = True)
    #rfobj.plotresult(fResults[2],figureID = 2,showExpertLabel = True)

    # Evaluate prediction result statistics
    #
    ECGstats = ecgEval.ECGstatistics(fResults[0:2])
    ECGstats.eval(debug = True)
    ECGstats.dispstat0()
    ECGstats.plotevalresofrec(fResults[1][0],Results)

def testconf():
    brange = conf['labelblankrange']
    print brange
    print 'keys:{}'.format(brange.keys())
    for kk in brange.keys():
        print '{}:{}'.format(kk,brange[kk])
        print brange[kk][0]
        print brange[kk][0][1] - brange[kk][0][0]

def checkQTrec():
    sel1213 = conf['sel1213']
    QTloader = QTdb.QTloader()
    for recname in sel1213:
        QTloader.plotrec(recname)
        #raw_input('waiting...')

def checkWT():
    sel1213 = conf['sel1213']
    QTloader = QTdb.QTloader()
    wtfobj = wtf.WTfeature()

    for recname in sel1213:
        sig = QTloader.load(recname)
        wtfobj.plot_wtcoefs(\
                sig['sig'],\
                waveletobj = wtfobj.gswt_wavelet(),\
                figureID = 2)

        #raw_input('waiting...')
    
if __name__ == '__main__':
    #checkQTrec()
    #testconf()
    checkWT()

