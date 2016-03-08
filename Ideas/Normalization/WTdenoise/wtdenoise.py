#encoding:utf-8
import pywt
import os
import codecs
import numpy as np

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

