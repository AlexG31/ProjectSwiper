#encoding:utf-8
import os
import sys
import pickle
import json
import pdb
import glob
import marshal
import matplotlib.pyplot as plt

# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
print projhomepath
# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

#import QTdata.loadQTdata.QTloader as QTloader
from QTdata.loadQTdata import QTloader 
from RFclassifier.ECGRF import ECGrf as ECGRF
from RFclassifier.evaluation import ECGstatistics as ECGstats
from WTdenoise.wtfeature import WTfeature
import pywt

class RecSelector():
    def __init__(self):
        self.qt= QTloader()
    def inspect_recs(self):
        reclist = self.qt.getQTrecnamelist()
        sel1213 = conf['sel1213']
        sel1213set = set(sel1213)
        
        out_reclist = set(reclist)# - sel1213set

        # records selected
        selected_record_list = []
        for ind,recname in enumerate(out_reclist):
            # inspect
            print '{} records left.'.format(len(out_reclist) - ind - 1)
            self.qt.plotrec(recname)
            # debug
            if ind > 2:
                pass
                #print 'debug break'
                #break
    def plot_rec_dwt(self):
        reclist = self.qt.getQTrecnamelist()
        sel1213 = conf['sel1213']
        sel1213set = set(sel1213)
        
        out_reclist = set(reclist)# - sel1213set

        # dwt coef 
        dwtECG = WTfeature()
        # records selected
        selected_record_list = []
        for ind,recname in enumerate(out_reclist):
            # inspect
            print 'processing record : {}'.format(recname)
            print '{} records left.'.format(len(out_reclist) - ind - 1)
            # debug selection 
            if not recname.startswith(ur'sele0704'):
                continue
            sig = self.qt.load(recname)
            # wavelet 
            waveletobj = dwtECG.gswt_wavelet() 
            self.plot_dwt_coef_with_annotation(sig['sig'],waveletobj = waveletobj,ECGrecordname = recname)
            #pdb.set_trace()
    def plot_dwt_coef_with_annotation(self,rawsig,waveletobj = pywt.Wavelet('db2'),figureID = 1,ECGrecordname = 'ECG input signal'):
            
        N = 5
        xL,xR = 1000,1600
        tarpos  = 1500
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        plt.figure(figureID)
        # plot raw ECG
        plt.subplot(N+1,1,1)
        # hide axis
        frame = plt.gca()
        frame.axes.get_xaxis().set_visible(False)
        frame.axes.get_yaxis().set_visible(False)
        plt.plot(pltxLim,sigAmp)
        # plot reference point
        #plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title(ECGrecordname)
        #plt.xlim(pltxLim)

        for i in range(2,N+2):
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            # crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # plot 
            plt.subplot(N+1,1,i)
            # hide axis
            frame = plt.gca()
            frame.axes.get_xaxis().set_visible(False)
            frame.axes.get_yaxis().set_visible(False)

            plt.plot(xi,cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(xL,xR-1)
            plt.title('DWT Level ({}):'.format(i-1))
        plt.show()

if __name__ == "__main__":
    print '-'*30
    recsel = RecSelector()
    recsel.plot_rec_dwt()



