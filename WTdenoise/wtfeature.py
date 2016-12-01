#encoding:utf-8
import pywt
import os
import codecs
import json

import numpy as np
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)


def denoise(sig):
    ## keep [2,7]
    sA,sD = [],[]
    cA = sig
    for i in range(0,7):
        cA,cD = pywt.dwt(cA,'coif2')
        sD.append(cD)
    ## filter
    #for i in range(0,len(sD)):
        #print 'sD',i,'len:',len(sD[i])

    for i in range(0,2):
        sD[i] = [0]*len(sD[i])
    cA = [0]*len(cA)
    ## idwt
    for i in range(6,-1,-1):

        # padding with zeros
        pdzeros = len(cA) - len(sD[i])
        #print pdzeros
        if pdzeros > 0:
            #print 'sD[i]:',sD[i].shape
            zstk = np.zeros((pdzeros,))
            #print 'zstk:',zstk.shape
            sD[i] = np.hstack((sD[i],zstk))
            #print 'sD[i]:',sD[i].shape
        elif pdzeros < 0:
            zstk = np.zeros((-pdzeros,))
            np.hstack((cA,zstk))
        #print 'len cA:',len(cA)
        #print 'len sD[',i,']:',len(sD[i])
        cA = pywt.idwt(cA,sD[i],'coif2')
        sD.append(cD)
    return cA
class WTfeature:
    def __init__(self):
        pass
    def getWTcoefficient_number_in_each_level(self):
        # get window length 
        fs = conf['fs']
        winlen_ratio = conf['winlen_ratio_to_fs']
        WinLen = winlen_ratio*fs
        DWT_LEVEL = conf['DWT_LEVEL']
        # get number of coef in each dwt level
        #sig = range(1,WinLen+1)
        #dslist = self.getWTcoef_gswt(sig)
        cnlist = []
        curWinLen = int(WinLen)
        for ind in xrange(0,DWT_LEVEL):
            cnlist.append(curWinLen/2)
            curWinLen /= int(2)
        return cnlist

    def getWT_Features(\
            self,\
            rawsig,\
            waveletobj = None\
            ):
        # 
        # Parameters:
        # N : number of dwt levels

        # waveletobj:
        # Type of wavelet used in DWT
        # --------------
        # level of DWT
        # --------------
        Ndec = conf['DWT_LEVEL']
        if waveletobj is None:
            if conf['Wavelet_type'] == 'gswt':
                waveletobj = self.gswt_wavelet()
            else:
                waveletobj = pywt.Wavelet(conf['Wavelet_type'])
        cA = rawsig

        detailList = []
        for i in xrange(0,Ndec):
            cA,cD = pywt.dwt(cA,waveletobj)
            detailList.append(cD)
        detailList.append(cA) 
        return detailList

    def plot_wtcoefs(\
            self,\
            rawsig,\
            waveletobj = pywt.Wavelet('db2'),\
            figureID = 1
            ):
        # ========================================================  
        # description: this function is used to 
        #   plot the rawsig with its dwt coefficients
        #   along with a reference point to indicate the 
        #   corresponding point in each level of dwt coefficients
        # ========================================================  
        # Parameters:
        # N : number of dwt levels

        N = 5
        xL,xR = 1000,2000
        tarpos  = 1500
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # 
        # plot raw signal input
        # 
        plt.figure(figureID)
        plt.subplot(N+1,1,1)
        plt.plot(pltxLim,sigAmp)
        plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title('raw signal input')
        #plt.xlim(pltxLim)

        for i in range(2,N+2):
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # plot 
            plt.subplot(N+1,1,i)
            plt.plot(xi,cDamp)
            plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            #plt.xlim(pltxLim)
            plt.title('Level ({}):'.\
                    format(i-1))
        plt.show()
        
        
    def gswt_wavelet(self):
        dechi = [0,2,-2,0]        
        declo = [1/8.0,3/8.0,3/8.0,1/8.0]
        rechi = [0,2,-2,0]
        reclo = [1/8.0,3/8.0,3/8.0,1/8.0]
        filterbanks = [declo,dechi,reclo,rechi]
        return pywt.Wavelet('gswt',filterbanks)

