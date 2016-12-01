#encoding:utf-8
"""
ECG Grouping Evaluation module
Author : Gaopengfei

This file find the bad performance record, print its round number and record name.
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
from TextLogger import TextLogger


def RunGroup(RoundInd):
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


class FindBadRecord:
    def __init__(self,mean_threshold,std_threshold,FN_threshold,FP_threshold):
        self.possible_label_list = ['P','T','Ponset','Poffset','Toffset']
        self.total_error_diction =  dict()
        self.error_list_for_label = dict()
        self.false_negtive_list = dict()
        self.false_positive_list = dict()
        self.sensitivity = dict()
        self.Pplus = dict()
        # thresholds
        self.mean_threshold = mean_threshold
        self.std_threshold = std_threshold
        self.FN_threshold = FN_threshold
        self.FP_threshold = FP_threshold
        # initialize for error_list_for_label& false_negtive_list
        for label in self.possible_label_list:
            self.error_list_for_label[label] = []
            self.false_negtive_list[label] = 0
            self.false_positive_list[label] = 0
            self.sensitivity[label] = 0
            self.Pplus[label] = 0

    def RunEval(self,RoundInd,GroupResultFolder):
        resultfilelist = glob.glob(os.path.join(GroupResultFolder,'*.json'))

        ErrDict = dict()
        ErrData = dict()

        for label in self.possible_label_list:
            ErrData[label] = dict()
            ErrDict[label] = dict()
            errList = []
            FNcnt = 0
            FPcnt = 0

            for file_ind in xrange(0,len(resultfilelist)):
                # progress info
                print 'label:',label
                print 'evaluation: file_ind',file_ind
                

                eva= Evaluation2Leads()
                eva.loadlabellist(resultfilelist[file_ind],label, supress_warning = True)
                eva.evaluate(label)

                # total error
                errList.extend(eva.errList)
                FN = eva.getFNlist()
                FP = eva.getFPlist()

                FNcnt += FN
                FPcnt += FP
                # police check:
                # find error that exceeded thresholds
                self.police_check(eva,RoundInd,resultfilelist[file_ind],label)

            self.error_list_for_label[label].extend(errList)
            self.false_negtive_list[label] += FNcnt
            self.false_positive_list[label] += FPcnt

    def police_check(self,eva,RoundInd,resultfilepath,label):
        # pass 
        mean = np.mean(eva.errList)
        std = np.std(eva.errList)
        FN = eva.getFNlist()
        FP = eva.getFPlist()

        txt_logger = TextLogger(
                os.path.join(curfolderpath,'Log_which_record_is_bad.txt'))
        # threshold
        good_record_mark = True
        if mean > self.mean_threshold:
            print 'mean = ',mean
            txt_logger.dump('mean = {}'.format(mean))
            good_record_mark = False
        if std > self.std_threshold:
            print 'std = ', std
            good_record_mark = False
            txt_logger.dump('std = {}'.format(std))
        if FN > self.FN_threshold:
            print 'FN = ', FN
            good_record_mark = False
            txt_logger.dump('FN = {}'.format(FN))
        if FP > self.FP_threshold:
            print 'FP = ', FP
            good_record_mark = False
            txt_logger.dump('FP = {}'.format(FP))
        if good_record_mark == False:
            print 'Round {}, record name {}'.format(RoundInd,os.path.split(resultfilepath)[-1])
            print '-'*20
            print '\n'
            txt_logger.dump('Round {}, record name {} label [{}]'.format(RoundInd,os.path.split(resultfilepath)[-1],label))
            txt_logger.dump('-'*20)

        

    def ReadEvaluationFolder(self,RoundInd):
        evalinfopath = os.path.join(curfolderpath,'MultiLead4','EvalInfoRound{}'.format(RoundInd))
        # write to json
        with open(os.path.join(evalinfopath,'ErrData.json'),'r') as fin:
            ErrData = json.load(fin)
        # add to total error list & False Negtive List
        for label in self.possible_label_list:
            self.error_list_for_label[label].extend(ErrData[label]['errList'])
            self.false_negtive_list[label] += ErrData[label]['FN']
            self.false_positive_list[label] += ErrData[label]['FP']

            #print 'label:',label,self.false_positive_list[label]
            #pdb.set_trace()

    def get_mean_and_std(self):
        for label in self.possible_label_list:
            self.total_error_diction[label] = dict()
            self.total_error_diction[label]['mean'] = np.mean(self.error_list_for_label[label])
            self.total_error_diction[label]['std'] = np.std(self.error_list_for_label[label])
            # debug
            print 'for label {}:'.format(label)
            print 'mean = {}, std = {}'.format(self.total_error_diction[label]['mean'],self.total_error_diction[label]['std'])
    def get_Sensitivity_and_Pplus(self):
        # Sensitivity & P plus
        for label in self.possible_label_list:
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
        for label in self.possible_label_list:
            print label, self.total_error_diction[label]['mean'],self.total_error_diction[label]['std'], self.false_negtive_list[label]
            print 'Sensitivity :{:.3f},\t Positive Predictivity: {:.3f}'.format(self.sensitivity[label],self.Pplus[label])

if __name__ == '__main__':
    # clear Log file
    with open(os.path.join(curfolderpath,'Log_which_record_is_bad.txt'),'w') as fin:
        pass
    police_obj = FindBadRecord(20, 20, 20, 20)
    # target label
    police_obj.possible_label_list = ['T',]

    for RoundInd in xrange(1,101):
        print 'processing Round :',RoundInd
        #RunGroup(RoundInd)
        #police_obj.RunEval(RoundInd)
        GroupResultFolder = os.path.join(curfolderpath,'M4_SWT','Result','SWT_T{}'.format(RoundInd))
        police_obj.RunEval(RoundInd,GroupResultFolder)
    # compute error statistics
    police_obj.ComputeStatistics()
    # display error statistics
    police_obj.display_error_statistics()

