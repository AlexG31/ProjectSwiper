#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import pdb
import bisect
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
    def PlotMarker2Label(self,label):
        if label == 'ro':
            mker = 'T wave peak'
        elif label == 'go':
            mker = 'R wave peak'
        elif label == 'bo':
            mker = 'P wave peak'
        elif label == 'r<':
            mker = 'T onset'
        elif label == 'r>':
            mker = 'T offset'
        elif label == 'g<':
            mker = 'Ronset'
        elif label == 'g>':
            mker = 'Roffset'
        elif label == 'b<':
            mker = 'Ponset'
        elif label == 'b>':
            mker = 'Poffset'
        else:# white
            mker = 'non-characteristic points'
        return mker
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
        
    def plot(self,plotTitle = None,dispRange = None,plotFig = 1,plotShow = True,AdditionalPlot = None):
        # AdditionalPlot
        # [ 
        #   [plotmarker,legend,x,(y)],
        #   ...
        # ]
        # display range
        if dispRange is not None:
            dispsig = self.rawsig[dispRange[0]:dispRange[1]]
        else:
            dispsig = self.rawsig
        # clear graph
        plt.clf()
        plt.figure(plotFig)
        plt.plot(dispsig)
        if self.testresult is not None and len(self.testresult)>0:
            if dispRange is not None:
                dispres = self.testresult
                (poslist,reslabellist) = zip(*dispres)
                resrange_L = bisect.bisect_left(poslist,dispRange[0])
                resrange_R = bisect.bisect_left(poslist,dispRange[1])
                poslist = poslist[resrange_L:resrange_R]
                reslabellist = reslabellist[resrange_L:resrange_R]
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
                    if mker == 'w.':
                        plt.plot(mkerposlist,Amplist,mker,markerfacecolor = 'b',markersize=10,label = '{}'.format(self.PlotMarker2Label(mker)))
                    else:
                        plt.plot(mkerposlist,Amplist,mker,markersize=10,label = '{}'.format(self.PlotMarker2Label(mker)))
        #=====================
        # plot AdditionalPlot
        #=====================
        if AdditionalPlot is not None:
            for plotElem in AdditionalPlot:
                plotElem_x = plotElem[2]
                if len(plotElem) == 3:
                    plotElem_y = map(lambda x:dispsig[int(x)],plotElem_x)            
                elif len(plotElem) == 4:
                    plotElem_y = plotElem[3]
                else:
                    raise Exception('len(plotElem) should be 3 or 4!')
                # plot 
                plt.plot(plotElem_x,plotElem_y,plotElem[0],markersize = 10,label = plotElem[1])
        if plotTitle is not None:
            plt.title(plotTitle)
        # show legend
        plt.legend(numpoints = 1)
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        if plotShow is True:
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
