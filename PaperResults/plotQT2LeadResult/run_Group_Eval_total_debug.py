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
    RoundFolder = r'F:\LabGit\ECG_RSWT\TestResult\paper\MultiRound4'
    ResultFolder = os.path.join(RoundFolder,'Round{}'.format(RoundInd))
    SaveFolder = os.path.join(curfolderpath,'MultiLead4','GroupRound{}'.format(RoundInd))
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


class TotalRoundEvaluation:
    def __init__(self):
        self.total_error_diction =  dict()
        self.error_list_for_label = dict()
        self.false_negtive_list = dict()
        self.false_positive_list = dict()
        self.sensitivity = dict()
        self.Pplus = dict()
        # initialize for error_list_for_label& false_negtive_list
        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            self.error_list_for_label[label] = []
            self.false_negtive_list[label] = 0
            self.false_positive_list[label] = 0
            self.sensitivity[label] = 0
            self.Pplus[label] = 0

    def RunEval(self,RoundInd):
        GroupResultFolder = os.path.join(curfolderpath,'MultiLead4','GroupRound{}'.format(RoundInd))
        resultfilelist = glob.glob(os.path.join(GroupResultFolder,'*.json'))

        ## print result files
        #for ind, fp in enumerate(resultfilelist):
            #print '[{}]'.format(ind),'fp:',fp

        ErrDict = dict()
        ErrData = dict()

        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            ErrData[label] = dict()
            ErrDict[label] = dict()
            errList = []
            FNcnt = 0
            FPcnt = 0

            for file_ind in xrange(0,len(resultfilelist)):
                # progress info
                #print 'label:',label
                #print 'file_ind',file_ind

                eva= Evaluation2Leads()
                eva.loadlabellist(resultfilelist[file_ind],label, supress_warning = True)
                eva.evaluate(label)

                # total error
                errList.extend(eva.errList)
                FN = eva.getFNlist()
                FP = eva.getFPlist()

                FNcnt += FN
                FPcnt += FP
            self.error_list_for_label[label].extend(errList)
            self.false_negtive_list[label] += FNcnt
            self.false_positive_list[label] += FPcnt

    def ReadEvaluationFolder(self,RoundInd):
        evalinfopath = os.path.join(curfolderpath,'MultiLead4','EvalInfoRound{}'.format(RoundInd))


        #ErrData[label]['errList'] = errList
        #ErrData[label]['FN'] = FNcnt


        # write to json
        with open(os.path.join(evalinfopath,'ErrData.json'),'r') as fin:
            ErrData = json.load(fin)
        # add to total error list & False Negtive List
        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            self.error_list_for_label[label].extend(ErrData[label]['errList'])
            self.false_negtive_list[label] += ErrData[label]['FN']
            self.false_positive_list[label] += ErrData[label]['FP']

            #print 'label:',label,self.false_positive_list[label]
            #pdb.set_trace()

    def get_mean_and_std(self):
        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            self.total_error_diction[label] = dict()
            self.total_error_diction[label]['mean'] = np.mean(self.error_list_for_label[label])
            self.total_error_diction[label]['std'] = np.std(self.error_list_for_label[label])
            # debug
            print 'for label {}:'.format(label)
            print 'mean = {}, std = {}'.format(self.total_error_diction[label]['mean'],self.total_error_diction[label]['std'])
    def get_Sensitivity_and_Pplus(self):
        # Sensitivity & P plus
        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            FN = self.false_negtive_list[label]
            FP = self.false_positive_list[label]
            TP = len(self.error_list_for_label[label])
            self.sensitivity[label] = 1.0*(1.0-float(FN)/(FN+TP))
            self.Pplus[label] = 1.0*(1.0-float(FP)/(FP+TP))
        
    def ComputeStatistics(self):
        self.get_mean_and_std()
        self.get_Sensitivity_and_Pplus()
    def output_to_json(self,jsonfilename):
        with open(jsonfilename,'w') as fout:
            json.dump(self.total_error_diction,fout,indent = 4,sort_keys = True)
            print 'json file save to {}.'.format(jsonfilename)
    def display_error_statistics(self):
        print '\n'
        print '-'*30
        print '[label]  [mean]   [std]   [False Negtive]'
        for label in ['P','R','T','Ponset','Poffset','Toffset','Ronset','Roffset']:
            print label, self.total_error_diction[label]['mean'],self.total_error_diction[label]['std'], self.false_negtive_list[label]
            print 'Sensitivity :{:.3f},\t Positive Predictivity: {:.3f}'.format(self.sensitivity[label],self.Pplus[label])

if __name__ == '__main__':
    eva_obj = TotalRoundEvaluation()
    for RoundInd in xrange(1,101):
        print 'Round :',RoundInd
        #RunGroup(RoundInd)
        #eva_obj.RunEval(RoundInd)
        eva_obj.ReadEvaluationFolder(RoundInd)
    # compute error statistics
    eva_obj.ComputeStatistics()
    # display error statistics
    eva_obj.display_error_statistics()

