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
curfolderpath = os.path.dirname(curfolderpath)
projhomepath = curfolderpath;
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
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime
from MITdb.MITdbLoader import MITdbLoader


def TestingAndSaveResult():
    sel1213 = conf['sel1213']
    time0 = time.time()
    rf = ECGRF.ECGrf()
    rf.training(sel1213[0:1])
    time1 = time.time()
    print 'Training time:',time1-time0
    ## test
    rf.testmdl(reclist = sel1213[0:1])
def backup_configure_file(saveresultpath):
    shutil.copy(os.path.join(projhomepath,'ECGconf.json'),saveresultpath)
    
def testonMITdb(rfClass):
    pass
    mitdb = MITdbLoader(os.path.join(projhomepath,'MITdb','pydata'))
    # get MITdb record list
    reclist = mitdb.getRecIDList()
    pdb.set_trace()
def TestAllQTdata(saveresultpath):
    # Leave Ntest out of 30 records to test
    #

    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    selrecords= QTreclist
    rf = ECGRF.ECGrf()
    rf.useParallelTest = False
    rf.TestRange = 'All'

    # ================
    # evaluate time cost for each stage
    # ================
    rtimer = RunAndTime()
    
    # clear debug logger
    ECGRF.debugLogger.clear()
    # display the time left to finish program
    one_round_time_cost = []

    # ====================
    # Training
    # ====================
    ECGRF.debugLogger.dump('\n====Test Start ====\n')


    time0 = time.time()
    # training the rf classifier with reclist
    #
    # dump to debug logger
    rf.training(selrecords)
    # timing
    time1 = time.time()
    print 'Total Training time:',time1-time0
    ECGRF.debugLogger.dump('Total Training time: {:.2f} s\n'.format(time1-time0))

    ## test
    testinglist = selrecords
    print '\n>>Testing:',testinglist
    ECGRF.debugLogger.dump('\n======\n\nTest Set :{}'.format(selrecords))
    testonMITdb(rf)
    #rf.testmdl(reclist = selrecords,TestResultFileName = os.path.join(saveresultpath,'TestResult.out'))
    # save trained mdl
    with open(os.path.join(saveresultpath,'trained_model'),'w') as fout:
        pickle.dump(rf.mdl,fout)
        ECGRF.debugLogger.dump('\n\n====\ntrained model saved in {}\n'.format(saveresultpath))
        
if __name__ == '__main__':

    saveresultpath = os.path.join(curfolderpath,'TestResult','pc','r3')
    # refresh random select feature json file
    ECGRF.ECGrf.RefreshRandomFeatureJsonFile()

    #backup configuration file
    backup_configure_file(saveresultpath)

    TestAllQTdata(saveresultpath)

