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
from QTdata.loadQTdata import QTloader
from EvaluationSchemes.csvwriter import CSVwriter


eps = 1e-3

debugmod = True

class ShowColors:
    def __init__(self):

        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        self.colors = []
        for color_tri in tableau20:
            self.colors.append((color_tri[0]/255.0,color_tri[1]/255.0,color_tri[2]/255.0))

    def show(self):
        #position array
        xlist = [1,2,3,4,5]*4
        ylist = [1,2,3,4]*5

        plt.figure(1)
        for ind,(xpos,ypos) in enumerate(zip(xlist,ylist)):
            plt.plot(xpos,ypos,marker = 's',markersize = 34,color = self.colors[ind],linestyle = 'none',label = 'color {}'.format(ind))
        plt.xlim(0,6)
        plt.ylim(0,5)
        plt.legend(numpoints = 1)
        plt.show()

if __name__ == '__main__':
    tool = ShowColors()
    tool.show()
