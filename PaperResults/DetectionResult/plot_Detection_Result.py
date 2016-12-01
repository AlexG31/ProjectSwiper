#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import pdb
import bisect
import matplotlib.pyplot as plt

# =========================================================
# Add project homepath
# =========================================================
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)


# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

#import QTdata.loadQTdata.QTloader as QTloader
from QTdata.loadQTdata import QTloader 
from MITdb.MITdbLoader import MITdbLoader
from RFclassifier.ECGRF import ECGrf as ECGRF
from RFclassifier.evaluation import ECGstatistics as ECGstats
from ECGPostProcessing.GroupResult import ResultFilter
from ECGPloter.ResultPloter import ECGResultPloter



def plotMITdbTestResult():
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           'r3')
    TargetRecordList = ['sel38','sel42',]
    # ==========================
    # plot prediction result
    # ==========================
    reslist = glob.glob(os.path.join(\
           RFfolder,'*'))
    for fi,fname in enumerate(reslist):
        # block *.out
        # filter file name
        if fname[-4:] == '.out' or '.json' in fname:
            continue
        currecname = os.path.split(fname)[-1]
        if currecname not in TargetRecordList:
            pass
        if not currecname.startswith('result'):
            continue
        print 'processing file',fname,'...'
        with open(fname,'r') as fin:
            (recID,reslist) = pickle.load(fin)
        print 'pickle file loaded.'
        # load signal from MITdb
        print 'loading signal data from MITdb...'
        mitdb = MITdbLoader()
        rawsig = mitdb.load(recID)
        print 'signal loaded.'
        # filter result list
        resfilter = ResultFilter(reslist)
        reslist = resfilter.groupresult()
        # plot res
        resploter = ECGResultPloter(rawsig,reslist)
        dispRange = (20000,21000)
        savefolderpath = os.path.join(curfolderpath,'tmp','MITdbTestResult')
        # debug
        #pdb.set_trace()
        #resploter.plot()
        #resploter.plotAndsave(os.path.join(savefolderpath,recID),plotTitle = 'ID:{},Range:{}'.format(recID,dispRange),dispRange = dispRange)
        resploter.plot(plotTitle = recID)
        pdb.set_trace()
# ====================================================================================
# 使用后处理，获得更好的输出结果，降低FP
# ====================================================================================
def plot_MITdb_filtered_Result():
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           'r3')
    TargetRecordList = ['sel38','sel42',]
    # ==========================
    # plot prediction result
    # ==========================
    reslist = glob.glob(os.path.join(\
           RFfolder,'*'))
    for fi,fname in enumerate(reslist):
        # block *.out
        # filter file name
        if fname[-4:] == '.out' or '.json' in fname:
            continue
        currecname = os.path.split(fname)[-1]
        if currecname not in TargetRecordList:
            pass
        if not currecname.startswith('result'):
            continue
        print 'processing file',fname,'...'
        with open(fname,'r') as fin:
            (recID,reslist) = pickle.load(fin)
        print 'pickle file loaded.'
        # load signal from MITdb
        print 'loading signal data from MITdb...'
        mitdb = MITdbLoader()
        rawsig = mitdb.load(recID)
        print 'signal loaded.'
        # filter result list
        resfilter = ResultFilter(reslist)
        reslist = resfilter.group_local_result(cp_del_thres = 1)
        # plot res
        resploter = ECGResultPloter(rawsig,reslist)
        #dispRange = (20000,21000)
        #savefolderpath = os.path.join(curfolderpath,'tmp','MITdbTestResult')
        resploter.plot(plotTitle = recID)
        # debug
        pdb.set_trace()
def plot_QTdb_filtered_Result_with_syntax_filter():
    # exit
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           'r5')
    TargetRecordList = ['result_sel39','result_sel41','result_sel48',]#'sel38','sel42','result_sel821','result_sel14046']
    # ==========================
    # plot prediction result
    # ==========================
    reslist = glob.glob(os.path.join(\
           RFfolder,'*'))
    qtdb = QTloader()
    non_result_extensions = ['out','json','log']
    for fi,fname in enumerate(reslist):
        # block *.out
        file_extension = fname.split('.')[-1]
        if file_extension in non_result_extensions:
            continue
        print 'file name:',fname
        currecname = os.path.split(fname)[-1]
        print currecname
        #if currecname == 'result_sel820':
            #pdb.set_trace()
        if currecname not in TargetRecordList:
            pass
            continue
        # load signal and reslist
        with open(fname,'r') as fin:
            (recID,reslist) = pickle.load(fin)
        # filter result of QT
        resfilter = ResultFilter(reslist)
        reslist = resfilter.group_local_result(cp_del_thres = 1)
        reslist_syntax = resfilter.syntax_filter(reslist)
        # empty signal result
        #if reslist is None or len(reslist) == 0:
            #continue
        #pdb.set_trace()
        sigstruct = qtdb.load(recID)
        # plot res
        #resploter = ECGResultPloter(sigstruct['sig'],reslist)
        #resploter.plot(plotTitle = 'QT database',plotShow = True,plotFig = 2)
        # syntax_filter
        resploter_syntax = ECGResultPloter(sigstruct['sig'],reslist_syntax)
        resploter_syntax.plot(plotTitle = 'QT database syntax_filter',plotShow = True)

def plot_QTdb_filtered_Result():
    # exit
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           'r5')
    TargetRecordList = ['result_sel48',]#'sel38','sel42','result_sel821','result_sel14046']
    # ==========================
    # plot prediction result
    # ==========================
    reslist = glob.glob(os.path.join(\
           RFfolder,'*'))
    qtdb = QTloader()
    non_result_extensions = ['out','json','log']
    for fi,fname in enumerate(reslist):
        # block *.out
        file_extension = fname.split('.')[-1]
        if file_extension in non_result_extensions:
            continue
        print 'file name:',fname
        currecname = os.path.split(fname)[-1]
        print currecname
        #if currecname == 'result_sel820':
            #pdb.set_trace()
        if currecname not in TargetRecordList:
            pass
            continue
        # load signal and reslist
        with open(fname,'r') as fin:
            (recID,reslist) = pickle.load(fin)
        # filter result of QT
        resfilter = ResultFilter(reslist)
        reslist = resfilter.group_local_result(cp_del_thres = 1)
        # empty signal result
        #if reslist is None or len(reslist) == 0:
            #continue
        #pdb.set_trace()
        sigstruct = qtdb.load(recID)
        # plot figure
        # plot res
        resploter = ECGResultPloter(sigstruct['sig'],reslist)
        resploter.plot(plotTitle = 'QT database')
        


if __name__ == "__main__":
    #plot_MITdb_filtered_Result();
    plot_QTdb_filtered_Result_with_syntax_filter()
    sys.exit();
