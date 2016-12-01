#encoding:utf-8
"""
ECG Evaluation Module
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
projhomepath = os.path.dirname(projhomepath)

# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
from QTdata.loadQTdata import QTloader
from RFclassifier.evaluation import ECGstatistics
import RFclassifier.ECGRF as ECGRF 
from ECGPostProcessing.GroupResult import ResultFilter


def TestingAndSaveResult():
    sel1213 = conf['sel1213']
    time0 = time.time()
    rf = ECGRF.ECGrf()
    rf.training(sel1213[0:1])
    time1 = time.time()
    print 'Training time:',time1-time0
    ## test
    rf.testmdl(reclist = sel1213[0:1])

def debug_show_eval_result(\
            picklefilename,\
            target_recname = None,\
            singleRecordFile = False\
        ):
    with open(picklefilename,'r') as fin:
        Results = pickle.load(fin)
    # convert to a list
    if singleRecordFile == True:
        Results = [Results,]
    for recind in xrange(0,len(Results)):
        # only plot target rec
        if target_recname is not None:
            print 'Current FileName: {}'.format(Results[recind][0])
            if Results[recind][0]!= target_recname:
                return 
        fResults = ECGRF.ECGrf.resfilter(Results)
        #
        # show filtered results & raw results
        # Evaluate prediction result statistics
        #

        ECGstats = ECGstatistics(fResults[recind:recind+1])
        ECGstats.eval(debug = False)
        ECGstats.dispstat0()
        ECGstats.plotevalresofrec(Results[recind][0],Results)

def LOOT_Eval(RFfolder):
    reslist = glob.glob(os.path.join(\
            RFfolder,'*.out'))
    FN =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
    Err = {
                'err':[],
                'pos':[],
                'label':[],
                'recname':[]
                }

    for fi,fname in enumerate(reslist):
        with open(fname,'r') as fin:
            Results = pickle.load(fin)
        fResults = ECGRF.ECGrf.resfilter(Results)
        # show filtered results & raw results
        #for recname , recRes in Results:

        # Evaluate prediction result statistics
        #
        ECGstats = ECGstatistics(fResults[0:1])
        pErr,pFN = ECGstats.eval(debug = False)
        for kk in Err:
            Err[kk].extend(pErr[kk])
        for kk in FN:
            FN[kk].extend(pFN[kk])

    # write to log file
    EvalLogfilename = os.path.join(curfolderpath,'res.log')
    ECGstatistics.dispstat0(\
            pFN = FN,\
            pErr = Err,\
            LogFileName = EvalLogfilename,\
            LogText = 'Statistics of Results in [{}]'.\
                format(RFfolder)\
            )
    ECGstats.stat_record_analysis(pErr = Err,pFN = FN,LogFileName = EvalLogfilename)

def TestN_Eval(RFfolder,output_log_filename = os.path.join(curfolderpath,'res.log')):

    # test result file list
    picklereslist = glob.glob(os.path.join(RFfolder,'*.out'))
    # struct Init
    FN =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
    Err = {
                'err':[],
                'pos':[],
                'label':[],
                'recname':[]
                }
    #========================================
    # select best round to compare with refs
    #========================================
    bRselector = BestRoundSelector()

    for fi,fname in enumerate(picklereslist):
        
        with open(fname,'rU') as fin:
            Results = pickle.load(fin)
        # filter result
        fResults = ECGRF.ECGrf.resfilter(Results)
        # show filtered results & raw results
        #for recname , recRes in Results:

        # Evaluate prediction result statistics
        #
        ECGstats = ECGstatistics(fResults)
        pErr,pFN = ECGstats.eval(debug = False)
        # one test Error stat
        print '[picle filename]:{}'.format(fname)
        print '[{}] files left.'.format(len(picklereslist) - fi)
        evallabellist,evalstats = ECGstatistics.dispstat0(\
                pFN = pFN,\
                pErr = pErr\
                )
        # select best Round 
        numofFN = len(pFN['pos'])
        if numofFN == 0:
            ExtraInfo = 'Best Round ResultFileName[{}]\nTestSet :{}\n#False Negtive:{}\n'.format(fname,[x[0] for x in Results],numofFN)
            bRselector.input(evallabellist,evalstats,ExtraInfo = ExtraInfo)

        for kk in Err:
            Err[kk].extend(pErr[kk])
        for kk in FN:
            FN[kk].extend(pFN[kk])

    # write to log file
    #EvalLogfilename = os.path.join(curfolderpath,'res.log')
    EvalLogfilename = output_log_filename
    # display error stat for each label & save results to logfile
    ECGstatistics.dispstat0(\
            pFN = FN,\
            pErr = Err,\
            LogFileName = EvalLogfilename,\
            LogText = 'Statistics of Results in FilePath [{}]'.format(RFfolder)\
            )
    with open(os.path.join(projhomepath,'tmp','Err.txt'),'w') as fout:
        pickle.dump(Err,fout)
    # find best round
    bRselector.dispBestRound()
    bRselector.dumpBestRound(EvalLogfilename)

    ECGstats.stat_record_analysis(pErr = Err,pFN = FN,LogFileName = EvalLogfilename)

class BestRoundSelector:
    '''Select the best Round'''
    std_max = {
            'P': 20,
            'R': 20,
            'T': 20,
            'Ponset': 14.3,
            'Poffset': 13.9,
            'Ronset': 8.8,
            'Roffset': 9.2,
            'Toffset': 18.6
            }
    mean_max = {
            'P': 4,
            'R': 6,
            'T': 5,
            'Ponset': 2.5,
            'Poffset': 3.1,
            'Ronset': 2.4,
            'Roffset': 4.7,
            'Toffset': 2.8
            }
    # select the best Round Unit (ms)
    def __init__(self):
        self.labellist = []
        self.beststats = []
        self.sumstd = None
        self.ExtraInfo = ""
        self.ExcMean = -1
        self.ExcStd = -1
        self.debugcnt = 0
        
    def input(self,labellist,stats,ExtraInfo = ''):
        # if better than current stats,then keep them
        if False == self.all_lower_than_standard(labellist,stats):
            return
        excmean,excstd = self.getnumof_Exceedingstats(labellist,stats)
        meanlist,stdlist = zip(*stats)
        # sum of std
        sumstd = sum(stdlist)
        if self.labellist == 0 or self.sumstd is None or (self.ExcMean>excmean and self.ExcStd >= excstd) or (self.ExcMean>=excmean and self.ExcStd > excstd) or ((self.ExcMean>=excmean and self.ExcStd >= excstd) and self.sumstd > sumstd):
            self.labellist = labellist
            self.beststats = stats
            self.sumstd = sumstd
            self.ExtraInfo = ExtraInfo
            self.ExcMean,self.ExcStd = excmean,excstd

        
    def all_lower_than_standard(self,labellist,stats):
        # class global threshold
        std_max = self.std_max
        mean_max = self.mean_max

        meanlist,stdlist = zip(*stats)
        label_std_list = zip(labellist,stdlist)
        label_mean_list = zip(labellist,meanlist)
        # cannot have inf/nan
        for meanval in meanlist:
            if np.isnan(meanval) or np.isinf(meanval):
                print 'this record has nan/inf,not included in best round selection.'
                return False
        # m and std Upper bound
        for label,std in label_std_list:
            if std > std_max[label]+4:
                return False
        for label,mean in label_mean_list:
            if abs(mean) > mean_max[label]+2:
                return False
        # the less number of bad m the better
        badn_m,badn_std = self.getnumof_Exceedingstats(labellist,stats)

        self.debugcnt += 1
        return True
    def getnumof_Exceedingstats(self,labellist,stats):
        # class global threshold
        std_max = self.std_max
        mean_max = self.mean_max

        meanlist,stdlist = zip(*stats)
        label_std_list = zip(labellist,stdlist)
        label_mean_list = zip(labellist,meanlist)
        # the less number of bad m the better
        badn_m,badn_std = 0,0
        for label,std in label_std_list:
            if std > std_max[label]:
                badn_std += 1
        for label,mean in label_mean_list:
            if abs(mean) > mean_max[label]:
                badn_m += 1
        return (badn_m,badn_std)
       
    def dumpBestRound(self,LogFileName):
        res = zip(self.labellist,self.beststats)
        with open(LogFileName,'a') as fout:
            fout.write('\n{}\n'.format('='*40))
            fout.write('{}\n'.format(self.ExtraInfo))
            fout.write('\n>>Best Round statistics Format:[label: (mean,std) ]<<\n')
            fout.write('\n number of error exceeds refs: [mean:{},std:{}]\n'.format(self.ExcMean,self.ExcStd))
            for elem in res:
                fout.write('{}\n'.format(elem))
            
    def dispBestRound(self):
        res = zip(self.labellist,self.beststats)
        print '='*40
        print self.ExtraInfo
        print '>>Best Round statistics [label: (mean,std) ]<<'
        print 'Error Exceedings: [mean:{},std:{}]'.format(self.ExcMean,self.ExcStd)
        print 'debugcnt:',self.debugcnt
        for elem in res:
            print elem
        

def EvalQTdbResults(resultfilelist,OutputFolder):
    if resultfilelist==None or len(resultfilelist)==0:
        print "Empty result file list!"
        return None
    FN =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
    FP =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
    Err = {
                'err':[],
                'pos':[],
                'label':[],
                'recname':[]
                }
    #========================================
    # select best round to compare with refs
    #========================================
    bRselector = BestRoundSelector()
    #InvalidRecordList = conf['InvalidRecords']

    # for each record test result
    for fi,fname in enumerate(resultfilelist):
        
        print 'pickle load :',fname
        with open(fname,'rU') as fin:
            Results = pickle.load(fin)
        # skip invalid records
        currecordname = Results[0]
        #if currecordname in InvalidRecordList:
            #continue
        # ==================================
        # filter result of QT
        # ==================================
        reslist = Results[1]
        resfilter = ResultFilter(reslist)
        reslist = resfilter.group_local_result(cp_del_thres = 1)
        reslist = resfilter.syntax_filter(reslist)
        fResults = (Results[0],reslist)

        fResults = [fResults,]
        # show filtered results & raw results
        #for recname , recRes in Results:

        # Evaluate prediction result statistics
        #
        ECGstats = ECGstatistics(fResults)
        pErr,pFN = ECGstats.eval(debug = False)
        # get False Positive
        pFP = ECGstats.pFP
        # one test Error stat
        print '[picle filename]:{}'.format(fname)
        print '[{}] files left.'.format(len(resultfilelist) - fi)
        evallabellist,evalstats = ECGstatistics.dispstat0(pFN = pFN,pErr = pErr)
        # select best Round 
        numofFN = len(pFN['pos'])
        if numofFN == 0:
            ExtraInfo = 'Best Round ResultFileName[{}]\nTestSet :{}\n#False Negtive:{}\n'.format(fname,[x[0] for x in Results],numofFN)
            bRselector.input(evallabellist,evalstats,ExtraInfo = ExtraInfo)
        # ==============================================
        for kk in Err:
            Err[kk].extend(pErr[kk])
        for kk in FN:
            FN[kk].extend(pFN[kk])
        for kk in FP:
            FP[kk].extend(pFP[kk])

    #====================================
    # save Err pickle file
    with open(os.path.join(OutputFolder,'Err.txt'),'w') as fout:
        pickle.dump(Err,fout)
    # write to log file
    #EvalLogfilename = os.path.join(curfolderpath,'res.log')
    output_log_filename = os.path.join(OutputFolder,'RecordResults.log')
    EvalLogfilename = output_log_filename
    # display error stat for each label & save results to logfile
    ECGstatistics.dispstat0(pFN = FN,pErr = Err,LogFileName = EvalLogfilename,LogText = 'Statistics of Results in FilePath [{}]'.format(os.path.split(resultfilelist[0])[0]),OutputFolder = OutputFolder)
    with open(os.path.join(projhomepath,'tmp','Err.txt'),'w') as fout:
        pickle.dump(Err,fout)
    # find best round
    bRselector.dispBestRound()
    bRselector.dumpBestRound(EvalLogfilename)

    ECGstats.stat_record_analysis(pErr = Err,pFN = FN,LogFileName = EvalLogfilename)
    # write csv file
    outputfilename = os.path.join(OutputFolder,'FalsePositive.csv')
    ECGstats.FP2CSV(FP,Err,outputfilename)
    # False Negtive
    outputfilename = os.path.join(OutputFolder,'FalseNegtive.csv')
    ECGstats.FN2CSV(FN,Err,outputfilename)

def getresultfilelist(RFfolder):
    # ================================
    #  get the result file path list
    # ================================
    reslist = glob.glob(os.path.join(\
           RFfolder,'*'))
    ret = []
    non_result_extensions = ['out','json','tmp','log','mdl','txt','rar']
    for fpath in reslist:
        cur_extension = fpath.split('.')[-1]
        # not folder
        if os.path.isdir(fpath) == True:
            continue
        if cur_extension in non_result_extensions:
            continue
        result_filename = os.path.split(fpath)[-1]
        if result_filename.startswith('result_') == False:
            continue
        print 'add result file to analysis: {}'.format(fpath) 
        ret.append(fpath)
    return ret
    
    
def get_training_testing_record_number(RFfolder):
    # get the number of training & testing records
    traininglist = conf['selQTall0']
    testlist = getresultfilelist(RFfolder)
    # filter testlist
    eval_testlist = []
    invalidlist = conf['InvalidRecords']
    for testrec in testlist:
        print 'processing record:{}'.format(testrec)
        with open(testrec,'r') as fin:
            (recname,resdata) = pickle.load(fin)
        if recname not in invalidlist:
            eval_testlist.append(recname)

    num_training = len(traininglist)
    num_testing = len(eval_testlist)
    print 'num of training rec:{}'.format(num_training)
    print 'num of testing rec:{}'.format(num_testing)
    print 'total record number : {}'.format(num_training+num_testing)

if __name__ == '__main__':
        #for round_i in xrange(29,30):
        round_i = 'A_14'
        RFfolder = os.path.join(\
               projhomepath,\
               'TestResult',\
               'pc',\
               '{}'.format(round_i))
        #getRRhisto()
        #sys.exit()
        #get number of test/training records
        # =========================
        # 分析训练和测试的record数目
        # =========================
        #get_training_testing_record_number(RFfolder)
        # 计算误差
        OutputFolder = os.path.join(curfolderpath,'Round_{}'.format(round_i))
        os.mkdir(OutputFolder)
        EvalQTdbResults(getresultfilelist(RFfolder),OutputFolder)
