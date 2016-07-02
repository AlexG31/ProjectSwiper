#encoding:utf-8
"""
ECG classification with Random Forest
Author : Gaopengfei
"""
import os
import sys
import json
import math
import pickle
import bisect
import random
import time
import pdb
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = curfolderpath
projhomepath = os.path.dirname(projhomepath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import extractfeature.extractfeature as extfeature
import extractfeature.randomrelations as RandRelation
import WTdenoise.wtdenoise as wtdenoise
from QTdata.loadQTdata import QTloader

## Main Scripts
# ==========
class pickNegtiveSample(object):
    def __init__(self):
        self.QTdb = QTloader()
        self.whiteRegionFolder = r'F:\LabGit\ECG_RSWT\QTdata\QTwhiteMarkList'
        self.MaxNegCnt = 40
        pass
    def getNegList4rec(self,recname):
        '''Pick Negtive samples from the ranges.'''
        with open(os.path.join(self.whiteRegionFolder,'{}_whiteRegionList.json'.format(recname)),'r') as fin:
            whiteList = json.load(fin)
        NegList = []
        for pair in whiteList:
            NegList.extend(range(pair[0],pair[1]+1))

        # choose neg list
        if len(NegList)<=self.MaxNegCnt:
            return NegList
        else:
            # random sample
            return random.sample(NegList,self.MaxNegCnt)

    def getRandomNegSamples(self,recname):
        '''Randomly select Negtive samples from ranges, but keep a minimum distance from the Expert Labels.'''
        # ------------------
        # keep out region dist
        KeepoutDist = 10

        with open(os.path.join(self.whiteRegionFolder,'{}_whiteRegionList.json'.format(recname)),'r') as fin:
            contRangeList = json.load(fin)

        expList = self.QTdb.getexpertlabeltuple(recname)
        expPoslist,expLabellist = zip(*expList)
        expPoslist = list(expPoslist)
        expPoslist.sort()

        # get all continous ranges
        RawPosList = []
        for contPair in contRangeList:
            RawPosList.extend(range(contPair[0],contPair[1]+1))

        # get possible neglist
        NegList = []
        for cPos in RawPosList:
            # find the closest expPos
            InsertInd = bisect.bisect_left(expPoslist,cPos)
            if InsertInd ==0:
                expPos = expPoslist[InsertInd]
            elif InsertInd == len(expPoslist):
                expPos = expPoslist[-1]
            else:
                expPos = expPoslist[InsertInd]
                if abs(expPoslist[InsertInd-1]-cPos) < abs(expPos-cPos):
                    expPos = expPoslist[InsertInd-1]

            curdist = abs(expPos-cPos)

            # add to neglist
            if curdist>= KeepoutDist:
                NegList.append(cPos)

        # =========================
        # choose neglist
        selNeglist = []
        if self.MaxNegCnt>=len(NegList):
            selNeglist = NegList
        else:
            selNeglist = random.sample(NegList,self.MaxNegCnt)

        if len(selNeglist) == 0:
            raise Exception('selNeglist is empty!')
                    
        return selNeglist


if __name__ == '__main__':
    picker = pickNegtiveSample()
    #neglist = picker.getNegList4rec('sel100')
    neglist = picker.getRandomNegSamples('sel114')
    print 
    print 'len of neglist:',len(neglist)
    print neglist


    reclist = picker.QTdb.getQTrecnamelist()
    for recname in reclist:
        neglist = picker.getRandomNegSamples(recname)
        print recname,':',len(neglist)
        print neglist
        pdb.set_trace()


