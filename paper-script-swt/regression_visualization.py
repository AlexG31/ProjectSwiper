#encoding:utf-8
"""
Feature Importance Visualization
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

# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath, 'ECGconf.json'), 'r') as fin:
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



class FeatureVisualizationSwt:
    def __init__(self, rfmdl, RandomPairList_Path):
        # get random relations
        randrel_path = RandomPairList_Path
        with open(randrel_path, 'r') as fin:
            self.randrels = json.load(fin)

        self.rfmdl = rfmdl
        self.trees = rfmdl.estimators_
        self.qt = QTloader()
        self.qt_reclist = self.qt.getQTrecnamelist()

        self.MaxHeartBeatWidth = 350
        self.QRS_segment_expand_length = 30
        self.FixedSignalLength = self.MaxHeartBeatWidth + 2 * self.QRS_segment_expand_length

    def info(self):
        t0 = self.trees[0]
        # list dir
        for attr in dir(t0):
            print attr
        print 'tree-------------------------'
        for attr in dir(t0.tree_):
            print attr

        pdb.set_trace()
    def GetImportancePairs(self):
        '''
        Zipping pairs from random pairs file & importance values from classification model.
        Get a struct of importance:
            [#layer0:[((23, 2), 0.2# importance),
                ((pair), #importance), ()...],
             #layer1:[], ..]
        
        return:
             pairs & their importance
        '''
        # random relations 
        randrels = self.randrels
        importance_list = self.rfmdl.feature_importances_
        sum_rr = 0
        for rr in randrels:
            sum_rr += len(rr)
        print 'len(feature importance) = {}, len(random relations) = {}'.format(
                len(importance_list), sum_rr)

        print 'len(importance_list) = ', len(importance_list)
        print 'sum_rr * 2 = ', sum_rr * 2
        if len(importance_list) != 2*sum_rr:
            raise Exception('Length of important features is not equal '
                    'to the total number of pairs!')

        layer_index_start, layer_index_end = 0, 0
        relation_importance = []
        for rel_layer in randrels:
            layer_size = len(rel_layer)
            layer_index_end = layer_index_start + 2 * layer_size

            pair_diff_importance_list = importance_list[layer_index_start:layer_index_end:2]
            abs_diff_importance_list = importance_list[layer_index_start+1:layer_index_end:2]
            # Choose the maximum value from the importance of pair difference
            # and absolute pair difference.
            imp_arr = map(lambda x:max(x[0], x[1]),
                    zip(pair_diff_importance_list,
                abs_diff_importance_list))
            relation_importance.append(zip(rel_layer, imp_arr))
            layer_index_start += 2 * layer_size

        return relation_importance

    def get_min_Importance_threshold(self,relation_importance,top_importance_ratio = 9.5/10):
        '''Select top p% importance value.'''
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

    def plot_dwt_pairs_arrow_transparent(self,
            rawsig,
            relation_importance,
            Window_Left = 1200,
            savefigname = None,
            figureID = 1,
            figsize = (8,6),
            figtitle = 'ECG Sample',
            showFigure = True,
            wavelet = 'db6',
            swt_level = 6):
        ## =========================================
        # 展示RSWT示意图
        # Plot Arrow
        #   with alpha value: png, pdf file
        ## =========================================
        #================
        # constants
        #================
        relation_importance = self.rfmdl.feature_importances_
        N_subplot = 7
        # Importance pairs lower than this threshold is not shown in the figure.
        # Thres_min_importance = self.get_min_Importance_threshold(relation_importance,
                # top_importance_ratio = 0.95)
        Thres_min_importance = 0.5

        fs = conf['fs']
        fixed_feature_layer_length = self.FixedSignalLength
        FixedWindowLen = fixed_feature_layer_length
        print 'Fixed Window Length:{}'.format(FixedWindowLen)

        xL = Window_Left
        xR = xL+FixedWindowLen
        tarpos  = (xL + xR) / 2
        # -----------------
        # Get median
        # -----------------
        importance_arr = self.rfmdl.feature_importances_

        IMP_MAX = np.max(importance_arr)

        # Get SWT detail coefficient lists
        rawsig = self.crop_data_for_swt(rawsig)
        coeflist = pywt.swt(rawsig, wavelet, swt_level)
        cAlist, cDlist = zip(*coeflist)
        self.cAlist = cAlist[::-1]
        self.cDlist = cDlist[::-1]

        pltxLim = range(xL,xR)
        sigAmp = [rawsig[x] for x in pltxLim]

        detail_index = 1
        # ====================
        # Plot raw signal input
        # ====================
        Fig_main = plt.figure(figureID, figsize = figsize)
        # plot raw ECG
        plt.subplot(N_subplot / 2,2,1)

        plt.plot(pltxLim,sigAmp)
        # plot reference point
        plt.plot(tarpos,rawsig[tarpos],'ro')
        plt.title(figtitle)
        plt.xlim(pltxLim[0],pltxLim[-1])


        importance_index = 0

        for i in range(2, N_subplot):
            # Relation&importance
            rel_layer = relation_importance[importance_index:importance_index + fixed_feature_layer_length]
            importance_index += 2 * fixed_feature_layer_length

            cD = self.cDlist[detail_index]
            detail_index += 1

            # Crop x range out
            xi = range(xL,xR)
            cDamp = [cD[x] for x in xi]
            # get relation points
            rel_x = []
            rel_y = []
            cur_N = len(cDamp)
            # ------------
            # sub plot 
            # ------------
            fig = plt.subplot(N_subplot / 2, 2, i)
            plt.title('DWT Detail Coefficient {}'.format(detail_index))
            # ------------
            # find pair&its amplitude
            # -----------
            plt.plot(cDamp, lw = 2)
            rel_layer = np.array(rel_layer)
            mean_rel_layer = np.mean(rel_layer)
            max_amp = np.max(cDamp)

            rel_layer = mean_rel_layer - (mean_rel_layer - rel_layer) * 1e3
            rel_layer -= np.min(rel_layer)
            rel_layer[rel_layer > max_amp] = max_amp

            stem_marker, stem_line, stem_base = plt.stem(rel_layer)
            plt.setp(stem_line, 'color', (1, 208/255.0, 114/255.0, 0.3), lw = 4)
            plt.setp(stem_marker, markersize = 2)

        
        # plot result
        if showFigure == True:
            plt.show()
        # save fig
        if savefigname is not None:
            Fig_main.savefig(savefigname, dpi = Fig_main.dpi)
            Fig_main.clf()

    def PlotApproximationLevel(self, importance_list):
        '''Plot Approximation level importance.'''
        # plot Approximation Level
        rel_x = []
        rel_y = []

        rel_layer = importance_list
        fig = plt.subplot(4,2,8)
        plt.title('Approximation Coefficient')
        cAamp = [self.cAlist[-1][x] for x in xi]

        # sort rel_layer with imp
        rel_layer.sort(key = lambda x:x[1])
        for rel_pair, imp in rel_layer:
            # Hide importance lower than threshold
            if imp<Thres_min_importance:
                continue
            # importance thres
            alpha = (imp-Thres_min_importance) / (IMP_MAX-Thres_min_importance)
            #arrow_color = self.get_RGB_from_Alpha((1,0,0),alpha,(1,1,1))
            arrow_color = (1,0,0)
            #arrowprops = dict(width = 1, headwidth = 4, facecolor=arrow_color, edgecolor = arrow_color, shrink=0)
            arrowprops = dict(alpha = alpha,
                    width = 0.15,
                    linewidth = 0.15,
                    headwidth = 1.5,
                    headlength = 1.5,
                    facecolor=arrow_color,
                    edgecolor = arrow_color,
                    shrink=0)

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
            fig.annotate('', xy=(rel_x[-2],rel_y[-2]),
                    xytext=(rel_x[-1],rel_y[-1]),arrowprops=arrowprops)

        # reference point
        plt.plot(rel_x,rel_y,'.b')
        plt.plot(cAamp)
        plt.xlim(0,len(cAamp)-1)

    def crop_data_for_swt(self,rawsig):
        '''Padding zeros to make the length of the signal to 2^N.'''
        # crop rawsig
        base2 = 1
        N_data = len(rawsig)
        if len(rawsig)<=1:
            raise Exception('len(rawsig)={},not enough for swt!',len(rawsig))
        crop_len = base2
        while base2<N_data:
            if base2*2>=N_data:
                crop_len = base2*2
                break
            base2*=2
        # Extending this signal input with its tail element.
        if N_data< crop_len:
            rawsig += [rawsig[-1],]*(crop_len-N_data)
        return rawsig

    def get_RGB_from_Alpha(self,color,alpha,bgcolor):
        new_color = []
        for color_elem,bg_color_elem in zip(color,bgcolor):
            color_elem = float(color_elem)
            bg_color_elem = float(bg_color_elem)
            ncolor = (1.0-alpha)*bg_color_elem+alpha*color_elem
            new_color.append(ncolor)
        return new_color
    def plot_fv_importance(self):
        # cycling plot importance of list of positions
        rID = 2
        sig = self.qt.load(self.qt_reclist[rID])
        rel_imp = self.GetImportancePairs()
        # save current fig
        for i in xrange(0,130,10):
            savefigname = os.path.join(curfolderpath,'range_{}.png'.format(i))
            self.plot_dwt_pairs_arrow(sig['sig'],rel_imp,Window_Left = 1180+i,savefigname = savefigname,figsize = (16,12),figtitle = 'Window Start[{}]'.format(i))

    def plot_fv_importance_gswt(self,
            savefigname,
            showFigure,
            WindowLeftBias = 10):
        # QT record ID
        rID = 2
        # sig = self.qt.load(self.qt_reclist[rID])
        sig = self.qt.load('sel103')

        rel_imp = []
        # rel_imp = self.GetImportancePairs()
        # Save current fig
        figtitle = 'ECG from QTdb Record {}'.format(self.qt_reclist[rID])
        self.plot_dwt_pairs_arrow_transparent(
                sig['sig'],
                rel_imp,
                Window_Left = 54100+WindowLeftBias,
                savefigname = savefigname,
                figsize = (14,14),
                figtitle = figtitle,
                showFigure = showFigure)


def VisualizeModel(target_label = 'T', WindowLeftBias = 140, show_figure = False):
    '''Visualize model.'''
    # target_label = 'P'
    mdlfilename = os.path.join(curfolderpath,
            'regression_models',
            target_label,
            'trained_model.mdl')
    rand_relation_path = os.path.join(curfolderpath,
            'regression_models',
            'rand_relations.json')

    with open(mdlfilename, 'rb') as fin:
        rfmdl = pickle.load(fin)
    fvis = FeatureVisualizationSwt(rfmdl, rand_relation_path)

    savefigname = os.path.join(curfolderpath, 'regression_{}.png'.format(target_label))
    fvis.plot_fv_importance_gswt(
            savefigname, showFigure = show_figure, WindowLeftBias = WindowLeftBias)



if __name__ == '__main__':
    show_figure = True
    VisualizeModel('P', 140, show_figure = show_figure)
    # VisualizeModel('T', 50, show_figure = show_figure)
    # VisualizeModel('R', 50, show_figure = show_figure)
