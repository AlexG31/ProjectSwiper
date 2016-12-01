#encoding:utf-8
import os
import sys
import pickle
import json
import pdb
import random
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
    def plot_rec_dwt_random_pairs(self):
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
            self.plot_dwt_rswt(sig['sig'],waveletobj = waveletobj,ECGrecordname = recname,auto_plot = True)
    def Normalise(self,sig):
        if sig is None or len(sig) == 0:
            return sig
        sigmax,sigmin = sig[0],sig[0]
        eps = 1e-6
        for sigval in sig:
            if sigval>sigmax:
                sigmax = sigval
            if sigval<sigmin:
                sigmin = sigval
        if sigmax - sigmin <= eps:
            return sig
        AmpSpan = sigmax-sigmin
        for i in range(0,len(sig)):
            sig[i] = (sig[i]-sigmin)/AmpSpan
        return sig
    def plot_dwt_rswt(self,rawsig,waveletobj = pywt.Wavelet('db2'),figureID = 1,ECGrecordname = 'ECG input signal',auto_plot = True):
        ## =========================================V    
        # 展示RSWT示意图
        ## =========================================V    
        N = 5
        xL,xR = 1000,1600
        tarpos  = 1500
        # props of ARROW
        arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        plt.figure(figureID)
        # plot raw ECG
        plt.subplot(N+1,1,1)
        # get handle for annote arrow
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
            fig = plt.subplot(N+1,1,i)
            # get max
            amp_max = cDamp[0]
            amp_min = cDamp[0]
            for cval in cDamp:
                amp_max = max(amp_max,cval)
                amp_min = min(amp_min,cval)
            # left pair
            lpairtail = [len(cDamp)*0.3,amp_min+(amp_max-amp_min)*0.8]
            L,R = int(len(cDamp)*0.1),int(len(cDamp)*0.4)
            rspairhead = (random.randint(L,R-1),random.randint(L+1,R))
            lpairtail[0] = int((rspairhead[0]+rspairhead[1])/2)
            # debug print
            #print 'left pair tail:',lpairtail
            #print 'rand selected pair head:', rspairhead
            #print 'rs height:',cDamp[int(rspairhead[0])],cDamp[int(rspairhead[1])]
            plt.text(lpairtail[0],lpairtail[1],'pair({}a)'.format(i-1))
            color = '#fe3b8d'
            arrowprops = dict(width = 1,headwidth = 4,facecolor=color,edgecolor = color, shrink=0)
            fig.annotate('', xy=(rspairhead[0],cDamp[int(rspairhead[0])]), xytext=lpairtail,arrowprops=arrowprops)
            fig.annotate('', xy=(rspairhead[1],cDamp[int(rspairhead[1])]), xytext=lpairtail,arrowprops=arrowprops)
            # right pair
            rpairtail = [len(cDamp)*0.7,amp_min+(amp_max-amp_min)*0.8]
            L,R = int(len(cDamp)*0.3),int(len(cDamp)*0.8)
            rspairhead = (random.randint(L,R-1),random.randint(L+1,R))
            rpairtail[0] = int((rspairhead[0]+rspairhead[1])/2)
            # debug print
            #print 'left pair tail:',lpairtail
            #print 'rand selected pair head:', rspairhead
            #print 'rs height:',cDamp[int(rspairhead[0])],cDamp[int(rspairhead[1])]
            plt.text(rpairtail[0],rpairtail[1],'pair({}b)'.format(i-1))
            arrowprops = dict(width = 1,headwidth = 4,facecolor='g',edgecolor = 'g', shrink=0)
            fig.annotate('', xy=(rspairhead[0],cDamp[int(rspairhead[0])]), xytext=rpairtail,arrowprops=arrowprops)
            fig.annotate('', xy=(rspairhead[1],cDamp[int(rspairhead[1])]), xytext=rpairtail,arrowprops=arrowprops)
            # hide axis
            frame = plt.gca()
            frame.axes.get_xaxis().set_visible(False)
            frame.axes.get_yaxis().set_visible(False)

            #plt.grid(True)
            plt.plot(cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(0,len(cDamp)-1)
            plt.title('DWT Level ({}):'.format(i-1))
        if auto_plot is True:
            plt.show()

    def plot_dwt_coef_with_annotation(self,rawsig,waveletobj = pywt.Wavelet('db2'),figureID = 1,ECGrecordname = 'ECG input signal',auto_plot = True):
            
        N = 5
        xL,xR = 1000,1600
        tarpos  = 1500
        # props of ARROW
        arrowprops = dict(width = 1,facecolor='black', shrink=0.05)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        sigAmp = self.Normalise(sigAmp)
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        plt.figure(figureID)
        # plot raw ECG
        fig = plt.subplot(N+1,1,1)
        # get handle for annote arrow
        fig.annotate('local max', xy=(1200, 0), xytext=(1300, 0.9),arrowprops=arrowprops)
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
            cDamp = self.Normalise(cDamp)
            # plot 
            fig = plt.subplot(N+1,1,i)
            fig.annotate('local max', xy=(xL,0), xytext=(xL+10, 0.6),arrowprops=arrowprops)
            # hide axis
            frame = plt.gca()
            frame.axes.get_xaxis().set_visible(False)
            frame.axes.get_yaxis().set_visible(False)

            plt.plot(xi,cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(xL,xR-1)
            plt.title('DWT Level ({}):'.format(i-1))
        if auto_plot is True:
            plt.show()

if __name__ == "__main__":
    print '-'*30
    recsel = RecSelector()
    recsel.plot_rec_dwt_random_pairs()



