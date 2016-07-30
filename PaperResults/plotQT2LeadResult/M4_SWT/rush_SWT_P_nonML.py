#encoding:utf-8
"""
ECG Medical Evaluation Module
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import bisect
import math
import pickle
import random
import time
import pdb
import pywt

import numpy as np
## machine learning methods
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
projhomepath = os.path.dirname(projhomepath)
print 'projhomepath:',projhomepath
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components

sys.path.append(os.path.dirname(curfolderpath))
from QTdata.loadQTdata import QTloader 
# import and define alias
import SWT_NoPredictQRS as NoQrsSwt
SWT_NoPredictQRS = NoQrsSwt.SWT_NoPredictQRS
Convert2ExpertFormat = NoQrsSwt.Convert2ExpertFormat

class SWT_GroupResult2Leads:
    ''' Find P&T peak with SWT+db6
    '''
    def __init__(self,recname,reslist,leadname,QRS_GroupResultFolder,MaxSWTLevel = 9):
        # leadname must be sig: lead number 0
        # or sig2:lead number 1
        if leadname not in ['sig','sig2']:
            raise Exception('self.getSWTcoeflist will rely on leadname to get the number of lead from the Group Result!')
        # color for plot
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        self.colors = []
        for color_tri in tableau20:
            self.colors.append((color_tri[0]/255.0,color_tri[1]/255.0,color_tri[2]/255.0))

        self.recres = reslist
        #self.LeadRes = (reslist,reslist2)

        self.recname = recname
        self.leadname = leadname
        self.QTdb = QTloader()
        self.sig_struct = self.QTdb.load(self.recname)
        self.rawsig = self.sig_struct[leadname]

        # For the SWT to remove QRS regions.
        self.QRS_GroupResultFolder = QRS_GroupResultFolder
        self.res_groups = None
        self.peak_dict = dict(T=[],P=[],Ponset = [],Poffset = [],Tonset = [],Toffset = [])

        # SWT without QRS region
        self.getSWTcoeflist()
    def getSWTcoeflist(self,MaxLevel = 9):
        # Get SWT coef
        recname = self.recname
        GroupResultFolder = self.QRS_GroupResultFolder
        rawsig = self.rawsig
        with open(os.path.join(GroupResultFolder,'{}.json'.format(recname)),'r') as fin:
            RawResultDict = json.load(fin)
            LeadResult = RawResultDict['LeadResult']
            if self.leadname == 'sig':
                MarkDict = LeadResult[0]
            elif self.leadname == 'sig2':
                MarkDict = LeadResult[1]
            MarkList = Convert2ExpertFormat(MarkDict)

        # Display with 2 subplots.
        swt = SWT_NoPredictQRS(rawsig,MarkList)
        swt.swt()
        self.cDlist = swt.cDlist
        self.cAlist = swt.cAlist

    def group_result(self,white_del_thres = 20,cp_del_thres = 0):
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

        recres = self.recres

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
        self.res_groups = frecres
                
        return frecres
    def filter_smaller_nearby_groups(self,res_groups,group_near_dist_thres = 100):
        # [(label,[poslist])]
        # filter close groups:
        # delete groups with smaller number
        frecres = res_groups
        N_groups = len(frecres)
        deleted_reslist = []
        
        deleted_reslist.append(frecres[0])
        for group_ind in xrange(1,N_groups):
            max_before = np.max(deleted_reslist[-1][1])
            min_after = np.min(frecres[group_ind][1])
            if min_after-max_before <=group_near_dist_thres:
                # keep the larger group
                if len(frecres[group_ind][1]) > len(deleted_reslist[-1][1]):
                    # del delete
                    del deleted_reslist[-1]
                    deleted_reslist.append(frecres[group_ind])
            else:
                deleted_reslist.append(frecres[group_ind])
        return deleted_reslist


    def crop_data_for_swt(self,rawsig):
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
        # pad zeros
        if N_data< crop_len:
            rawsig += [rawsig[-1],]*(crop_len-N_data)
        rawsig = rawsig[0:crop_len]
        return rawsig

        
    def get_downward_cross_zero_list(self,array):
        # rising slope only
        if array is None or len(array)<2:
            return []
        crosszerolist = []
        #
        # len of array
        N_array = len(array)
        for ind in xrange(1,N_array-1):
            # cross zero
            if array[ind-1]>0 and array[ind]<=0:
                crosszerolist.append(ind)
        return crosszerolist

    def get_cross_zero_list(self,array):
        # rising slope only
        if array is None or len(array)<2:
            return []
        crosszerolist = []
        rem = array[0]
        N_array = len(array)

        for ind in xrange(1,N_array):
            if array[ind-1]<0 and array[ind]>=0:
                crosszerolist.append(ind)
        return crosszerolist
    def get_local_minima_list(self,array):
        # rising slope only
        if array is None or len(array)<2:
            return []
        ret_list = []
        # 
        # length of array
        N = len(array)
        for ind in xrange(1,N-1):
            if array[ind]-array[ind-1]<0 and array[ind+1]-array[ind]>=0:
                # local maxima
                ret_list.append(ind)
        return ret_list

    def get_local_maxima_list(self,array):
        # rising slope only
        if array is None or len(array)<2:
            return []
        ret_list = []
        N = len(array)
        for ind in xrange(1,N-1):
            if array[ind]-array[ind-1]>0 and array[ind+1]-array[ind]<=0:
                # local maxima
                ret_list.append(ind)
        return ret_list


    def bw_find_nearest(self,pos,array):
        N = len(array)
        insertPos = bisect.bisect_left(array,pos)
        if insertPos>=N:
            return abs(pos-array[-1])
        elif insertPos ==0:
            return abs(pos-array[0])
        else:
            return min(abs(pos-array[insertPos]),abs(pos-array[insertPos-1]))
    def get_longest_downward_slope_index(self,candidate_list,crosszerolist,e4list):
        #
        # length of cross zeros
        N = len(crosszerolist)
        max_slope_len = -1
        best_candidate = -1
        for prd_pos in candidate_list:

            # find the closest cross point in the list to prd_pos
            insertPos = bisect.bisect_left(crosszerolist,prd_pos)
            peak_pos = -1
            if insertPos>=N:
                peak_pos = N-1
            elif insertPos == 0:
                peak_pos = 0
            else:
                if abs(prd_pos-crosszerolist[insertPos])<abs(prd_pos-crosszerolist[insertPos-1]):
                    peak_pos = insertPos
                else:
                    peak_pos = insertPos-1

            peak_pos = crosszerolist[peak_pos]
            # Find current slope length
            right_bound = N-1
            left_bound = 0

            # reached N-1 or local maxima
            for cur_pos in xrange(peak_pos,N-1):
                if e4list[cur_pos+1]-e4list[cur_pos]>=0:
                    # local minima
                    right_bound = cur_pos
                    break
            
            # reached 0
            for cur_pos in xrange(peak_pos,0,-1):
                if e4list[cur_pos]-e4list[cur_pos-1]>=0:
                    # local maxima
                    left_bound = cur_pos
                    break
            cur_slope_len = right_bound-left_bound
            if cur_slope_len>max_slope_len:
                max_slope_len = cur_slope_len
                best_candidate = peak_pos
        return best_candidate

    def get_current_upward_slope_steepness(self,pos,crosszerolist,e4list):
        # Frequent used var.
        N = len(crosszerolist)
        N_e4list = len(e4list)

        # Only one pos, find its left minima&right maxima.
        prd_pos = pos
        # find the closest cross point in the list to prd_pos
        insertPos = bisect.bisect_left(crosszerolist,prd_pos)

        peak_pos = -1
        if insertPos>=N:
            peak_pos = N-1
        elif insertPos == 0:
            peak_pos = 0
        else:
            if abs(prd_pos-crosszerolist[insertPos])<abs(prd_pos-crosszerolist[insertPos-1]):
                peak_pos = insertPos
            else:
                peak_pos = insertPos-1

        peak_pos = crosszerolist[peak_pos]
        # Find current slope length
        right_bound = N-1
        left_bound = 0

        # reached N-1 or local maxima
        for cur_pos in xrange(peak_pos,N_e4list-1):
            if e4list[cur_pos+1]-e4list[cur_pos]<=0:
                # local maxima
                right_bound = cur_pos
                break
        
        # reached 0
        for cur_pos in xrange(peak_pos,0,-1):
            if e4list[cur_pos]-e4list[cur_pos-1]<=0:
                # local minima
                left_bound = cur_pos
                break
        cur_slope_len = right_bound-left_bound
        if cur_slope_len <= 0:
            plt.figure(2)
            plt.plot(e4list)
            plt.plot(crosszerolist,map(lambda x:e4list[x],crosszerolist),'ro')
            plt.plot(peak_pos,e4list[peak_pos],'y*',markersize = 14)
            plt.grid(True)
            plt.show()
            print 
            print 'Warning: cur_slope_len <= 0!'
            pdb.set_trace()
        cur_slope_amp = abs(e4list[right_bound]-e4list[left_bound])
        return float(cur_slope_amp)/cur_slope_len

    def get_steepest_slope_index(self,candidate_list,crosszerolist,e4list):
        N = len(crosszerolist)
        max_slope_steepness = None
        best_candidate = None
        for prd_pos in candidate_list:

            # find the closest cross point in the list to prd_pos
            insertPos = bisect.bisect_left(crosszerolist,prd_pos)
            peak_pos = -1
            if insertPos>=N:
                peak_pos = N-1
            elif insertPos == 0:
                peak_pos = 0
            else:
                if abs(prd_pos-crosszerolist[insertPos])<abs(prd_pos-crosszerolist[insertPos-1]):
                    peak_pos = insertPos
                else:
                    peak_pos = insertPos-1

            peak_pos = crosszerolist[peak_pos]
            # Find current slope length
            right_bound = N-1
            left_bound = 0
            right_amp,left_amp = None,None

            # reached N-1 or local maxima
            N_e4list = len(e4list)
            for cur_pos in xrange(peak_pos,N_e4list-1):
                if e4list[cur_pos+1]-e4list[cur_pos]<=0:
                    # local maxima
                    right_bound = cur_pos
                    right_amp = e4list[cur_pos]
                    break
            
            # reached 0
            for cur_pos in xrange(peak_pos,0,-1):
                if e4list[cur_pos]-e4list[cur_pos-1]<=0:
                    # local minima
                    left_bound = cur_pos
                    left_amp = e4list[cur_pos]
                    break
            cur_slope_len = right_bound-left_bound
            cur_steepness = float(abs(right_amp-left_amp))/cur_slope_len

            # choose the steepest one as the finnal position 
            if max_slope_steepness is None or cur_steepness > max_slope_steepness:
                max_slope_steepness = cur_steepness
                best_candidate = prd_pos
        return best_candidate

    def get_steepest_downward_slope_index(self,candidate_list,crosszerolist,e4list):
        #
        # length of cross zeros
        N = len(crosszerolist)
        max_slope_len = -1
        best_candidate = -1
        max_slope_steepness = None

        for prd_pos in candidate_list:

            # find the closest cross point in the list to prd_pos
            insertPos = bisect.bisect_left(crosszerolist,prd_pos)
            peak_pos = -1
            if insertPos>=N:
                peak_pos = N-1
            elif insertPos == 0:
                peak_pos = 0
            else:
                if abs(prd_pos-crosszerolist[insertPos])<abs(prd_pos-crosszerolist[insertPos-1]):
                    peak_pos = insertPos
                else:
                    peak_pos = insertPos-1

            peak_pos = crosszerolist[peak_pos]
            # Find current slope length
            right_bound = N-1
            left_bound = 0
            right_amp,left_amp = None,None

            # reached N-1 or local maxima
            for cur_pos in xrange(peak_pos,len(e4list)):
                if e4list[cur_pos+1]-e4list[cur_pos]>=0:
                    # local minima
                    right_bound = cur_pos
                    right_amp = e4list[cur_pos]
                    break
            
            # reached 0
            for cur_pos in xrange(peak_pos,0,-1):
                if e4list[cur_pos]-e4list[cur_pos-1]>=0:
                    # local maxima
                    left_bound = cur_pos
                    left_amp = e4list[cur_pos]
                    break
            cur_slope_len = right_bound-left_bound

            if left_amp is None or right_amp is None:
                print 'left_amp,right_amp:'
                print left_amp,right_amp
                pdb.set_trace()
            cur_steepness = float(abs(right_amp-left_amp))/cur_slope_len

            # choose the steepest one as the finnal position 
            if max_slope_steepness is None or cur_steepness > max_slope_steepness:
                max_slope_steepness = cur_steepness
                best_candidate = prd_pos
        return best_candidate

    def get_longest_slope_index(self,candidate_list,crosszerolist,e4list):
        N = len(crosszerolist)
        N_e4list = len(e4list)
        max_slope_len = None
        best_candidate = None
        for prd_pos in candidate_list:

            # find the closest cross point in the list to prd_pos
            insertPos = bisect.bisect_left(crosszerolist,prd_pos)
            peak_pos = -1
            if insertPos>=N:
                peak_pos = N-1
            elif insertPos == 0:
                peak_pos = 0
            else:
                if abs(prd_pos-crosszerolist[insertPos])<abs(prd_pos-crosszerolist[insertPos-1]):
                    peak_pos = insertPos
                else:
                    peak_pos = insertPos-1

            peak_pos = crosszerolist[peak_pos]
            # Find current slope length
            right_bound = N-1
            left_bound = 0

            # reached N-1 or local maxima
            for cur_pos in xrange(peak_pos,N_e4list-1):
                if e4list[cur_pos+1]-e4list[cur_pos]<=0:
                    # local maxima
                    right_bound = cur_pos
                    break
            
            # reached 0
            for cur_pos in xrange(peak_pos,0,-1):
                if e4list[cur_pos]-e4list[cur_pos-1]<=0:
                    # local minima
                    left_bound = cur_pos
                    break
            cur_slope_len = right_bound-left_bound
            if max_slope_len is None or cur_slope_len>max_slope_len:
                max_slope_len = cur_slope_len
                best_candidate = prd_pos
        return best_candidate

                
    def get_T_peaklist(self):
        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]=='T',self.res_groups)
        res_groups = self.filter_smaller_nearby_groups(res_groups)

        # get T peak
        #e4list = np.array(self.cDlist[-4])+np.array(self.cDlist[-5])
        D6list = np.array(self.cDlist[-6])
        D5list = np.array(self.cDlist[-5])
        crosszerolist = self.get_cross_zero_list(D6list)
        D5crosszerolist = self.get_cross_zero_list(D5list)

        # debug :D5crosszerolist check!
        # e4list = D5list
        # plt.figure(2)
        # plt.plot(e4list)
        # plt.plot(D5crosszerolist,map(lambda x:e4list[x],D5crosszerolist),'ro')
        # plt.plot(155424,D5list[155424],'y*',markersize = 14)
        # plt.grid(True)
        # plt.show()
        # if 155424 in D5crosszerolist:
            # print '155424'
        # pdb.set_trace()

        # for debug
        sig_struct = self.QTdb.load(self.recname)
        raw_sig = sig_struct['sig']
        
        debug_res_group_ind = 21
        for label,posgroup in res_groups[22:]:
            debug_res_group_ind += 1
            scorelist = []
            D5scorelist = []
            for pos in posgroup:
                nearest_dist = self.bw_find_nearest(pos,crosszerolist)
                scorelist.append((nearest_dist,pos))
                # for D5
                D5nearest_dist = self.bw_find_nearest(pos,D5crosszerolist)
                D5scorelist.append((D5nearest_dist,pos))

            # get all pos with min score
            min_score,candidate_list  = self.get_min_score_poslist(scorelist)
            D5min_score,D5candidate_list  = self.get_min_score_poslist(D5scorelist)

            D5pos,D6pos = [],[]
            D5_swt_mark,D6_swt_mark = True,True
            final_decision_peak = -1
            # get D6 crosszero position
            if min_score >2:
                # not a peak
                print 
                print 'Warning: using mean group position!'
                D6_swt_mark = False
                D6pos.append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                D6pos.append(candidate_list[0])
            else:
                # multiple min score
                longest_slope_index = self.get_longest_slope_index(candidate_list,crosszerolist,D6list)
                D6pos.append(crosszerolist[longest_slope_index])
            # get D5 crosszero position
            if D5min_score >2:
                # not a peak
                print 
                print 'Warning: using mean group position!'
                D5_swt_mark = False
                D5pos.append(np.mean(posgroup))
            elif len(D5candidate_list) ==1:
                # only mean score by SWT
                D5pos.append(D5candidate_list[0])
            else:
                # multiple min score
                longest_slope_index = self.get_longest_slope_index(D5candidate_list,D5crosszerolist,D5list)
                D5pos.append(D5crosszerolist[longest_slope_index])
            # plot two positions for debug --- check!

            print 'debug_res_group_ind',debug_res_group_ind
            # Get the slope for D5list and D6list.
            if D5_swt_mark and D6_swt_mark:
                print 'getting D5 slope:'
                D5slope = self.get_current_upward_slope_steepness(D5pos[-1],D5crosszerolist,D5list)
                print 'getting D6 slope:'
                D6slope = self.get_current_upward_slope_steepness(D6pos[-1],crosszerolist,D6list)
                print 'D6 slope value:'
                print D6slope
                print 'D5 slope value:'
                print D5slope

                pdb.set_trace()
                if D5slope < D6slope:
                    final_decision_peak = D6pos[-1]
                else:
                    final_decision_peak = D5pos[-1]

            elif D5_swt_mark:
                final_decision_peak = D5pos[-1]
            elif D6_swt_mark:
                final_decision_peak = D6pos[-1]
            else:
                # Default value is D6pos
                final_decision_peak = D6pos[-1]

            # debug plot
            # 1. get range
            seg_range = [min(posgroup),max(posgroup)]
            seg_range[0] = max(0,seg_range[0] - 100)
            seg_range[1] = min(len(raw_sig)-1,seg_range[1] + 100)
            # 2.plot
            seg = raw_sig[seg_range[0]:seg_range[1]]
            plt.ion()
            plt.figure(1)
            plt.clf()
            plt.plot(seg,label = 'ECG')
            # 3.plot group
            seg_posgroup = map(lambda x:x-seg_range[0],posgroup)
            plt.plot(seg_posgroup,map(lambda x: seg[x],seg_posgroup),label = 'posgroup',marker = 'o',markersize = 4,markerfacecolor = 'g',alpha = 0.7)
            # 4.plot peak pos
            # plot D6 postion
            peak_pos = D6pos[-1]-seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'yo',markersize = 12,alpha = 0.7,label = 'D6 pos')
            # plot D5 postion
            peak_pos = D5pos[-1]-seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'mo',markersize = 12,alpha = 0.7,label = 'D5 pos')
            # plot final decision postion
            peak_pos = final_decision_peak - seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'r*',markersize = 12,alpha = 0.7,label = 'D5 pos')
            # 5.plot determin line
            seg_determin_line = self.cDlist[-6][seg_range[0]:seg_range[1]]
            seg_determin_line5 = self.cDlist[-5][seg_range[0]:seg_range[1]]
            plt.plot(seg_determin_line,'y',label = 'D6')
            plt.plot(seg_determin_line5,'m',label = 'D5')

            plt.title(self.recname)
            plt.legend()
            plt.grid(True)
            plt.show()
            # debug stop
            if D5_swt_mark and D6_swt_mark:
                print 'D5pos:',D5pos
                print 'D6pos:',D6pos
                print 'final_decision_peak',final_decision_peak
            pdb.set_trace()

        # return list of T peaks
        return self.peak_dict['T']

    def get_min_score_poslist(self,scorelist):
        # get min score poslist from 
        # [(score,pos),...]

        if scorelist is None or len(scorelist) ==0:
            return None
        minScore = scorelist[0][0]
        poslist = []
        
        # find minScore
        for score,pos in scorelist:
            if score<minScore:
                minScore = score

        # find all pos with minScore
        for score,pos in scorelist:
            if score ==minScore:
                poslist.append(pos)
        return (minScore,poslist)
    def get_P_peaklist_debug(self,debug = False,extra_search_len = 10):
        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]=='P',self.res_groups)
        res_groups = self.filter_smaller_nearby_groups(res_groups)

        # debug plot expert position
        expert_label_list = self.QTdb.getexpertlabeltuple(self.recname)
        D4list = np.array(self.cDlist[-4])
        D5list = np.array(self.cDlist[-5])
        crosszerolist = self.get_cross_zero_list(D4list)
        D5crosszerolist = self.get_cross_zero_list(D5list)

        # debug :D5crosszerolist check!
        # e4list = D5list
        # plt.figure(2)
        # plt.plot(e4list)
        # plt.plot(D5crosszerolist,map(lambda x:e4list[x],D5crosszerolist),'ro')
        # plt.plot(155424,D5list[155424],'y*',markersize = 14)
        # plt.grid(True)
        # plt.show()
        # if 155424 in D5crosszerolist:
            # print '155424'
        # pdb.set_trace()

        # for debug
        sig_struct = self.QTdb.load(self.recname)
        raw_sig = sig_struct['sig']
        
        debug_res_group_ind = 0
        for label,posgroup in res_groups:
            debug_res_group_ind += 1
            scorelist = []
            D5scorelist = []
            for pos in posgroup:
                nearest_dist = self.bw_find_nearest(pos,crosszerolist)
                scorelist.append((nearest_dist,pos))
                # for D5
                D5nearest_dist = self.bw_find_nearest(pos,D5crosszerolist)
                D5scorelist.append((D5nearest_dist,pos))

            # get all pos with min score
            min_score,candidate_list  = self.get_min_score_poslist(scorelist)
            D5min_score,D5candidate_list  = self.get_min_score_poslist(D5scorelist)

            D5pos,D4pos = [],[]
            D5_swt_mark,D4_swt_mark = True,True
            final_decision_peak = -1
            # get D4 crosszero position
            if min_score >2:
                # not a peak
                print 
                print 'Warning: using mean group position!'
                D4_swt_mark = False
                D4pos.append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                D4pos.append(candidate_list[0])
            else:
                # multiple min score
                best_candidate = self.get_longest_slope_index(candidate_list,crosszerolist,D4list)
                D4pos.append(best_candidate)
            # get D5 crosszero position
            if D5min_score >2:
                # not a peak
                print 
                print 'Warning: using mean group position!'
                D5_swt_mark = False
                D5pos.append(np.mean(posgroup))
            elif len(D5candidate_list) ==1:
                # only mean score by SWT
                D5pos.append(D5candidate_list[0])
            else:
                # multiple min score
                best_candidate = self.get_longest_slope_index(D5candidate_list,D5crosszerolist,D5list)
                D5pos.append(best_candidate)
            # plot two positions for debug --- check!

            print 'debug_res_group_ind',debug_res_group_ind
            # Get the slope for D5list and D4list.
            if D5_swt_mark and D4_swt_mark:
                print 'getting D5 slope:'
                D5slope = self.get_current_upward_slope_steepness(D5pos[-1],D5crosszerolist,D5list)
                print 'getting D4 slope:'
                D4slope = self.get_current_upward_slope_steepness(D4pos[-1],crosszerolist,D4list)
                print 'D4 slope value:'
                print D4slope
                print 'D5 slope value:'
                print D5slope

                # pdb.set_trace()
                if D5slope < D4slope:
                    final_decision_peak = D4pos[-1]
                else:
                    final_decision_peak = D5pos[-1]

            elif D5_swt_mark:
                final_decision_peak = D5pos[-1]
            elif D4_swt_mark:
                final_decision_peak = D4pos[-1]
            else:
                # Default value is D4pos
                final_decision_peak = D4pos[-1]

            # debug plot
            # 1. get range
            seg_range = [min(posgroup),max(posgroup)]
            seg_range[0] = max(0,seg_range[0] - 100)
            seg_range[1] = min(len(raw_sig)-1,seg_range[1] + 100)
            # 2.plot
            seg = raw_sig[seg_range[0]:seg_range[1]]
            plt.ion()
            plt.figure(1)
            plt.clf()
            plt.plot(seg,label = 'ECG')
            # 3.plot group
            seg_posgroup = map(lambda x:x-seg_range[0],posgroup)
            plt.plot(seg_posgroup,map(lambda x: seg[x],seg_posgroup),label = 'posgroup',marker = 'o',markersize = 4,markerfacecolor = 'g',alpha = 0.7)
            # 4.plot peak pos
            # plot D4 postion
            peak_pos = D4pos[-1]-seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'yo',markersize = 12,alpha = 0.7,label = 'D4 pos')
            # plot D5 postion
            peak_pos = D5pos[-1]-seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'mo',markersize = 12,alpha = 0.7,label = 'D5 pos')
            # plot Expert label position
            segment_expertlist = filter(lambda x: x[0]>=seg_range[0] and x[0]<seg_range[1],expert_label_list)
            if len(segment_expertlist) > 0:
                segment_expert_poslist,segment_expert_labellist = zip(*segment_expertlist)
                plt.plot(map(lambda x:x-seg_range[0],segment_expert_poslist),map(lambda x:seg[x-seg_range[0]],segment_expert_poslist),'rd',markersize = 12,alpha = 0.7,label = 'expert label')
            # plot final decision postion
            peak_pos = final_decision_peak - seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'*',color = self.colors[1],markersize = 12,alpha = 0.7,label = 'final position')
            # 5.plot determin line
            seg_determin_line = self.cDlist[-4][seg_range[0]:seg_range[1]]
            seg_determin_line5 = self.cDlist[-5][seg_range[0]:seg_range[1]]
            plt.plot(seg_determin_line,'y',label = 'D4')
            plt.plot(seg_determin_line5,'m',label = 'D5')

            plt.title(self.recname)
            plt.legend()
            plt.grid(True)
            plt.show()
            # debug stop
            if D5_swt_mark and D4_swt_mark:
                print 'D5pos:',D5pos
                print 'D4pos:',D4pos
                print 'final_decision_peak',final_decision_peak
            pdb.set_trace()

        # return list of T peaks
        return self.peak_dict['T']
    def get_P_peaklist(self,debug = False,extra_search_len = 10):
        return self.get_P_peaklist_debug(debug = debug,extra_search_len = extra_search_len)

        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]=='P',self.res_groups)
        res_groups = self.filter_smaller_nearby_groups(res_groups)
        # get P peak list
        #D5list = np.array(self.cDlist[-6])+np.array(self.cDlist[-5])
        D5list = np.array(self.cDlist[-5])

        # Get raw_sig
        sig_struct = self.QTdb.load(self.recname)
        raw_sig = sig_struct['sig']
        N_rawsig = len(raw_sig)

        #local_maxima_list = self.get_local_maxima_list(D5list)
        local_maxima_list = self.get_cross_zero_list(D5list)
        
        # Expert Label list
        expert_label_list = self.QTdb.getexpertlabeltuple(self.recname)
        print 'record name:',self.recname
        print 'length of expert label:',len(expert_label_list)
        # debug
        #if debug == True:
            #plt.figure(2)
            #plt.plot(D5list)
            #plt.plot(local_maxima_list,map(lambda x:D5list[x],local_maxima_list),'y*',markersize = 14)
            #plt.show()

        # find local maxima point within each group
        debug_ind = 0
        print 'len(res_groups):',len(res_groups)
        # pdb.set_trace()
        for label,posgroup in res_groups[7:]:
            print 'debug_ind:',debug_ind
            debug_ind += 1
            scorelist = []

            if len(posgroup) <= 2:
                print 'Warning: Filtering out small posgroup.'
                continue
            print 'Pos Group:',posgroup
            print 'mean Group:',np.mean(posgroup)

            
            extra_search_left = max(0,min(posgroup)-extra_search_len)
            extra_search_right = min(N_rawsig,max(posgroup)+extra_search_len)

            for pos in xrange(extra_search_left,extra_search_right):
                nearest_dist = self.bw_find_nearest(pos,local_maxima_list)
                scorelist.append((nearest_dist,pos))
            scorelist.sort(key = lambda x:x[0])

            # get all pos with min score
            min_score,candidate_list  = self.get_min_score_poslist(scorelist)
            print 'candidate_list:',candidate_list
            print 'got candidate_list'

            if min_score >2:
                # not a peak
                self.peak_dict['P'].append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                self.peak_dict['P'].append(candidate_list[0])
            else:
                # multiple min score
                best_candidate = self.get_steepest_slope_index(candidate_list,local_maxima_list,D5list)
                self.peak_dict['P'].append(best_candidate)

            # debug
            if debug ==True:
                print 'SWT peak pos:',self.peak_dict['P'][-1]
                pdb.set_trace()
            # debug plot
            # 1. get range
            seg_range = [min(posgroup),max(posgroup)]
            seg_range[0] = max(0,seg_range[0] - 200)
            seg_range[1] = min(len(raw_sig)-1,seg_range[1] + 200)
            # 2.plot
            seg = raw_sig[seg_range[0]:seg_range[1]]
            plt.ion()
            plt.figure(1)
            plt.clf()
            plt.plot(seg,label = 'ECG')
            # 3.plot group
            seg_posgroup = map(lambda x:x-seg_range[0],posgroup)
            plt.plot(seg_posgroup,map(lambda x: seg[x],seg_posgroup),label = 'posgroup',marker = 'o',markersize = 4,markerfacecolor = 'g',alpha = 0.7)
            # 4.plot peak pos
            # plot D6 postion
            peak_pos = self.peak_dict['P'][-1]-seg_range[0]
            peak_pos = int(peak_pos)
            plt.plot(peak_pos,seg[peak_pos],'yo',markersize = 12,alpha = 0.7,label = 'Final decision postion')
            # plot D5 postion
            # peak_pos = D5pos[-1]-seg_range[0]
            # peak_pos = int(peak_pos)
            # plt.plot(peak_pos,seg[peak_pos],'mo',markersize = 12,alpha = 0.7,label = 'D5 pos')
            # plot final decision postion
            # peak_pos = final_decision_peak - seg_range[0]
            # peak_pos = int(peak_pos)
            # plt.plot(peak_pos,seg[peak_pos],'r*',markersize = 12,alpha = 0.7,label = 'D5 pos')
            
            # plot Expert label position
            segment_expertlist = filter(lambda x: x[0]>=seg_range[0] and x[0]<seg_range[1],expert_label_list)
            if len(segment_expertlist) > 0:
                segment_expert_poslist,segment_expert_labellist = zip(*segment_expertlist)
                plt.plot(map(lambda x:x-seg_range[0],segment_expert_poslist),map(lambda x:seg[x-seg_range[0]],segment_expert_poslist),'rd',markersize = 12,alpha = 0.7,label = 'expert label')
            
            # 5.plot determin line
            seg_determin_line = self.cDlist[-4][seg_range[0]:seg_range[1]]
            seg_determin_lineD5 = self.cDlist[-5][seg_range[0]:seg_range[1]]
            seg_determin_lineD6 = self.cDlist[-3][seg_range[0]:seg_range[1]]

            plt.plot(seg_determin_line,'y',label = 'D4')
            plt.plot(seg_determin_lineD5,'g',label = 'D5')
            #plt.plot(seg_determin_lineD6,'m',label = 'D3')

            plt.title('{} {}'.format(self.recname,seg_range))
            plt.legend()
            plt.grid(True)
            plt.show()
            # debug stop
            pdb.set_trace()
        # return list of P peaks
        return self.peak_dict['P']

    #
    # detect boundaries using get_boundary_list function
    #
    def get_Ponset_list(self):
        label = 'Ponset'
        e3list = np.array(self.cDlist[-4])+np.array(self.cDlist[-3])
        crossZeroFunc = self.get_downward_cross_zero_list
        LongestSlopeIndexFunc = self.get_longest_downward_slope_index

        return self.get_boundary_list(label,e3list,crossZeroFunc,LongestSlopeIndexFunc)
    def get_Poffset_list(self):
        label = 'Poffset'
        e3list = np.array(self.cDlist[-4])+np.array(self.cDlist[-3])
        crossZeroFunc = self.get_local_minima_list
        LongestSlopeIndexFunc = self.get_longest_downward_slope_index

        return self.get_boundary_list(label,e3list,crossZeroFunc,LongestSlopeIndexFunc)
    def get_Toffset_list(self):
        label = 'Toffset'
        e3list = np.array(self.cDlist[-4])+np.array(self.cDlist[-5])
        crossZeroFunc = self.get_downward_cross_zero_list
        LongestSlopeIndexFunc = self.get_longest_downward_slope_index

        return self.get_boundary_list(label,e3list,crossZeroFunc,LongestSlopeIndexFunc)
    def get_Tonset_list(self,debug = False):
        label = 'Tonset'
        e3list = np.array(self.cDlist[-4])+np.array(self.cDlist[-5])
        crossZeroFunc = self.get_downward_cross_zero_list
        LongestSlopeIndexFunc = self.get_longest_downward_slope_index

        return self.get_boundary_list(label,e3list,crossZeroFunc,LongestSlopeIndexFunc,debug = debug)
    def get_boundary_list(self,label,e3list,crossZeroFunc,LongestSlopeIndexFunc,debug = False):

        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]==label,self.res_groups)

        if debug == True:
            print 'length of result groups:',len(res_groups)
            pdb.set_trace()

        res_groups = self.filter_smaller_nearby_groups(res_groups)
        # get label peak list
        #e3list = np.array(self.cDlist[-6])+np.array(self.cDlist[-5])

        #local_maxima_list = self.get_local_maxima_list(e3list)
        #local_maxima_list = self.get_cross_zero_list(e3list)
        local_maxima_list = crossZeroFunc(e3list)

        # debug
        #if debug == True:
            #plt.figure(2)
            #plt.plot(e3list)
            #plt.plot(local_maxima_list,map(lambda x:e3list[x],local_maxima_list),'y*',markersize = 14)
            #plt.show()

        # find local maxima point within each group
        for label,posgroup in res_groups:
            scorelist = []

            if debug == True:
                print 'Pos Group:',posgroup
                print 'mean Group:',np.mean(posgroup)

            for pos in posgroup:
                nearest_dist = self.bw_find_nearest(pos,local_maxima_list)
                scorelist.append((nearest_dist,pos))
            #scorelist.sort(key = lambda x:x[0])

            # get all pos with min score
            min_score,candidate_list  = self.get_min_score_poslist(scorelist)

            if min_score >2:
                # not a peak
                self.peak_dict[label].append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                self.peak_dict[label].append(candidate_list[0])
            else:
                # multiple min score
                longest_slope_index = LongestSlopeIndexFunc(candidate_list,local_maxima_list,e3list)
                self.peak_dict[label].append(local_maxima_list[longest_slope_index])

            # debug
            if debug ==True:
                print 'SWT peak pos:',self.peak_dict[label][-1]
                pdb.set_trace()
        # return list of label peaks
        return self.peak_dict[label]

    def get_peak_list(self):
        self.group_result()
        # get T&P peak list
        self.get_T_peaklist()
        self.get_P_peaklist()

def debug_SwtGroupRound(round_index,load_round_folder,save_round_folder,TargetRecordName,QRS_group_result_folder):
    # load the results
    #RoundFolder = r'F:\LabGit\ECG_RSWT\TestResult\paper\MultiRound4'
    ResultFolder = os.path.join(load_round_folder,'Round{}'.format(round_index))

    # each result file
    resfiles = glob.glob(os.path.join(ResultFolder,'result_*'))
    for resfilepath in resfiles:
        with open(resfilepath,'r') as fin:
            prdRes = json.load(fin)
        recname = prdRes[0][0]
        if recname != TargetRecordName:
            continue
        print 'current record name:',recname

        reslist1= prdRes[0][1]
        reslist2= prdRes[1][1]

        # ------------------------------------------------------
        # Group Results
        LeadResult = []
        # ------------------
        # lead I result dict
        eva = SWT_GroupResult2Leads(recname,reslist1,'sig',QRS_group_result_folder)
        eva.group_result()

        resDict = dict()

        # T
        reslist = eva.get_P_peaklist(extra_search_len = 0)
        resDict['T'] = reslist

        LeadResult.append(resDict)
        # ------------------
        # lead II result dict
        eva = SWT_GroupResult2Leads(recname,reslist2,'sig2',QRS_group_result_folder)
        eva.group_result()

        resDict = dict()

        # T
        reslist = eva.get_P_peaklist(extra_search_len = 0)
        resDict['T'] = reslist

        LeadResult.append(resDict)
        # ------------------------------------------------------
        # save to Group Result
        GroupDict = dict(recname = recname,LeadResult=LeadResult)
        #with open(os.path.join(save_round_folder,recname+'.json'),'w') as fout:
            #json.dump(GroupDict,fout,indent = 4,sort_keys = True)

        # debug
        print '-'*20
        print 'record name:',recname
        print 'Group Diction:',GroupDict

if __name__ == '__main__':
    # will append 'Round{}' behind those folders
    load_round_folder = os.path.join(curfolderpath,'RawResult')
    save_round_folder = os.path.join(curfolderpath)
    # for SWT to remove QRS region
    QRS_group_result_folder = os.path.join(os.path.dirname(curfolderpath),'MultiLead4')

    TargetRecordName = 'sel46'

    for ind in xrange(2, 23):
      print 'Current round:', ind
      current_round_folder = os.path.join(save_round_folder, 'SWT_P{}'.format(ind))
      cur_QRS_group_result_folder = os.path.join(QRS_group_result_folder,'GroupRound{}'.format(ind))
      debug_SwtGroupRound(ind,load_round_folder,current_round_folder,TargetRecordName,cur_QRS_group_result_folder)
    
