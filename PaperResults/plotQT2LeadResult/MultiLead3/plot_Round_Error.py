#encoding:utf-8
"""
Test CWT coefficients
Author : Gaopengfei
Date: 2016.6.23
"""
import os
import sys
import json
import math
import pickle
import random
import pywt
import time
import glob
import pdb
from multiprocessing import Pool

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import pi, r_
from scipy import optimize

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
sys.path.append(projhomepath)
# configure file
# conf is a dict containing keys
# my project components


class plotRoundStat:
    def __init__(self):
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        self.colors = []
        for color_tri in tableau20:
            self.colors.append((color_tri[0]/255.0,color_tri[1]/255.0,color_tri[2]/255.0))

    def plot_mean_error(self):
        EvalRoundList = glob.glob(os.path.join(curfolderpath,'EvalInfoRound*'))
        meandict = dict()
        for evalfolder in EvalRoundList:
            jsonfilepath = os.path.join(evalfolder,'ErrStat.json')
            with open(jsonfilepath,'r') as fin:
                errdict = json.load(fin)

            # get mean error
            for label,stat in errdict.iteritems():
                if label not in meandict:
                    meandict[label] = []
                meandict[label].append(stat['mean'])
        # plot mean error
        plt.figure(1)
        color_ind = 1
        for label,meanlist in meandict.iteritems():
            plt.plot(meanlist,color = self.colors[color_ind],marker = 's',label = label,markersize = 12,lw = 4,alpha = 0.8)
            color_ind += 1

        plt.grid(True)
        plt.legend()
        plt.title('mean error in each Round')
        plt.show()


    def plot_std_error(self):
        EvalRoundList = glob.glob(os.path.join(curfolderpath,'EvalInfoRound*'))
        stddict = dict()
        for evalfolder in EvalRoundList:
            jsonfilepath = os.path.join(evalfolder,'ErrStat.json')
            with open(jsonfilepath,'r') as fin:
                errdict = json.load(fin)

            # get mean error
            for label,stat in errdict.iteritems():
                if label not in stddict:
                    stddict[label] = []
                stddict[label].append(stat['std'])
        # plot mean error
        plt.figure(1)
        color_ind = 1
        for label,meanlist in stddict.iteritems():
            plt.plot(meanlist,color = self.colors[color_ind],marker = 's',label = label,markersize = 12,lw = 4,alpha = 0.8)
            color_ind += 1

        plt.grid(True)
        plt.legend()
        plt.title('std error in each Round')
        plt.show()


if __name__ == '__main__':
    roundstat = plotRoundStat()
    roundstat.plot_mean_error()
    #roundstat.plot_std_error()
