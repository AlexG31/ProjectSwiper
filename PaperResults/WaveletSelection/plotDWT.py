#encoding:utf-8
import pywt
import os
import sys
import codecs
import pdb
import json

import numpy as np
import scipy.io
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)

sys.path.append(projhomepath)

from WTdenoise.wtfeature import WTfeature
from QTdata.loadQTdata import QTloader

def PlotDWT():
    dat = scipy.io.loadmat('test.mat')
    dat = dat['sig']
    dat = [float(x) for x in dat]
    #plt.plot(dat)
    #plt.show()


    wtf = WTfeature()
    # DWT
    Level = 5
    res = pywt.wavedec(dat,wtf.gswt_wavelet(),level = Level)

    plt.figure(2)
    plt.plot(dat)
    
    
    plt.figure(1)
    for i in xrange(0,Level+1):
        plt.subplot(Level+1,1,i+1)
        plt.plot(res[i])
        plt.title('Level {}'.format(i+1))
    
    plt.show()
class WT_choose:
    def __init__(self):
        self.qt = QTloader()
        self.reclist = self.qt.getQTrecnamelist()
    def loadsig(self,selID):
        self.sig = self.qt.load(self.reclist[selID])
    def PlotDWTCoef(self,sig = None,figID = 1,waveletobj = pywt.Wavelet('sym2')):
        if sig is None:
            sig = self.sig['sig']

        rawsig = sig
        wtf = WTfeature()
        # DWT
        Level = 7
        #waveletobj = wtf.gswt_wavelet()
        #waveletobj = pywt.Wavelet('sym2')
        res = pywt.wavedec(rawsig,waveletobj,level = Level)

        plt.figure(figID)
        N_subplot = Level+2
        plt.subplot(N_subplot,1,1)
        plt.plot(rawsig)
        plt.title('Original Signal')
        detail_i = 1
        for i in xrange(Level,0,-1):
            plt.subplot(N_subplot,1,detail_i+1)
            plt.plot(res[i])
            plt.xlim(0,len(res[i])-1)
            plt.title('Detail Level {}'.format(detail_i))
            detail_i += 1
        plt.subplot(N_subplot,1,N_subplot)
        plt.plot(res[0])
        plt.xlim(0,len(res[0])-1)
        plt.title('Approximation Level')
        
        plt.show()


if __name__ == '__main__':
    wt = WT_choose()
    wtf = WTfeature()
    reclist = wt.reclist
    for ind in xrange(0,105):
        if reclist[ind]!='sel46':
            continue
        wt.loadsig(ind)
        rawsig = wt.sig['sig']
        rawsig = rawsig[1000:2000]
        wt.PlotDWTCoef(sig = rawsig,waveletobj = pywt.Wavelet('db2'))
        # gswt
        waveletobj = wtf.gswt_wavelet()
        wt.PlotDWTCoef(sig = rawsig,figID = 2,waveletobj = waveletobj)
