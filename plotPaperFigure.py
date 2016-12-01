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
import pdb

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
from QTdata.loadQTdata import QTloader
from RFclassifier.evaluation import ECGstatistics
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

def debug_show_eval_result(\
            picklefilename,\
            target_recname = None\
        ):
    with open(picklefilename,'r') as fin:
        Results = pickle.load(fin)
    # only plot target rec
    if target_recname is not None:
        print Results[0][0]
        if Results[0][0]!= target_recname:
            return 
    fResults = ECGRF.ECGrf.resfilter(Results)
    #
    # show filtered results & raw results
    # Evaluate prediction result statistics
    #

    ECGstats = ECGstatistics(fResults[0:1])
    ECGstats.eval(debug = False)
    ECGstats.dispstat0()
    ECGstats.plotevalresofrec(Results[0][0],Results)

    

def LOOT_Eval(RFfolder):
    #RFfolder = os.path.join(\
            #curfolderpath,\
            #'TestResult',\
            #'t2')
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

def TestN_Eval(RFfolder):
    #RFfolder = os.path.join(\
            #curfolderpath,\
            #'TestResult',\
            #'t2')
    picklereslist = glob.glob(os.path.join(RFfolder,'*.out'))
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
    EvalLogfilename = os.path.join(curfolderpath,'res.log')
    # display error stat for each label & save results to logfile
    ECGstatistics.dispstat0(\
            pFN = FN,\
            pErr = Err,\
            LogFileName = EvalLogfilename,\
            LogText = 'Statistics of Results in [{}]'.\
                format(RFfolder)\
            )
    # find best round
    bRselector.dispBestRound()
    bRselector.dumpBestRound(EvalLogfilename)

    ECGstats.stat_record_analysis(pErr = Err,pFN = FN,LogFileName = EvalLogfilename)

class BestRoundSelector:
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
            fout.write('\n>>Best Round statistics [label: (mean,std) ]<<\n')
            fout.write('\n Error Exceedings: [mean:{},std:{}]\n'.format(self.ExcMean,self.ExcStd))
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
        
def PlotMarkerList():
    return [
            'ro',
            'go',
            'bo',
            'r<',
            'r>',
            'g<',
            'g>',
            'b<',
            'b>',
            'w.']
def Label2PlotMarker(label):
    if label == 'T':
        mker = 'ro'
    elif label == 'R':
        mker = 'go'
    elif label == 'P':
        mker = 'bo'
    elif label == 'Tonset':
        mker = 'r<'
    elif label == 'Toffset':
        mker = 'r>'
    elif label == 'Ronset':
        mker = 'g<'
    elif label == 'Roffset':
        mker = 'g>'
    elif label == 'Ponset':
        mker = 'b<'
    elif label == 'Poffset':
        mker = 'b>'
    else:# white
        mker = 'w.'
    return mker
def PlotrawPredictionLabels(picklefilename):
    # Init Parameters
    target_recname = None
    ResID = 0
    showExpertLabel = True
    xLimtoLabelRange = True

    with open(picklefilename,'r') as fin:
        Results = pickle.load(fin)
    # only plot target rec
    if target_recname is not None:
        print 'Result[{}] QTrecord name:{}'.format(ResID,Results[ResID][0])
        if target_recname is not None and Results[ResID][0]!= target_recname:
            return 

    #
    # show filtered results & raw results
    # Evaluate prediction result statistics
    #
    recname = Results[ResID][0]
    recLoader = QTloader()
    sig = recLoader.load(recname)

    rawReslist = Results[ResID][1]

    # plot signal
    plt.figure(1);

    rawsig = sig['sig']
    # plot sig 
    plt.plot(rawsig)
    # for xLim(init)
    Label_xmin ,Label_xmax = rawReslist[0][0],rawReslist[0][0]
    plotmarkerlist = PlotMarkerList()
    PlotMarkerdict = {x:[] for x in plotmarkerlist}
    map(lambda x:PlotMarkerdict[Label2PlotMarker(x[1])].append((x[0],rawsig[x[0]])),rawReslist)

    # for each maker
    for mker,posAmpList in PlotMarkerdict.iteritems():
        if len(posAmpList) ==0:
            continue
        poslist,Amplist = zip(*posAmpList)
        Label_xmin = min(Label_xmin,min(poslist))
        Label_xmax = max(Label_xmax ,max(poslist))
        plt.plot(poslist,Amplist,mker,label='{} Label'.format(mker))
    # plot expert marks
    if showExpertLabel:
        # blend together
        explbpos = recLoader.getexpertlabeltuple(recname)
        explbpos = [[x[0],x[0]] for x in explbpos]
        explbAmp = [[-100,100] for x in explbpos]
        # plot expert labels
        for x in explbpos:
            xpos = x[0]
            plt.plot([xpos,xpos],[-10,10],'black')
        #h_expertlabel = plt.plot(explbpos,explbAmp,'black')
        # set plot properties
        #plt.setp(h_expertlabel,'ms',12)
    if xLimtoLabelRange == True:
        plt.xlim(Label_xmin-100,Label_xmax+100)

    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.title(recname)
    plt.show()


def get_boundary_percentage(errlist,cfval):
    if cfval is None or cfval <0:
        raise StandardError('cfval is {}.'.format(cfval))
    N = len(errlist)
    tmplist = [x for x in errlist if abs(x)<=cfval]
    return float(len(tmplist))/N

def get_confidence_value(errlist):
    L,R = 0,1000
    TargetPercent = 0.9
    while L<R:
        mid = int(L + (R-L)/2)
        if get_boundary_percentage(errlist,mid) < 0.9:
            L = mid + 1
        else:
            R = mid
        
    cfval = R
    return cfval
def PlotErrorHist():
    with open(os.path.join(projhomepath,'tmp','Err.txt'),'r') as fin:
        pErr = pickle.load(fin)
    # all the ECG CP labels
    LabelList = [
            'P',
            'R',
            'T',
            'Ponset',
            'Poffset',
            'Ronset',
            'Roffset',
            'Toffset'
            ]
    ErrDict = {x:[] for x in LabelList}
    ErrConfDict = {x:None for x in LabelList}
    LEtuple = zip(pErr['label'],pErr['err'])
    map(lambda x :ErrDict[x[0]].append(x[1]*4.0),LEtuple)
    # get 90% confidence interval
    for tlabel in LabelList:
        errlist = ErrDict[tlabel]
        cfval = get_confidence_value(errlist)
        ErrConfDict[tlabel] = cfval

    # plot Err
    plt.figure(1)
    for pltcnt,tlb in enumerate(LabelList):
        plt.subplot(3,3,pltcnt+1)
        n,bins,patches = plt.hist(ErrDict[tlb],bins = 10,range = (-45,45))
        cfval = ErrConfDict[tlb]

        MaxYval = math.ceil(1.2*max(n)/2000)*2000
        # confidence interval
        plt.plot([cfval,cfval],[0,MaxYval],'r',linewidth = 2)
        plt.plot([-cfval,-cfval],[0,MaxYval],'r',linewidth = 2)

        plt.title(tlb)
        plt.xlabel('Error(ms)')
        plt.ylabel('Number')

    plt.show()

if __name__ == '__main__':
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           't16')
    # ==========================
    # plot prediction result
    # ==========================
    #reslist = glob.glob(os.path.join(\
           #RFfolder,'*.out'))
    #for fi,fname in enumerate(reslist):
       #debug_show_eval_result(fname,target_recname = 'sele0612')
    # ==========================
    # show evaluation statistics
    # ==========================

    # PlotErrorHist()
    #targetresultfilename = os.path.join(RFfolder,'hand125.out')
    #PlotrawPredictionLabels(targetresultfilename)

