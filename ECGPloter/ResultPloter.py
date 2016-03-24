#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import pdb
import matplotlib.pyplot as plt

# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

#import QTdata.loadQTdata.QTloader as QTloader
from QTdata.loadQTdata import QTloader 
from RFclassifier.ECGRF import ECGrf as ECGRF
from RFclassifier.evaluation import ECGstatistics as ECGstats

class ECGResultPloter:
    def __init__(self,rawsig,testresult = None):
        self.rawsig = rawsig
        self.testresult = testresult
        self.plotMarkerlist = [
                'ro',
                'go',
                'bo',
                'r<',
                'r>',
                'g<',
                'g>',
                'b<',
                'b>',
                'w.']
        pass
    def Label2PlotMarker(self,label):
        if label == 'T':
            mker = 'ro'
        elif label == 'R':
            mker = 'go'
        elif label == 'P':
            mker = 'bo'
        elif label == 'Tonset':
            mker = 'r<'
        elif label == 'Toffset':
            mker = 'r>'
        elif label == 'Ronset':
            mker = 'g<'
        elif label == 'Roffset':
            mker = 'g>'
        elif label == 'Ponset':
            mker = 'b<'
        elif label == 'Poffset':
            mker = 'b>'
        else:# white
            mker = 'w.'
        return mker
        
    def plot(self,plotTitle = None,dispRange = None):
        # display range
        if dispRange is not None:
            dispsig = self.rawsig[dispRange[0]:dispRange[1]]
        else:
            dispsig = self.rawsig
        # clear graph
        plt.clf()
        plt.figure(1)
        plt.plot(dispsig)
        print 'raw sig None?'
        pdb.set_trace()
        if self.testresult is not None and len(self.testresult)>0:
            if dispRange is not None:
                dispres = self.testresult[dispRange[0]:dispRange[1]]
            else:
                dispres = self.testresult
            # convert labels to plot markers
            (poslist,reslabellist) = zip(*dispres)
            resplotmarkerlist = map(self.Label2PlotMarker,reslabellist)
            for mker in self.plotMarkerlist:
                mkerposlist = []
                Amplist = []
                for mi,resmker in enumerate(resplotmarkerlist):
                    if resmker == mker:
                        if dispRange is None:
                            mkerpos = poslist[mi]
                        else:
                            mkerpos = poslist[mi] - dispRange[0]
                        mkerposlist.append(mkerpos)
                        # poslist is signal global index
                        Amplist.append(dispsig[mkerpos])
                if len(mkerposlist)>0:
                    # have avaliable mker to plot
                    plt.plot(mkerposlist,Amplist,mker)
        if plotTitle is not None:
            plt.title(plotTitle)
        plt.show()
    def plotAndsave(self,savefilefullpath,plotTitle = None,dispRange = None):
        # display range
        if dispRange is not None:
            dispsig = self.rawsig[dispRange[0]:dispRange[1]]
        else:
            dispsig = self.rawsig
        plt.figure(num = 1,figsize = (20,10))
        plt.plot(dispsig)
        if self.testresult is not None:
            if dispRange is not None:
                dispres = self.testresult[dispRange[0]:dispRange[1]]
            else:
                dispres = self.testresult
            # convert labels to plot markers
            (poslist,reslabellist) = zip(*dispres)
            resplotmarkerlist = map(self.Label2PlotMarker,reslabellist)
            for mker in self.plotMarkerlist:
                mkerposlist = []
                Amplist = []
                for mi,resmker in enumerate(resplotmarkerlist):
                    if resmker == mker:
                        if dispRange is None:
                            mkerpos = poslist[mi]
                        else:
                            mkerpos = poslist[mi] - dispRange[0]
                        mkerposlist.append(mkerpos)
                        # poslist is signal global index
                        Amplist.append(dispsig[mkerpos])
                if len(mkerposlist)>0:
                    # have avaliable mker to plot
                    plt.plot(mkerposlist,Amplist,mker)
            if plotTitle is not None:
                plt.title(plotTitle)
            plt.savefig(savefilefullpath+'.png')
        # clear graph
        plt.clf()
