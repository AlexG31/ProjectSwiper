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
sys.path.append(projhomepath)
# configure file
# conf is a dict containing keys
# my project components
from QTdata.loadQTdata import QTloader
from EvaluationSchemes.csvwriter import CSVwriter


eps = 1e-3

debugmod = True

class whiteSamplePicker:
    def __init__(self):

        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        self.colors = []
        for color_tri in tableau20:
            self.colors.append((color_tri[0]/255.0,color_tri[1]/255.0,color_tri[2]/255.0))

    #def loadQT(self,QTrecname):
        #sig_struct = self.QTdb.load(QTrecname)
        #self.rawsig = sig_struct['sig2']
        #self.recname = QTrecname



    def show(self):
        # ====================================
        # set figure and axes
        fig = plt.figure(1)

        # two plots
        rect = 0.1,0.5,0.8,0.4
        ax = fig.add_axes(rect)

        rect2 = 0.1,0.05,0.8,0.4
        ax2 = fig.add_axes(rect2)

        ax.grid(color=(0.8,0.8,0.8), linestyle='--', linewidth=2)
        ax2.grid(color=(0.8,0.8,0.8), linestyle='--', linewidth=2)
        # ====================================

        # ====================================
        # load ECG signal

        ax.set_title('Please Press space to refresh')
        ax2.set_title('Please Press space to refresh')

        # ====================================

        browser = PointBrowser(fig,ax,ax2)

        fig.canvas.mpl_connect('pick_event', browser.onpick)
        fig.canvas.mpl_connect('key_press_event', browser.onpress)

        plt.show()

class PointBrowser(object):
    """
    Click on a point to select and highlight it -- the data that
    generated the point will be shown in the lower axes.  Use the 'n'
    and 'p' keys to browse through the next and previous points
    """


    def __init__(self,fig,ax,ax2):
        self.fig = fig
        self.ax = ax
        self.ax2 = ax2

        self.SaveFolder = os.path.join(curfolderpath,'QTwhiteMarkList')


        self.text = self.ax.text(0.05, 0.95, 'selected: none',
                            transform=self.ax.transAxes, va='top')
        #self.selected, = self.ax.plot([xs[0]], [ys[0]], 'o', ms=12, alpha=0.4,
                                 #color='yellow', visible=False)
        # ============================
        # QTdb
        self.QTdb = QTloader()
        #self.reclist = self.QTdb.reclist
        self.resultlist = glob.glob(os.path.join(projhomepath,
            'result',
            'regression-test',
            'result_*'))

        print 'len result list:', len(self.resultlist)

        self.recInd = 0
        self.recname = os.path.split(self.resultlist[self.recInd])[-1][7:]
        print 'self.recname', self.recname
        self.sigStruct = self.QTdb.load(self.recname)
        self.rawSig = self.sigStruct['sig']
        self.rawSig2 = self.sigStruct['sig2']
        self.expLabels = self.QTdb.getexpertlabeltuple(self.recname)

        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        self.colors = []
        for color_tri in tableau20:
            self.colors.append((color_tri[0]/255.0,color_tri[1]/255.0,color_tri[2]/255.0))
        # ===========================
        # Mark list
        self.whiteRegionList = []
        self.totalWhiteCount = 0

    def onpress(self, event):
        if event.key not in ('n', 'p',' ','x','a','d'):
            return

        if event.key == 'n':
            self.saveWhiteMarkList2Json()
            self.next_record()
            self.clearWhiteMarkList()

            # clear Marker List
            self.reDraw()
            return None
        elif event.key == ' ':
            self.reDraw()
            
            return None
        elif event.key == 'x':
            if len(self.whiteRegionList) > 0:
                # minus whiteCount
                self.totalWhiteCount -= abs(self.whiteRegionList[-1][1]-self.whiteRegionList[-1][0])
                del self.whiteRegionList[-1]
        elif event.key == 'a':
            step = -200
            xlims = self.ax.get_xlim()
            new_xlims = [xlims[0]+step,xlims[1]+step]
            self.ax.set_xlim(new_xlims)
            self.ax2.set_xlim(new_xlims)
        elif event.key == 'd':
            step = 200
            xlims = self.ax.get_xlim()
            new_xlims = [xlims[0]+step,xlims[1]+step]
            self.ax.set_xlim(new_xlims)
            self.ax2.set_xlim(new_xlims)
        else:
            pass

        self.update()
    def saveWhiteMarkList2Json(self):
        pass

    def clearWhiteMarkList(self):
        self.whiteRegionList = []
        self.totalWhiteCount = 0
        

    def addMarkx(self,x):
        # mark data
        if len(self.whiteRegionList) == 0 or self.whiteRegionList[-1][-1] != -1:
            startInd = int(x)
            self.whiteRegionList.append([startInd,-1])
        else:
            endInd = int(x)
            self.whiteRegionList[-1][-1] =  endInd

            # add to total white count
            # [startInd,endInd]
            #
            pair = self.whiteRegionList[-1]
            if pair[1]<pair[0]:
                self.whiteRegionList[-1] = [pair[1],pair[0]]
                pair = self.whiteRegionList[-1]

            self.totalWhiteCount += pair[1]-pair[0]+1

            # draw markers
            xlist = xrange(pair[0],pair[1]+1)
            ylist = []
            N_rawsig = len(self.rawSig)
            for xval in xlist:
                if xval>=0 and xval<N_rawsig:
                    ylist.append(self.rawSig[xval])
                else:
                    ylist.append(0)
            self.ax.plot(xlist,ylist,lw = 6,color = self.colors[0],alpha = 0.3,label = 'whiteRegion')

        
    def onpick(self, event):

        # the click locations
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata


        # add white Mark
        self.addMarkx(x)
        self.text.set_text('Marking region: ({}) [whiteCnt {}][expertCnt {}]'.format(self.whiteRegionList[-1],self.totalWhiteCount,len(self.expLabels)))

        # update canvas
        self.fig.canvas.draw()

    def reDraw(self):

        ax = self.ax
        ax.cla()
        self.ax2.cla()

        self.text = self.ax.text(0.05, 0.95, 'selected: none',
                            transform=self.ax.transAxes, va='top')
        ax.grid(color=(0.8,0.8,0.8), linestyle='--', linewidth=2)
        self.ax2.grid(color=(0.8,0.8,0.8), linestyle='--', linewidth=2)

        # ====================================
        # load ECG signal

        # ====================================
        ax.set_title('QT {} (Index = {})'.format(self.recname,self.recInd))
        ax.plot(self.rawSig, picker=5)  # 5 points tolerance

        # plot ax2
        self.ax2.set_title('Lead II')
        self.ax2.plot(self.rawSig2, picker=5)  # 5 points tolerance

        # plot Expert Labels
        self.plotExpertLabels(ax,self.rawSig)
        self.plotExpertLabels(self.ax2,self.rawSig2)
        # plot Result labels
        self.plotResultLabels(ax,0,self.rawSig)
        self.plotResultLabels(self.ax2,1,self.rawSig2)

        # update draw
        self.fig.canvas.draw()

    def update(self):

        #self.ax2.text(0.05, 0.9, 'mu=%1.3f\nsigma=%1.3f' % (xs[dataind], ys[dataind]),
                 #transform=self.ax2.transAxes, va='top')
        #self.ax2.set_ylim(-0.5, 1.5)
        

        self.fig.canvas.draw()

    def next_record(self):
        self.recInd += 1
        self.recname = os.path.split(self.resultlist[self.recInd])[-1][7:]
        self.sigStruct = self.QTdb.load(self.recname)
        self.rawSig = self.sigStruct['sig']
        self.rawSig2 = self.sigStruct['sig2']
        self.expLabels = self.QTdb.getexpertlabeltuple(self.recname)

    def plotResultLabels(self,ax,prdInd,rawSig):

        with open(self.resultlist[self.recInd],'r') as fin:
            resStruct = json.load(fin)

        resLabels = resStruct[prdInd][1]
        #get label Dict
        labelSet = set()
        labelDict = dict()
        for prediction_node in resLabels:
            # Parse prediction result
            pos,label = prediction_node[0:2]
            pos = int(pos)
            if len(prediction_node) >= 3:
                confidence  = prediction_node[2]
            else:
                confidence = None

            if label in labelSet:
                labelDict[label].append(pos)
            else:
                labelSet.add(label)
                labelDict[label] = [pos,]

        # plot to axes
        for label,posList in labelDict.iteritems():
            # plot marker for current label
            if label[0]=='T':
                color = self.colors[0]
            elif label[0]=='P':
                color  = self.colors[4]
            elif label[0]=='R':
                color  = self.colors[6]
            else:
                color  = self.colors[14]
            # marker
            if 'onset' in label:
                marker = '<'
            elif 'offset' in label:
                marker = '>'
            elif len(label) ==1:
                marker = 'o'
            else:
                marker = '.'
            ax.plot(posList,
                    map(lambda x:rawSig[x],posList),
                    marker = marker,
                    color = color,
                    linestyle = 'none',
                    markersize = 6,
                    label = 'Pred[{}]'.format(label),
                    alpha = 0.8)
        ax.legend(numpoints = 1)

    def plotExpertLabels(self,ax,rawSig):

        #get label Dict
        labelSet = set()
        labelDict = dict()
        for pos,label in self.expLabels:
            if label in labelSet:
                labelDict[label].append(pos)
            else:
                labelSet.add(label)
                labelDict[label] = [pos,]

        # plot to axes
        for label,posList in labelDict.iteritems():
            # plot marker for current label
            if label[0]=='T':
                color = self.colors[4]
            elif label[0]=='P':
                color  = self.colors[5]
            elif label[0]=='R':
                color  = self.colors[6]
            # marker
            if 'onset' in label:
                marker = '<'
            elif 'offset' in label:
                marker = '>'
            else:
                marker = 'o'
            ax.plot(posList,map(lambda x:rawSig[x],posList),marker = marker,color = color,linestyle = 'none',markersize = 14,label = label)
        ax.legend(numpoints = 1)


def get_QTdb_recordname(index = 1):
    QTdb = QTloader()
    reclist = QTdb.getQTrecnamelist()
    return reclist[index]

if __name__ == '__main__':
    tool = whiteSamplePicker()
    tool.show()
    pass
