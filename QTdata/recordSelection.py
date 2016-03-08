#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import matplotlib.pyplot as plt

# project homepath
curfilepath =  os.path.realpath(__file__)
projhomepath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(projhomepath)
# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

#import QTdata.loadQTdata.QTloader as QTloader
from QTdata.loadQTdata import QTloader 
from RFclassifier.ECGRF import ECGrf as ECGRF
from RFclassifier.evaluation import ECGstatistics as ECGstats

class RecSelector():
    def __init__(self):
        self.qt= QTloader()
    def inspect_recs(self):
        reclist = self.qt.getQTrecnamelist()
        sel1213 = conf['sel1213']
        sel1213set = set(sel1213)
        
        out_reclist = set(reclist) - sel1213set

        for ind,recname in enumerate(out_reclist):
            # inspect
            print '{} records left.'.format(len(out_reclist) - ind - 1)
            self.qt.plotrec(recname)
    def inspect_recname(self,tarrecname):
        self.qt.plotrec(tarrecname)
    def inspect_selrec(self):
        sel0115 = conf['sel0115']
        for ind,recname in enumerate(sel0115):
            print '{} records left.'.format(len(sel0115) - ind - 1)
            self.inspect_recname(recname)
            
    def RFtest(self,testrecname):
        ecgrf = ECGRF()
        sel1213 = conf['sel1213']
        ecgrf.training(sel1213)
        Results = ecgrf.testing([testrecname,])
        # Evaluate result
        filtered_Res = ECGRF.resfilter(Results)
        stats = ECGstats(filtered_Res[0:1])
        Err,FN = stats.eval(debug = False)

        # write to log file
        EvalLogfilename = os.path.join(projhomepath,'res.log')
        stats.dispstat0(\
                pFN = FN,\
                pErr = Err)
        # plot prediction result
        stats.plotevalresofrec(Results[0][0],Results)
                #LogFileName = EvalLogfilename,\
                #LogText = 'Statistics of Results in [{}]'.\
                    #format(RFfolder)\
                #)
        #ECGstats.stat_record_analysis(pErr = Err,pFN = FN,LogFileName = EvalLogfilename)
        




if __name__ == "__main__":
    recsel = RecSelector()
    #recsel.inspect_recname('sel16272')
    recsel.inspect_recs()
    print '-'*30


