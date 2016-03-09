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
import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
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


def TestingAndSaveResult():
    sel1213 = conf['sel1213']
    time0 = time.time()
    rf = ECGRF.ECGrf()
    rf.training(sel1213[0:1])
    time1 = time.time()
    print 'Training time:',time1-time0
    ## test
    rf.testmdl(reclist = sel1213[0:1])
def leaveNtest(saveresultpath,Ntest,StartFileIndex = 0,TestRoundNum = 30):
    # Leave Ntest out of 30 records to test
    #

    # refresh random select feature json file
    ECGRF.ECGrf.RefreshRandomFeatureJsonFile()
    
    selrecords= conf['sel0116']
    rf = ECGRF.ECGrf()
    
    # clear debug logger
    ECGRF.debugLogger.clear()
    # display the time left to finish program
    one_round_time_cost = []

    # reapeat test
    for i in range(StartFileIndex,TestRoundNum):
        # round start time
        time_round_start = time.time()
        print '====Test Index {} ===='.format(i)
        ECGRF.debugLogger.dump('\n====Test Index {} ====\n'.format(i))

        # get N random selected test records
        indexlist = range(0,len(selrecords))
        random.shuffle(indexlist)
        testindexlist = indexlist[0:Ntest]
        # training set
        trainingindexset = set(indexlist)
        testingindexset = set(testindexlist)
        trainingindexset -= testingindexset

        time0 = time.time()
        # training the rf classifier with reclist
        #
        traininglist = [ selrecords[x] for x in trainingindexset]
        # dump to debug logger
        ECGRF.debugLogger.dump('\n======\nTrainingset:{}\nTrainingRecords:{}\n'.format(trainingindexset,traininglist))
        rf.training(traininglist)
        # timing
        time1 = time.time()
        print 'Total Training time:',time1-time0
        ECGRF.debugLogger.dump('Total Training time: {:.2f} s\n'.format(time1-time0))

        ## test
        testinglist = [selrecords[x] for x in testingindexset]
        print '\n>>Testing:',testinglist
        ECGRF.debugLogger.dump('\n======\nTestingindexs:{}\nTestingRecords:{}\n'.format(testingindexset,testinglist))
        rf.testmdl(reclist = testinglist,TestResultFileName = os.path.join(saveresultpath,'hand{}.out'.format(i)))
        # round end time
        time_round_end = time.time()
        one_round_time_cost.append(time_round_end - time_round_start)
        time_cost_per_round = np.nanmean(one_round_time_cost)
        if time_cost_per_round is not None:
            debug_timeleft_info = '\n[Time left:{:.1f}s({:.1f}min)]\n'.format((TestRoundNum-i-1)*time_cost_per_round,(TestRoundNum-i-1)*time_cost_per_round/60.0)
            print debug_timeleft_info
            ECGRF.debugLogger.dump(debug_timeleft_info)

def leaveonetest(saveresultpath,StartFileIndex = 0):
    #
    # test speed version of LOOT
    #

    # refresh random select feature json file
    #
    ECGRF.ECGrf.RefreshRandomFeatureJsonFile()
    
    sel1213 = conf['sel0116']
    rf = ECGRF.ECGrf()
    
    ECGRF.debugLogger.clear()

    # display the time left to finish program
    one_round_time_cost = []
    # reapeat test
    for i in range(StartFileIndex,len(sel1213)):
        # round start time
        time_round_start = time.time()
        
        print '====Test Index {} ===='.format(i)
        ECGRF.debugLogger.dump('\n====Test Index {} ====\n'.format(i))

        time0 = time.time()
        # training the rf classifier with reclist
        #
        traininglist = [x for x in sel1213 \
                if x != sel1213[i]]
        rf.training(traininglist)
        # timing
        time1 = time.time()
        print 'Total Training time:',time1-time0
        ECGRF.debugLogger.dump(\
                    'Total Training time: {:.2f} s\n'.format(time1-time0))

        ## test
        print 'testing:',sel1213[i]
        rf.testmdl(reclist = [sel1213[i],],\
                TestResultFileName = \
                    os.path.join(saveresultpath,'hand{}.out'.format(i)))
        # round end time
        time_round_end = time.time()
        one_round_time_cost.append(time_round_end - time_round_start)
        time_cost_per_round = np.nanmean(one_round_time_cost)
        if time_cost_per_round is not None:
            print '\n[Time left:{:.1f}s({:.1f}min)]'.format((len(sel1213)-i-1)*time_cost_per_round,(len(sel1213)-i-1)*time_cost_per_round/60.0)

    
def test_classifier_run():
    # =======================================
    # refresh random select feature json file
    # =======================================
    ECGRF.ECGrf.RefreshRandomFeatureJsonFile()

    # collect test record list
    sel1213 = conf['sel1213']
    target_index = 11
    # init rf classifier
    rf = ECGRF.ECGrf()
    # traning
    traininglist = [x for x in sel1213 \
            if x != sel1213[target_index]]
    traininglist = traininglist[0:5]
    # prompt
    print '>>> Training {}'.format(traininglist)
    rf.training(traininglist)
    print '>>> Training finished.'
    # testing
    print 'testing:',sel1213[target_index]
    rf.testmdl(\
            reclist = [sel1213[target_index],],\
            TestResultFileName = \
                os.path.join(\
                        projhomepath,\
                        'tmp',\
                        'tmp.out'.format(target_index)))

if __name__ == '__main__':

    saveresultpath = os.path.join(curfolderpath,'TestResult','pc','r1')
    #leaveonetest(saveresultpath,StartFileIndex = 0)
    leaveNtest(saveresultpath,3,StartFileIndex = 0,TestRoundNum = 100)
    #test_classifier_run()

