#encoding:utf-8
"""
ECG Grouping Evaluation module
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import bisect
import math
import pickle
import random
import time
import pdb
import pywt

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
sys.path.append(curfolderpath)
#
# my project components

from Group2LeadsResults import GroupResult2Leads
from Evaluation2Leads import Evaluation2Leads


def RunGroup(RoundInd):
    #RoundInd = 3
    # load the results
    RoundFolder = r'F:\LabGit\ECG_RSWT\TestResult\paper\MultiRound2'
    ResultFolder = os.path.join(RoundFolder,'Round{}'.format(RoundInd))
    SaveFolder = os.path.join(curfolderpath,'MultiLead2','GroupRound{}'.format(RoundInd))
    os.mkdir(SaveFolder)

    # each result file
    resfiles = glob.glob(os.path.join(ResultFolder,'result_*'))
    for resfilepath in resfiles:
        with open(resfilepath,'r') as fin:
            prdRes = json.load(fin)
        recname = prdRes[0][0]
        reslist1= prdRes[0][1]
        reslist2= prdRes[1][1]

        # ------------------------------------------------------
        # Group Results
        eva = GroupResult2Leads(recname,reslist1,reslist2)
        resDict = eva.getResultDict(debug = False)
        
        # ------------------------------------------------------
        # save to Group Result
        GroupDict = dict(recname = recname,LeadResult=resDict)

        # save to Round folder 
        jsonfilepath = os.path.join(SaveFolder,recname+'.json')
        with open(jsonfilepath,'w') as fout:
            json.dump(GroupDict,fout,indent = 4,sort_keys = True)

        # debug
        print 'record name:',recname
def RunEval(RoundInd):
    GroupSaveFolder = os.path.join(curfolderpath,'MultiLead2','GroupRound{}'.format(RoundInd))
    resultfilelist = glob.glob(os.path.join(GroupSaveFolder,'*.json'))
    evalinfopath = os.path.join(curfolderpath,'MultiLead2','EvalInfoRound{}'.format(RoundInd))
    os.mkdir(evalinfopath)

    # print result files
    for ind, fp in enumerate(resultfilelist):
        print '[{}]'.format(ind),'fp:',fp

    ErrDict = dict()
    ErrData = dict()

    for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
        ErrData[label] = dict()
        ErrDict[label] = dict()
        errList = []
        FNcnt = 0

        for file_ind in xrange(0,len(resultfilelist)):
            # progress info
            print 'label:',label
            print 'file_ind',file_ind

            eva= Evaluation2Leads()
            eva.loadlabellist(resultfilelist[file_ind],label)
            eva.evaluate(label)

            # total error
            errList.extend(eva.errList)
            FN = eva.getFNlist()
            FNcnt += FN

            # -----------------
            # error statistics

            #ErrDict[label]['mean'] = np.mean(eva.errList)
            #ErrDict[label]['std'] = np.std(eva.errList)
            #ErrDict[label]['FN'] = eva.getFNlist()

            # debug
            #print '--'
            #print 'record: {}'.format(os.path.split(resultfilelist[file_ind])[-1])
            #print 'Error Dict:','label:',label
            #print ErrDict[label]

            # ======
            #eva.plot_evaluation_result()
            #pdb.set_trace()
        ErrData[label]['errList'] = errList
        ErrData[label]['FN'] = FNcnt

        ErrDict[label]['mean'] = np.mean(errList)
        ErrDict[label]['std'] = np.std(errList)
        ErrDict[label]['FN'] = FNcnt

    print '-'*10
    print 'ErrDict'
    print ErrDict

    # write to json
    with open(os.path.join(evalinfopath,'ErrData.json'),'w') as fout:
        json.dump(ErrData,fout,indent = 4,sort_keys = True)
        print '>>Dumped to json file: ''ErrData.json''.'
    # error statistics
    with open(os.path.join(evalinfopath,'ErrStat.json'),'w') as fout:
        json.dump(ErrDict,fout,indent = 4,sort_keys = True)
        print '>>Dumped to json file: ''ErrStat.json''.'


if __name__ == '__main__':
    for RoundInd in xrange(1,13):
        RunGroup(RoundInd)
        RunEval(RoundInd)

