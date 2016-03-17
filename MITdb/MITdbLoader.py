#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import matplotlib.pyplot as plt
import numpy as np
import pdb
import logging
import bisect


# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)

class MITdbLoader:
    def __init__(self,datafolderpath = None):
        if datafolderpath is None:
            datafolderpath = os.path.join(curfolderpath,'pydata')
        self.datafolderpath = datafolderpath
        self.recIDlist = []
        # MITdb data :
        self.sigd1 = []
        self.sigd2 = []
        self.time = []
        self.markpos = []
        self.marklabel = []
        # ID info
        self.recID = None

    def load(self,recID):
        self.recID = recID
        with open(os.path.join(self.datafolderpath,'{}_sig1'.format(recID)),'r') as fin:
            self.sigd1 = pickle.load(fin)
        with open(os.path.join(self.datafolderpath,'{}_sig2'.format(recID)),'r') as fin:
            self.sigd2 = pickle.load(fin)
        with open(os.path.join(self.datafolderpath,'{}_time'.format(recID)),'r') as fin:
            self.time = pickle.load(fin)
        with open(os.path.join(self.datafolderpath,'{}_markpos'.format(recID)),'r') as fin:
            self.markpos = pickle.load(fin)
        with open(os.path.join(self.datafolderpath,'{}_marklabel'.format(recID)),'r') as fin:
            self.marklabel = pickle.load(fin)
        # convert mark position format
        self.convertLabelpos()
        # return lead1 signal
        return self.sigd1
        
    def getRecIDList(self):
        filelist = glob.glob(os.path.join(self.datafolderpath,'*_time'))
        filelist = map(lambda x:os.path.split(x)[-1],filelist)
        self.recIDlist = map(lambda x:x[0:len(x)-5],filelist)
        return self.recIDlist
    def convertLabelpos(self):
        # warning:only use once:after loading the data
        for mi,mpos in enumerate(self.markpos):
            # find mpos in self.time
            cvt_ind = bisect.bisect_left(self.time,mpos)
            self.markpos[mi] = cvt_ind
            
    def savetoimage(self,xLim = 1000,savefolder = ur'img'):
        plt.figure(num = 1,figsize = (20,10))
        # plot signal leads
        plt.plot(self.sigd1[0:xLim],'b-')
        plt.plot(self.sigd2[0:xLim],'r-')
        # annotate
        meanAmp = np.nanmean(self.sigd1[0:xLim])
        for mi,mpos in enumerate(self.markpos):
            if mi>= xLim:
                break
            mpos = int(mpos)
            plt.annotate(s = self.marklabel[mi],xy = (mpos,meanAmp))
        plt.title('MITdb record: {}'.format(self.recID))
        plt.savefig(os.path.join(savefolder,'{}.png'.format(self.recID)))
        plt.clf()



if __name__ == "__main__":
    pdb.set_trace()
    mit = MITdbLoader()
    IDlist = mit.getRecIDList()
    for recID in IDlist:
        logging.warning('loading:{}'.format(recID))
        mit.load(recID)
        mit.savetoimage()
        pdb.set_trace()
    
