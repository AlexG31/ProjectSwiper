#encoding:utf-8
"""
ECG classification Module
Author : Gaopengfei
"""
import os
import sys
sys.stdout = open('test.txt','w')
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
from RFclassifier.ECGRF import timing_for
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime


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
def backupobj(obj,savefilename):
    with open(savefilename,'w') as fout:
        pickle.dump(obj,fout)
    
def TestAllQTdata(saveresultpath):
    # Leave Ntest out of 30 records to test
    #
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    print 'Totoal QT record number:{}'.format(len(QTreclist))
    ## Training record list
    testinglist = conf["selQTall0_test_set"]
    traininglist = list(set(QTreclist) - set(testinglist))

    rf = ECGRF.ECGrf()
    # Multi Process
    rf.useParallelTest = True 
    rf.TestRange = 'All'

    # clear debug logger
    ECGRF.debugLogger.clear()
    # ====================
    # Training
    # ====================
    ECGRF.debugLogger.dump('\n====Test Start ====\n')

    # training the rf classifier with reclist
    #
    # dump to debug logger
    time_cost_output = []
    timing_for(rf.training,[traininglist,],prompt = 'Total Training time:',time_cost_output = time_cost_output)
    ECGRF.debugLogger.dump('Total Training time: {:.2f} s\n'.format(time_cost_output[-1]))
    # save trained mdl
    backupobj(rf.mdl,os.path.join(saveresultpath,'trained_model.mdl'))

    ## test
    print '\n>>Testing:',testinglist
    ECGRF.debugLogger.dump('\n======\n\nTest Set :{}'.format(testinglist))
    rf.testrecords(saveresultpath,reclist = testinglist)


    
if __name__ == '__main__':

    saveresultpath = projhomepath
    Result_path_conf = conf['ResultFolder_Relative']
    for folder in Result_path_conf:
        saveresultpath = os.path.join(saveresultpath,folder)
    # create result folder if not exist
    #if os.path.exists(saveresultpath) == False:
    os.mkdir(saveresultpath)
    # refresh random select feature json file and backup
    ECGRF.ECGrf.RefreshRandomFeatureJsonFile(copyTo = os.path.join(saveresultpath,'rand_relations.json'))

    #backup configuration file
    backup_configure_file(saveresultpath)

    TestAllQTdata(saveresultpath)

    # back up processing debug output log
    shutil.copy(os.path.join(projhomepath,'classification_process.log'),saveresultpath)
