#encoding:utf-8
"""
ECG Medical Evaluation Module
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import math
import pickle
import random
import time
import pdb

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
print 'projhomepath:',projhomepath
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import QTdata.loadQTdata as QTdb
from RFclassifier.evaluation import ECGstatistics
import RFclassifier.ECGRF as ECGRF 

class ResultFilter:
    def __init__(self,recres):
        self.recres = recres
        pass
    def groupresult(self,recres = None):
        # 根据不同label的边界来分组，应该根据位置来分组！
        #
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        # default parameter
        if recres is None:
            recres = self.recres
        group_min_thres = 1

        # filtered test result
        frecres = []
        # in var
        prev_label = None
        posGroup = []
        #----------------------
        # [pos,label] in recres
        #----------------------
        for pos,label in recres:
            if prev_label is not None:
                if label != prev_label:
                    frecres.append((prev_label,posGroup))
                    posGroup = []
                
            prev_label = label
            posGroup.append(pos)
        
        # last one
        if len(posGroup)>0:
            frecres.append((prev_label,posGroup))
        # [(label,[poslist])]
        frecres = [x for x in frecres if len(x[1]) > group_min_thres]
        frecres = [(int(np.mean(x[1])),x[0]) \
                for x in frecres]
                
        return frecres

    def group_local_result(self,recres = None,white_del_thres = 20,cp_del_thres = 1):
        #
        # 参数说明：1.white_del_thres是删除较小白色组的阈值
        #           2.cp_del_thres是删除较小其他关键点组的阈值
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        # default parameter
        if recres is None:
            recres = self.recres
        group_min_thres = 1

        # filtered test result
        frecres = []
        # in var
        prev_label = None
        posGroup = []
        #----------------------
        # [pos,label] in recres
        #----------------------
        for pos,label in recres:
            if prev_label is not None:
                if label != prev_label:
                    frecres.append((prev_label,posGroup))
                    posGroup = []
                
            prev_label = label
            posGroup.append(pos)
        # add last label group
        if len(posGroup)>0:
            frecres.append((prev_label,posGroup))
        #======================
        # 1.删除比较小的白色组和其他组(different threshold)
        # 2.合并删除后的相邻同色组
        #======================
        filtered_local_res = []
        for label,posGroup in frecres:
            if label == 'white' and len(posGroup) <= white_del_thres:
                continue
            if label != 'white' and len(posGroup) <= cp_del_thres:
                continue
            # can merge backward?
            if len(filtered_local_res)>0 and filtered_local_res[-1][0] == label:
                filtered_local_res[-1][1].extend(posGroup)
            else:
                filtered_local_res.append((label,posGroup))

        frecres = filtered_local_res
        # [(label,[poslist])]
        frecres = [x for x in frecres if len(x[1]) > group_min_thres]
        frecres = [(int(np.mean(x[1])),x[0]) \
                for x in frecres]
                
        return frecres
    def syntax_filter(self,reslist = None):
        # nest function
        def next_label(label):
            ## syntax next label
            ret = None
            if label == 'T':
                ret = 'Toffset'
            elif label == 'R':
                ret = 'Roffset'
            elif label == 'P':
                ret = 'Poffset'
            elif label == 'Tonset':
                ret = 'T'
            elif label == 'Toffset':
                ret = 'Ponset'
            elif label == 'Ronset':
                ret = 'R'
            elif label == 'Roffset':
                ret = 'Tonset'
            elif label == 'Ponset':
                ret = 'P'
            elif label == 'Poffset':
                ret = 'Ronset'
            else:# white
                ret = None
            return ret
        # parameter
        if reslist is None:
            reslist = self.recres
        if len(reslist) == 0:
            return []
        # const
        fs = 250
        Max_Len = 3*fs/25
        Offset_Len = fs/25
        # filtered result
        flt_res = []
        flt_res.append(reslist[0])

        # prev label and pos
        prev_label = reslist[0][1]
        prev_pos = reslist[0][0]
        prev_ind = 0

        # ----------------------
        # filtering
        # ----------------------
        N_reslist = len(reslist)
        while prev_ind < N_reslist:
            # find next non white point
            while prev_label == 'white' and prev_ind+1<N_reslist:
                prev_ind += 1
                prev_pos,prev_label = reslist[prev_ind]
                flt_res[-1] = reslist[prev_ind]
            if prev_ind+1 >= N_reslist:
                # no next
                break
            # matched next ind
            match_ind = -1
            cur_Max_Dist = Max_Len
            if 'offset' in prev_label:
                cur_Max_Dist = Offset_Len
            for nxt_ind in xrange(prev_ind,N_reslist):
                curpos,curlabel = reslist[nxt_ind]
                if curpos - prev_pos > cur_Max_Dist:
                    # not a label match
                    if match_ind == -1:
                        pass
                        #print 'prev_ind = {},nxt_ind = {}'.format(prev_label,nxt_ind)
                        #print 'reslist[{}:{}] = {}'.format(prev_ind,nxt_ind+1,reslist[prev_ind:nxt_ind+1])
                        #pdb.set_trace()
                    break
                if next_label(prev_label) == curlabel:
                    match_ind = nxt_ind
            if match_ind == -1:
                if nxt_ind >= N_reslist:
                    break
                else:
                    # False negtive
                    match_ind = nxt_ind
            prev_ind = match_ind
            flt_res.append(reslist[match_ind])
            prev_pos,prev_label = reslist[match_ind]

        return flt_res


