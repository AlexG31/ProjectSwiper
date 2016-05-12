#encoding:utf-8
"""
Feature Visualization
Author : Gaopengfei
"""
import os
import sys
import json
import math
import pickle
import random
import time
import pywt
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
projhomepath = os.path.dirname(projhomepath)

# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import RFclassifier.extractfeature.randomrelations as RandRelation
import WTdenoise.wtdenoise as wtdenoise
from WTdenoise.wtfeature import WTfeature
from QTdata.loadQTdata import QTloader 

## Main Scripts
# ==========
EPS = 1e-6



class FeatureVis:
    def __init__(self,rfmdl,RandomPairList_Path):
        # get random relations
        randrel_path = RandomPairList_Path
        with open(randrel_path,'r') as fin:
            self.randrels = json.load(fin)

        self.rfmdl = rfmdl
        self.trees = rfmdl.estimators_
        self.qt = QTloader()
        self.qt_reclist = self.qt.getQTrecnamelist()
    def info(self):
        t0 = self.trees[0]
        # list dir
        for attr in dir(t0):
            print attr
        print 'tree-------------------------'
        for attr in dir(t0.tree_):
            print attr

        pdb.set_trace()
    def get_pair_importance_list(self):
        return self.feature_importance_test()
    def feature_importance_test(self):
        # return pairs&their importance
        rID = 1
        sig = self.qt.load(self.qt_reclist[rID])
        # random relations 
        randrels = self.randrels
        fimp = self.rfmdl.feature_importances_
        sum_rr = 0
        for rr in randrels:
            sum_rr += len(rr)
        print 'len(feature importance) = {},len(random relations) = {}'.format(len(fimp),sum_rr)
        # ===========================
        # get a struct of importance:
        # ------------
        # [#layer0:[((23,2),0.2# importance),((pair),#importance),()...],#layer1:[],..]
        # 
        cur_feature_ind = 0
        relation_importance = []
        for rel_layer in randrels:
            layerSZ = len(rel_layer)
            diff_arr = fimp[cur_feature_ind:cur_feature_ind+layerSZ]
            absdiff_arr = fimp[cur_feature_ind+layerSZ:cur_feature_ind+2*layerSZ]
            imp_arr = map(lambda x:max(x[0],x[1]),zip(diff_arr,absdiff_arr))
            relation_importance.append(zip(rel_layer,imp_arr))
            print 'layer len = {}'.format(len(imp_arr))
            cur_feature_ind += 2*layerSZ

        return relation_importance
    def plot_dwt_pairs_arrow_partial_window_compare(self,rawsig,relation_importance,Window_Left = 1200,savefigname = None,figsize = (10,8),figtitle = 'ECG Sample',showFigure = True):
        ## =========================================V    
        # 展示RSWT示意图
        ## =========================================V    
        #
        #================
        # constants
        #================
        N = 5
        figureID = 1
        fs = conf['fs']
        FixedWindowLen = conf['winlen_ratio_to_fs']*fs
        print 'Fixed Window Length:{}'.format(FixedWindowLen)
        xL = Window_Left
        xR = xL+FixedWindowLen
        tarpos  = 1500
        # props of ARROW
        arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        # -----------------
        # get median
        # -----------------
        importance_arr = []
        for rel_layer in relation_importance:
            for rel,imp in rel_layer:
                importance_arr.append(imp)
        N_imp = len(importance_arr)
        # ascending order:0->1
        importance_arr.sort()
        IMP_Thres = importance_arr[int(N_imp/2)]
        IMP_MAX = importance_arr[-1]
        # get wavelet obj
        # dwt coef 
        dwtECG = WTfeature()
        waveletobj = dwtECG.gswt_wavelet() 
        # props of ARROW
        #arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        Fig_main = plt.figure(figureID,figsize = figsize)
        # plot raw ECG
        plt.subplot(N+1,2,1)
        # get handle for annote arrow
        # hide axis
        #frame = plt.gca()
        #frame.axes.get_xaxis().set_visible(False)
        #frame.axes.get_yaxis().set_visible(False)
        plt.plot(pltxLim,sigAmp)
        # plot reference point
        #plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title('Window the signal before DWT')
        #plt.xlim(pltxLim)
        # ===========Col2=================
        plt.subplot(N+1,2,2)
        plt.plot(pltxLim,sigAmp)
        cA_col2 = cA[xL:xR]
        plt.title('Window the signal after DWT')
        

        for i in range(2,N+2):
            # ====================
            # subplot col2
            # ====================
            cA_col2,cD_col2 = pywt.dwt(cA_col2,waveletobj)
            plt.subplot(N+1,2,i*2-1)
            plt.plot(cA_col2)
            # relation&importance
            rel_layer = relation_importance[i-2]
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            # crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # get relation points
            rel_x = []
            rel_y = []
            cur_N = len(cDamp)
            # ------------
            # sub plot 
            # ------------
            # plot 
            fig = plt.subplot(N+1,2,2*i)
            #------------
            # find pair&its amplitude
            # -----------
            for rel_pair,imp in rel_layer:
                # importance thres
                arrowprops = dict(width = 1,headwidth = 4,facecolor='r',edgecolor = 'r',alpha = imp/IMP_MAX,shrink=0)

                rel_x.append(rel_pair[0])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_pair[0]])
                rel_x.append(rel_pair[1])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_x[-1]])
                fig.annotate('', xy=(rel_x[-2],rel_y[-2]), xytext=(rel_x[-1],rel_y[-1]),arrowprops=arrowprops)

            #plt.grid(True)
            plt.plot(rel_x,rel_y,'.b')
            plt.plot(cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(0,len(cDamp)-1)
            plt.title('DWT Level ({}):'.format(i-1))
        # plot result
        if showFigure == True:
            plt.show()
        # save fig
        if savefigname is not None:
            Fig_main.savefig(savefigname,dpi = Fig_main.dpi)
            Fig_main.clf()
    def get_min_Importance_threshold(self,relation_importance,top_importance_ratio = 9.0/10):
        if relation_importance == None or len(relation_importance) == 0:
            raise Exception('relation_importance is empty!')
        imp_list = []
        for layer in relation_importance:
            # unzip the lists
            pairs,imps = zip(*layer)
            imp_list.extend(imps)
        # get the min_importance threshold
        N = len(imp_list)
        midpos = int(top_importance_ratio*float(N))
        imp_list.sort()
        return imp_list[midpos]

    def plot_dwt_pairs_arrow(self,rawsig,relation_importance,Window_Left = 1200,savefigname = None,figsize = (10,8),figtitle = 'ECG Sample',showFigure = True):
        ## =========================================V    
        # 展示RSWT示意图
        # Plot Arrow
        ## =========================================V    
        #
        #================
        # constants
        #================
        N = 5
        N_subplot = N+2
        # importance pairs lower than this threshold is not shown in the figure
        Thres_min_importance = self.get_min_Importance_threshold(relation_importance)
        figureID = 1
        fs = conf['fs']
        FixedWindowLen = conf['winlen_ratio_to_fs']*fs
        print 'Fixed Window Length:{}'.format(FixedWindowLen)
        xL = Window_Left
        xR = xL+FixedWindowLen
        tarpos  = 1500
        # props of ARROW
        arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        # -----------------
        # get median
        # -----------------
        importance_arr = []
        for rel_layer in relation_importance:
            for rel,imp in rel_layer:
                importance_arr.append(imp)
        N_imp = len(importance_arr)
        # ascending order:0->1
        importance_arr.sort()
        IMP_Thres = importance_arr[int(N_imp/2)]
        IMP_MAX = importance_arr[-1]
        # get wavelet obj
        # dwt coef 
        dwtECG = WTfeature()
        waveletobj = dwtECG.gswt_wavelet() 
        # props of ARROW
        #arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        Fig_main = plt.figure(figureID,figsize = figsize)
        # plot raw ECG
        plt.subplot((N_subplot + 1)/2,2,1)
        # get handle for annote arrow
        # hide axis
        #frame = plt.gca()
        #frame.axes.get_xaxis().set_visible(False)
        #frame.axes.get_yaxis().set_visible(False)
        plt.plot(pltxLim,sigAmp)
        # plot reference point
        #plt.plot(tarpos,rawsig[tarpos],'ro')
        #plt.title(figtitle+'[Window Left = {}]'.format(Window_Left))
        plt.title(figtitle)
        plt.xlim(pltxLim[0],pltxLim[-1])

        for i in range(2,N_subplot):
            # relation&importance
            rel_layer = relation_importance[i-2]
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            # crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # get relation points
            rel_x = []
            rel_y = []
            cur_N = len(cDamp)
            # ------------
            # sub plot 
            # ------------
            #fig = plt.subplot(N+1,1,i)
            fig = plt.subplot((N_subplot + 1)/2,2,i)
            plt.title('DWT Detail Coefficient {}'.format(i-1))
            #------------
            # find pair&its amplitude
            # -----------
            # sort rel_layer with imp
            rel_layer.sort(key = lambda x:x[1])
            for rel_pair,imp in rel_layer:
                # do not show imp lower than threshold
                if imp<Thres_min_importance:
                    continue 
                # importance thres
                alpha = (imp-Thres_min_importance)/(IMP_MAX-Thres_min_importance)
                arrow_color = self.get_RGB_from_Alpha((1,0,0),alpha,(1,1,1))
                arrowprops = dict(width = 0.15,linewidth = 0.15,headwidth = 1.5,headlength = 1.5,facecolor=arrow_color,edgecolor = arrow_color,shrink=0)

                rel_x.append(rel_pair[0])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_pair[0]])
                rel_x.append(rel_pair[1])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_x[-1]])
                fig.annotate('', xy=(rel_x[-2],rel_y[-2]), xytext=(rel_x[-1],rel_y[-1]),arrowprops=arrowprops)

            #plt.grid(True)
            plt.plot(rel_x,rel_y,'.b')
            plt.plot(cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(0,len(cDamp)-1)
        # plot Approximation Level
        rel_x = []
        rel_y = []
        rel_layer = relation_importance[-1]
        #fig = plt.subplot((N_subplot + 1)/2,2,N_subplot)
        fig = plt.subplot(4,1,4)
        plt.title('Approximation Coefficient')
        cAamp = [cA[x] for x in xi]
        # sort rel_layer with imp
        rel_layer.sort(key = lambda x:x[1])
        for rel_pair,imp in rel_layer:
            # do not show imp lower than threshold
            if imp<Thres_min_importance:
                continue
            # importance thres
            alpha = (imp-Thres_min_importance)/(IMP_MAX-Thres_min_importance)
            arrow_color = self.get_RGB_from_Alpha((1,0,0),alpha,(1,1,1))
            #arrowprops = dict(width = 1,headwidth = 4,facecolor=arrow_color,edgecolor = arrow_color,shrink=0)
            arrowprops = dict(width = 0.15,linewidth = 0.15,headwidth = 1.5,headlength = 1.5,facecolor=arrow_color,edgecolor = arrow_color,shrink=0)

            rel_x.append(rel_pair[0])
            if rel_x[-1] >= cur_N:
                rel_y.append(0)
            else:
                rel_y.append(cAamp[rel_pair[0]])
            rel_x.append(rel_pair[1])
            if rel_x[-1] >= cur_N:
                rel_y.append(0)
            else:
                rel_y.append(cAamp[rel_x[-1]])
            fig.annotate('', xy=(rel_x[-2],rel_y[-2]), xytext=(rel_x[-1],rel_y[-1]),arrowprops=arrowprops)

        # reference point
        plt.plot(rel_x,rel_y,'.b')
        plt.plot(cAamp)
        plt.xlim(0,len(cAamp)-1)

        # plot result
        if showFigure == True:
            plt.show()
        # save fig
        if savefigname is not None:
            Fig_main.savefig(savefigname,dpi = Fig_main.dpi)
            Fig_main.clf()
    def get_RGB_from_Alpha(self,color,alpha,bgcolor):
        new_color = []
        for color_elem,bg_color_elem in zip(color,bgcolor):
            color_elem = float(color_elem)
            bg_color_elem = float(bg_color_elem)
            ncolor = (1.0-alpha)*bg_color_elem+alpha*color_elem
            new_color.append(ncolor)
        return new_color
    def plot_dwt_pairs_no_arrow(self,rawsig,relation_importance):
        ## =========================================V    
        # 展示RSWT示意图
        # No Arrow, only points
        ## =========================================V    
        N = 5
        figureID = 1
        fs = conf['fs']
        FixedWindowLen = conf['winlen_ratio_to_fs']*fs
        print 'Fixed Window Length:{}'.format(FixedWindowLen)
        xL = 1000
        xR = xL+FixedWindowLen
        tarpos  = 1500
        # -----------------
        # get median
        # -----------------
        importance_arr = []
        for rel_layer in relation_importance:
            for rel,imp in rel_layer:
                importance_arr.append(imp)
        N_imp = len(importance_arr)
        # ascending order:0->1
        importance_arr.sort()
        IMP_Thres = importance_arr[int(N_imp/2)]
        # get wavelet obj
        # dwt coef 
        dwtECG = WTfeature()
        waveletobj = dwtECG.gswt_wavelet() 
        # props of ARROW
        #arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        plt.figure(figureID)
        # plot raw ECG
        plt.subplot(N+1,1,1)
        # get handle for annote arrow
        # hide axis
        #frame = plt.gca()
        #frame.axes.get_xaxis().set_visible(False)
        #frame.axes.get_yaxis().set_visible(False)
        plt.plot(pltxLim,sigAmp)
        # plot reference point
        #plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title('ECG sample')
        #plt.xlim(pltxLim)

        for i in range(2,N+2):
            # relation&importance
            rel_layer = relation_importance[i-2]
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            # crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # get relation points
            rel_x = []
            rel_y = []
            cur_N = len(cDamp)
            for rel_pair,imp in rel_layer:
                rel_x.append(rel_pair[0])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_pair[0]])
                rel_x.append(rel_pair[1])
                if rel_x[-1] >= cur_N:
                    rel_y.append(0)
                else:
                    rel_y.append(cDamp[rel_x[-1]])
            # plot 
            fig = plt.subplot(N+1,1,i)

            #plt.grid(True)
            plt.plot(rel_x,rel_y,'.b')
            plt.plot(cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(0,len(cDamp)-1)
            plt.title('DWT Level ({}):'.format(i-1))
        # plot result
        plt.show()

    def plot_fv_importance(self):
        # cycling plot importance of list of positions
        rID = 2
        sig = self.qt.load(self.qt_reclist[rID])
        rel_imp = self.feature_importance_test()
        # save current fig
        for i in xrange(0,130,10):
            savefigname = os.path.join(curfolderpath,'range_{}.png'.format(i))
            self.plot_dwt_pairs_arrow(sig['sig'],rel_imp,Window_Left = 1180+i,savefigname = savefigname,figsize = (20,18),figtitle = 'Window Start[{}]'.format(i))
    def plot_fv_importance_gswt(self,savefigname,showFigure,WindowLeftBias = 0):
        # QT record ID
        rID = 1
        sig = self.qt.load(self.qt_reclist[rID])
        # get layers of list [pair,importance]
        # ----
        # Format:
        # [[(pair,importance),...],# layer 1
        # [...],# layer 2
        # ,]
        # ----
        rel_imp = self.get_pair_importance_list()
        # save current fig
        #self.plot_dwt_pairs_arrow_partial_window_compare(sig['sig'],rel_imp,Window_Left = 54100+i,savefigname = savefigname,figsize = (20,18),figtitle = 'Window Start[{}]'.format(i))
        figtitle = 'ECG from QTdb Record {}'.format(self.qt_reclist[rID])
        self.plot_dwt_pairs_arrow(sig['sig'],rel_imp,Window_Left = 54100+WindowLeftBias,savefigname = savefigname,figsize = (20,18),figtitle = figtitle,showFigure = showFigure)


    def load_sig_test(self):
        pass
        rID = 1
        sig = self.qt.load(self.qt_reclist[rID])
        # random relations 
        randrel_path = os.path.join(curfolderpath,'rand_relations.json')
        with open(randrel_path,'r') as fin:
            randrels = json.load(fin)
        pdb.set_trace()
        # get rand positions and WT coef
        dslist = wtfobj.getWTcoef_gswt(normwinsig)
        for detailsignal,randrels in zip(dslist,WTrelList):
            # debug:
            for x in randrels:
                for xval in x:
                    if xval<0 or xval >= len(detailsignal):
                        print 'x = ',x
                        pdb.set_trace()

            fv = [detailsignal[x[0]] - detailsignal[x[1]] for x in randrels]
            features.extend(fv)
            fv = [abs(detailsignal[x[0]] - detailsignal[x[1]]) for x in randrels]
            features.extend(fv)
        # todo..
        waveletobj = dwtECG.gswt_wavelet() 
        self.plot_dwt_rswt(sig['sig'],waveletobj = waveletobj,ECGrecordname = recname,auto_plot = True)

    def plot_dwt_rswt(self):
        ## =========================================V    
        # 展示RSWT示意图
        ## =========================================V    
        N = 5
        xL,xR = 1000,1600
        tarpos  = 1500
        # props of ARROW
        arrowprops = dict(width = 1,headwidth = 4,facecolor='black', shrink=0)
        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]
        cA = rawsig
        # ====================
        # plot raw signal input
        # ====================
        plt.figure(figureID)
        # plot raw ECG
        plt.subplot(N+1,1,1)
        # get handle for annote arrow
        # hide axis
        frame = plt.gca()
        frame.axes.get_xaxis().set_visible(False)
        frame.axes.get_yaxis().set_visible(False)
        plt.plot(pltxLim,sigAmp)
        # plot reference point
        #plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title('ECG sample')
        #plt.xlim(pltxLim)

        for i in range(2,N+2):
            cA,cD = pywt.dwt(cA,waveletobj)
            xL/=2
            xR/=2
            tarpos/=2
            # crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # plot 
            fig = plt.subplot(N+1,1,i)
            # get max
            amp_max = cDamp[0]
            amp_min = cDamp[0]
            for cval in cDamp:
                amp_max = max(amp_max,cval)
                amp_min = min(amp_min,cval)
            # left pair
            lpairtail = [len(cDamp)*0.3,amp_min+(amp_max-amp_min)*0.8]
            L,R = int(len(cDamp)*0.1),int(len(cDamp)*0.4)
            rspairhead = (random.randint(L,R-1),random.randint(L+1,R))
            lpairtail[0] = int((rspairhead[0]+rspairhead[1])/2)
            # debug print
            #print 'left pair tail:',lpairtail
            #print 'rand selected pair head:', rspairhead
            #print 'rs height:',cDamp[int(rspairhead[0])],cDamp[int(rspairhead[1])]
            plt.text(lpairtail[0],lpairtail[1],'pair({}a)'.format(i-1))
            color = '#fe3b8d'
            arrowprops = dict(width = 1,headwidth = 4,facecolor=color,edgecolor = color, shrink=0)
            fig.annotate('', xy=(rspairhead[0],cDamp[int(rspairhead[0])]), xytext=lpairtail,arrowprops=arrowprops)
            fig.annotate('', xy=(rspairhead[1],cDamp[int(rspairhead[1])]), xytext=lpairtail,arrowprops=arrowprops)
            # right pair
            rpairtail = [len(cDamp)*0.7,amp_min+(amp_max-amp_min)*0.8]
            L,R = int(len(cDamp)*0.3),int(len(cDamp)*0.8)
            rspairhead = (random.randint(L,R-1),random.randint(L+1,R))
            rpairtail[0] = int((rspairhead[0]+rspairhead[1])/2)
            # debug print
            #print 'left pair tail:',lpairtail
            #print 'rand selected pair head:', rspairhead
            #print 'rs height:',cDamp[int(rspairhead[0])],cDamp[int(rspairhead[1])]
            plt.text(rpairtail[0],rpairtail[1],'pair({}b)'.format(i-1))
            arrowprops = dict(width = 1,headwidth = 4,facecolor='g',edgecolor = 'g', shrink=0)
            fig.annotate('', xy=(rspairhead[0],cDamp[int(rspairhead[0])]), xytext=rpairtail,arrowprops=arrowprops)
            fig.annotate('', xy=(rspairhead[1],cDamp[int(rspairhead[1])]), xytext=rpairtail,arrowprops=arrowprops)
            # hide axis
            frame = plt.gca()
            frame.axes.get_xaxis().set_visible(False)
            frame.axes.get_yaxis().set_visible(False)

            #plt.grid(True)
            plt.plot(cDamp)
            # reference point
            # plt.plot(tarpos,cDamp[tarpos-xL],'ro')
            plt.xlim(0,len(cDamp)-1)
            plt.title('DWT Level ({}):'.format(i-1))
        if auto_plot is True:
            plt.show()
        
    def loadsig(self,sig):
        pass
        



if __name__ == '__main__':
    mdlfilename = os.path.join(curfolderpath,'trained_model','A_5.mdl')
    rand_relation_path = os.path.join(curfolderpath,'trained_model','A_5_randrel.json')
    with open(mdlfilename,'r') as fin:
        rfmdl = pickle.load(fin)
    fvis = FeatureVis(rfmdl,rand_relation_path)
    #fvis.plot_fv_importance_test()
    # if savefigname == None:do not save
    savefigname = os.path.join(curfolderpath,'Feature_Importance.pdf')
    #savefigname = None
    fvis.plot_fv_importance_gswt(savefigname,False,50)
    

