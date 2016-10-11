#encoding:utf-8
"""
Date: 2016.10.10
ECG Grouping Evaluation module
Author : Gaopengfei

This file find the bad performance record, print its round number and record name.

1. This file tries to group the results as single outputs around the ground truth position.
   * Must make sure 'EvaluationSchemes/results/{result_name}/group-result' folder exists in
     the Round Folder
2. This file computes the intra-record standard deviation with police object.
"""
import os
import sys
import json
import glob
import bisect
import math
import pickle
import shutil
import random
import time
import importlib
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
projhomepath = os.path.dirname(curfolderpath)
sys.path.append(projhomepath)
#
# my project components

from EvaluationSchemes.Group2LeadsResults import GroupResult2Leads
from EvaluationSchemes.EvaluationMultiLeads import EvaluationMultiLeads
from TextLogger import TextLogger


def GroupingRawResults(RoundInd, round_folder, output_round_folder):
    '''Grouping the raw detection result of random forest.'''
    # load the results
    RoundFolder = round_folder
    raw_result_folder = os.path.join(RoundFolder,'round{}'.format(RoundInd))
    output_round_folder = os.path.join(output_round_folder,'round{}'.format(RoundInd))

    # Remove existing folder
    if os.path.exists(output_round_folder) == True:
        shutil.rmtree(output_round_folder)
    os.mkdir(output_round_folder)

    # each result file
    resfiles = glob.glob(os.path.join(raw_result_folder, 'result_*'))
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
        jsonfilepath = os.path.join(output_round_folder,recname+'.json')
        with open(jsonfilepath,'w') as fout:
            json.dump(GroupDict,fout,indent = 4,sort_keys = True)
    print 'Finished grouping for round %d' % RoundInd

class FindBadRecord:
    def __init__(self,mean_threshold,std_threshold,FN_threshold,FP_threshold,possible_label_list = None, result_converter = None):
        if possible_label_list is None:
            self.possible_label_list = ['P','T','Ponset','Poffset','Toffset']
        else:
            self.possible_label_list = possible_label_list

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

        # result converter
        self.result_converter_ = result_converter
        # initialize for error_list_for_label& false_negtive_list
        # statistics for each record.
        self.statistics_list_for_label = dict()
        for label in self.possible_label_list:
            self.error_list_for_label[label] = []
            self.false_negtive_list[label] = 0
            self.false_positive_list[label] = 0
            self.sensitivity[label] = 0
            self.Pplus[label] = 0
            self.statistics_list_for_label[label] = dict(mean = [], std = [])

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
                # print 'label:',label
                # print 'evaluation: file_ind',file_ind
                

                eva= EvaluationMultiLeads(self.result_converter_)
                eva.loadlabellist(resultfilelist[file_ind],label, supress_warning = True)
                eva.evaluate(label)

                # total error
                errList.extend(eva.errList)
                FN = eva.getFNlist()
                FP = eva.getFPlist()
                # intrarecord mean & std
                self.statistics_list_for_label[label]['mean'].append(np.mean(eva.errList))
                self.statistics_list_for_label[label]['std'].append(np.std(eva.errList))

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
        if len(eva.errList) == 0:
            mean = -1
            std = -1
        else:
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
            if len(self.error_list_for_label[label]) == 0:
                self.total_error_diction[label]['mean'] = -1
                self.total_error_diction[label]['std'] = -1
            else:
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
            if FN + TP == 0:
                self.sensitivity[label] = -1
                self.Pplus[label] = -1
                continue
                
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
            print label, self.total_error_diction[label]['mean'],
            self.total_error_diction[label]['std'], self.false_negtive_list[label]
            print 'Sensitivity :{:.3f},\t Positive Predictivity: {:.3f}'.format(
                    self.sensitivity[label],self.Pplus[label])
            print 'Mean across records: ',
            print 'mean = {}, std = {}'.format(
                    np.nanmean(self.statistics_list_for_label[label]['mean']),
                    np.nanmean(self.statistics_list_for_label[label]['std']))
    def dump_statistics_to_file(self, log_file_name):
        '''Dump statistics data to txt file.'''
        def BreakLine(fout):
            fout.write('\n')
        with open(log_file_name, 'w') as fout:
            fout.write('\n')
            fout.write('-'*30 + '\n')
            fout.write('[label]  [mean]   [std]   [False Negtive]');
            BreakLine(fout)
            for label in self.possible_label_list:
                fout.write('label, self.total_error_diction[label][''mean'']')
                fout.write('{} {}\n'.format(self.total_error_diction[label]['std'],
                    self.false_negtive_list[label]))
                BreakLine(fout)
                fout.write('Sensitivity :{:.3f},\t Positive Predictivity: {:.3f}'.format(
                        self.sensitivity[label],self.Pplus[label]))
                BreakLine(fout)
                fout.write('Mean across records: ')
                fout.write('mean = {}, std = {}'.format(
                        np.nanmean(self.statistics_list_for_label[label]['mean']),
                        np.nanmean(self.statistics_list_for_label[label]['std'])))
                BreakLine(fout)

def ConverterFactory(converter_name):
    '''Return converter according to converter name.'''
    # Import Converters
    ListResultConverterModule = importlib.import_module(
            'EvaluationSchemes.result-converters.list-result-converter')
    ListResultConverter = ListResultConverterModule.ListResultConverter
    SimpleConverterModule = importlib.import_module(
            'EvaluationSchemes.result-converters.original-converter')
    SimpleConverter = SimpleConverterModule.OriginalConverter
    # Converter function handle
    if converter_name == 'simple-converter':
        result_converter = SimpleConverter.convert

    return result_converter
def ResetFolder(folder_name):
    # Remove existing folder
    if os.path.exists(folder_name) == True:
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

if __name__ == '__main__':

    # Name of the experiment
    experiment_name = 'swt-paper-2'
    total_round_number = 30

    # Get converter
    result_converter = ConverterFactory('simple-converter')
    # Set folder path.
    prediction_result_folder = os.path.join(projhomepath, 'result',
            experiment_name)
    evaluation_result_path = os.path.join(projhomepath,'EvaluationSchemes',
            'results', experiment_name)

    # Grouping given result.
    should_group_result = raw_input('Grouping given result folder:{}?'.format(
        prediction_result_folder))
    if should_group_result in ['y', 'Y']:
        print 'Grouping...'
        # Remove existing folders
        ResetFolder(evaluation_result_path)
        new_group_result_folder = os.path.join(evaluation_result_path,'group-result')
        ResetFolder(new_group_result_folder)

        for ind in xrange(1,total_round_number + 1):
            GroupingRawResults(ind, prediction_result_folder,
                    new_group_result_folder)
        prediction_result_folder = new_group_result_folder
        result_converter = ConverterFactory('simple-converter')

    # clear Log file
    with open(os.path.join(evaluation_result_path,
        'Log_which_record_is_bad.txt'),'w') as fin:
        pass

    possible_label_list = ['T','P','Toffset','Ponset','Poffset','Ronset','R','Roffset']

    police_obj = FindBadRecord(10, 13, 20, 20,
            possible_label_list = possible_label_list,
            result_converter = result_converter)

    for RoundInd in xrange(1, total_round_number + 1):
        print 'processing Round :',RoundInd
        GroupResultFolder = os.path.join(prediction_result_folder,
                'round{}'.format(RoundInd))
        police_obj.RunEval(RoundInd,GroupResultFolder)
    # compute error statistics
    police_obj.ComputeStatistics()
    # display error statistics
    police_obj.display_error_statistics()
    police_obj.dump_statistics_to_file(os.path.join(evaluation_result_path, 'evaluation-statistics.txt'))
