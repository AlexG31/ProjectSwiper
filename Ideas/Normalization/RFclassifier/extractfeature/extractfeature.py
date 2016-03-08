"""
This is ECG feature extractor class
Aiming to extract feature for training and classification

Author: Gaopengfei
"""

#encoding:utf-8
import os
import sys
import json
import math
import pdb

import matplotlib.pyplot as plt
import numpy as np

# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(projhomepath)
projhomepath = os.path.dirname(projhomepath)

# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
import WTdenoise.wtdenoise as wtdenoise
import WTdenoise.wtfeature as wtf

EPS = 1e-6

class ECGfeatures:
    ## Common Feature extractor for ECG classifier
    #
    def __init__(\
                self,\
                rawsig,\
                isdenoised = False\
            ):
        if not isinstance(rawsig,list):
            raise StandardError('Input rawsig is not a list type![WTdenoise]')

        #
        # first denoise 
        #
        if isdenoised == False:
            self.sig = ECGfeatures.signal_preprocessing(rawsig)
        else:
            self.sig = rawsig
        self.rawsig = rawsig
        # new normalization method
        if conf['Normalization_type'] == 'mean_std':
            self.sig = ECGfeatures.Normalization_meanstd(self.sig)
            self.rawsig = ECGfeatures.Normalization_meanstd(self.rawsig)
        
    @staticmethod
    def Normalization_meanstd(rawsigin):
        # mean - std normalization
        mean = np.nanmean(rawsigin)
        std = np.nanstd(rawsigin)
        if std is None or mean is None:
            raise StandardError('Normalization: mean or std is None!')
        if std == 0:
            raise StandardError('Normalization: std is 0!')
        normsig = [(x-mean)/std for x in rawsigin]
        return normsig

    @staticmethod
    def signal_preprocessing(rawsig):
        # wavelet denoise:
        sig = wtdenoise.denoise(rawsig)

        return sig

    def frompos(self,pos):
        feature_type = conf['feature_type']
        if feature_type == 'wavelet':
            return self.getWTfeatureforpos(pos)
        elif feature_type == 'wavelet_normal':
            return self.getWTfeatureforpos(pos,WithNormalPairFeature = True)
        else:
            return self.getfeatureforposition(pos,debug = 'none')

    def getfeatureforposition(self,x,debug = 'none'):
        x = int(x)
        if x<0 or x >= len(self.sig):
            print 'Error:'
            print 'x = {}'.format(x)
            print 'length of sig:{}'.format(len(self.sig))
            raise StandardError('input position x must in range of sig indexs!')
        denoisesig = self.sig

        # Windowed signal
        winsig = self.getWindowedSignal(x,denoisesig)

        # winsig:
        # normalization
        #
        normwinsig = winsig
        if conf['Normalization_type'] != 'mean_std':
            Ampmax = max(winsig)
            Ampmin = min(winsig)
            sig_height = float(Ampmax-Ampmin)
            if sig_height <= EPS:
                sig_height = 1
            normwinsig = [x/sig_height for x in winsig]

        # ================================
        # debug plot
        # ================================
        if debug == 'plot':
            plt.figure(1)
            plt.plot(normwinsig)
            # plot center point
            x_c = len(normwinsig)/2
            plt.plot(x_c,normwinsig[x_c],'ro')
            plt.show()

        # extract feature
        with open(os.path.join(curfolderpath,'ECGrandrel.json'),'r') as fin:
            rels = json.load(fin)
        # all random
        features = [normwinsig[x[0]]-normwinsig[x[1]] for x in rels]
        features.extend([abs(normwinsig[x[0]]-normwinsig[x[1]]) for x in rels])
        
        return features
    
    def getWindowedSignal(self,x,sig):
        # get windowed signal from original signal
        # padding zeros if near boundaries
        fs = conf['fs']
        FixedWindowLen = conf['winlen_ratio_to_fs']*fs
        winlen_hlf = int(FixedWindowLen/2)
        # 
        winsig = []
        if x <winlen_hlf:
            winsig.extend([0]*(winlen_hlf-x))
            winsig.extend(sig[0:x])
        else:
            winsig.extend(sig[x-winlen_hlf:x])
        if x+winlen_hlf >= len(sig):
            winsig.extend(sig[x:])
            winsig.extend([0]*(len(sig)-winlen_hlf-x+1))
        else:
            winsig.extend(sig[x:x+winlen_hlf+1])
        return winsig

        
    def getWTfeatureforpos(self,pos,WithNormalPairFeature = False):
        pos = int(pos)
        if pos<0 or pos >= len(self.rawsig):
            raise StandardError(\
                    'input position posx must in range of sig indexs!')
        rawsig = self.rawsig
        
        # ====================================
        # windowed signal
        winsig = self.getWindowedSignal(pos,rawsig)

        # ====================================
        # winsig:
        # normalization
        #
        normwinsig = winsig
        if conf['Normalization_type'] == 'mean_std':
            Ampmax = max(winsig)
            Ampmin = min(winsig)
            sig_height = float(Ampmax-Ampmin)
            if sig_height <= EPS:
                sig_height = 1
            normwinsig = [val/sig_height for val in winsig]

        # ====================================
        # all random
        #
        features = []
        if WithNormalPairFeature == True:
            features = self.getfeatureforposition(pos)
        # ====================================
        # WT features
        #
        wtfobj = wtf.WTfeature()
        dslist = wtfobj.getWTcoef_gswt(normwinsig)
        # load Random Relations
        WTrrJsonFileName = os.path.join(curfolderpath,'WTcoefrandrel.json')
        
        with open(WTrrJsonFileName,'r') as fin:
            WTrelList = json.load(fin)
        for detailsignal,randrels in zip(dslist,WTrelList):
            fv = [detailsignal[x[0]] - detailsignal[x[1]] for x in randrels]
            features.extend(fv)
            fv = [abs(detailsignal[x[0]] - detailsignal[x[1]]) for x in randrels]
            features.extend(fv)
        
        return features


## for multiProcess
def frompos_with_denoisedsig(Params):
    # 
    # map function should have only 1 Param
    # ,so I wrapped two parameters into one
    #
    denoisedsig,pos = Params
    fvExtractor = ECGfeatures(denoisedsig,isdenoised = True)
    return fvExtractor.frompos(pos)


