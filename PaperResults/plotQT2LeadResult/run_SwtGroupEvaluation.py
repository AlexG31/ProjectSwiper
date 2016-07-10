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
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
print 'projhomepath:',projhomepath
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components

from QTdata.loadQTdata import QTloader 
from Evaluation2Leads import Evaluation2Leads

class SWT_GroupResult2Leads:
    ''' Find P&T peak with SWT+db6
    '''
    def __init__(self,recname,reslist,leadname,MaxSWTLevel = 9):
        self.recres = reslist
        #self.LeadRes = (reslist,reslist2)

        self.recname = recname
        self.QTdb = QTloader()
        self.sig_struct = self.QTdb.load(self.recname)
        self.rawsig = self.sig_struct[leadname]

        self.res_groups = None
        self.peak_dict = dict(T=[],P=[],Ponset = [],Poffset = [],Tonset = [],Toffset = [])
        self.getSWTcoeflist(MaxLevel = MaxSWTLevel)

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

    def getSWTcoeflist(self,MaxLevel = 9):
        # crop two leads
        self.rawsig = self.crop_data_for_swt(self.rawsig)

        print '-'*3
        print 'len(rawsig)= ',len(self.rawsig)
        print 'SWT maximum level =',pywt.swt_max_level(len(self.rawsig))
        coeflist = pywt.swt(self.rawsig,'db6',MaxLevel)

        cAlist,cDlist = zip(*coeflist)
        self.cAlist = cAlist
        self.cDlist = cDlist

        
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

    def get_longest_slope_index(self,candidate_list,crosszerolist,e4list):
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

            # Find current slope length
            right_bound = N-1
            left_bound = 0

            # reached N-1 or local maxima
            for cur_pos in xrange(peak_pos,N-1):
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
            if cur_slope_len>max_slope_len:
                max_slope_len = cur_slope_len
                best_candidate = peak_pos
        return best_candidate

                
    def get_T_peaklist(self):
        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]=='T',self.res_groups)
        res_groups = self.filter_smaller_nearby_groups(res_groups)

        # get T peak
        e4list = np.array(self.cDlist[-4])+np.array(self.cDlist[-5])
        crosszerolist = self.get_cross_zero_list(e4list)
        for label,posgroup in res_groups:
            scorelist = []
            for pos in posgroup:
                nearest_dist = self.bw_find_nearest(pos,crosszerolist)
                scorelist.append((nearest_dist,pos))

            # get all pos with min score
            min_score,candidate_list  = self.get_min_score_poslist(scorelist)

            if min_score >2:
                # not a peak
                self.peak_dict['T'].append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                self.peak_dict['T'].append(candidate_list[0])
            else:
                # multiple min score
                longest_slope_index = self.get_longest_slope_index(candidate_list,crosszerolist,e4list)
                self.peak_dict['T'].append(crosszerolist[longest_slope_index])
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
    def get_P_peaklist(self,debug = False):

        if self.res_groups is None:
            # group the raw predition results if not grouped already
            self.group_result()
        res_groups = filter(lambda x:x[0]=='P',self.res_groups)
        res_groups = self.filter_smaller_nearby_groups(res_groups)
        # get P peak list
        #e3list = np.array(self.cDlist[-6])+np.array(self.cDlist[-5])
        e3list = np.array(self.cDlist[-4])

        #local_maxima_list = self.get_local_maxima_list(e3list)
        local_maxima_list = self.get_cross_zero_list(e3list)

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
                self.peak_dict['P'].append(np.mean(posgroup))
            elif len(candidate_list) ==1:
                # only mean score by SWT
                self.peak_dict['P'].append(candidate_list[0])
            else:
                # multiple min score
                longest_slope_index = self.get_longest_slope_index(candidate_list,local_maxima_list,e3list)
                self.peak_dict['P'].append(local_maxima_list[longest_slope_index])

            # debug
            if debug ==True:
                print 'SWT peak pos:',self.peak_dict['P'][-1]
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

def SwtGroupRound(round_index,load_round_folder,save_round_folder):
    # load the results
    #RoundFolder = r'F:\LabGit\ECG_RSWT\TestResult\paper\MultiRound4'
    ResultFolder = os.path.join(load_round_folder,'Round{}'.format(round_index))

    # each result file
    resfiles = glob.glob(os.path.join(ResultFolder,'result_*'))
    for resfilepath in resfiles:
        with open(resfilepath,'r') as fin:
            prdRes = json.load(fin)
        recname = prdRes[0][0]
        reslist1= prdRes[0][1]
        reslist2= prdRes[1][1]

        # ------------------------------------------------------
        # Group Results
        LeadResult = []
        # ------------------
        # lead I result dict
        eva = SWT_GroupResult2Leads(recname,reslist1,'sig')
        eva.group_result()

        resDict = dict()

        # T
        reslist = eva.get_T_peaklist()
        resDict['T'] = reslist

        # P
        reslist = eva.get_P_peaklist()
        resDict['P'] = reslist
        
        # Ponset
        reslist = eva.get_Ponset_list()
        resDict['Ponset'] = reslist

        # Poffset
        reslist = eva.get_Poffset_list()
        resDict['Poffset'] = reslist
        
        # Toffset
        reslist = eva.get_Toffset_list()
        resDict['Toffset'] = reslist

        LeadResult.append(resDict)
        # ------------------
        # lead II result dict
        eva = SWT_GroupResult2Leads(recname,reslist2,'sig2')
        eva.group_result()

        resDict = dict()

        # T
        reslist = eva.get_T_peaklist()
        resDict['T'] = reslist

        # P
        reslist = eva.get_P_peaklist()
        resDict['P'] = reslist
        
        # Ponset
        reslist = eva.get_Ponset_list()
        resDict['Ponset'] = reslist

        # Poffset
        reslist = eva.get_Poffset_list()
        resDict['Poffset'] = reslist
        
        # Toffset
        reslist = eva.get_Toffset_list()
        resDict['Toffset'] = reslist

        LeadResult.append(resDict)
        # ------------------------------------------------------
        # save to Group Result
        GroupDict = dict(recname = recname,LeadResult=LeadResult)
        with open(os.path.join(save_round_folder,'SWT_GroupRound{}'.format(round_index),recname+'.json'),'w') as fout:
            json.dump(GroupDict,fout,indent = 4,sort_keys = True)

        # debug
        #print 'record name:',recname

def RunEval(RoundInd):
    GroupSaveFolder = os.path.join(curfolderpath,'MultiLead4','SWT_GroupRound{}'.format(RoundInd))
    resultfilelist = glob.glob(os.path.join(GroupSaveFolder,'*.json'))
    evalinfopath = os.path.join(curfolderpath,'MultiLead4','SwtEvalInfoRound{}'.format(RoundInd))
    os.mkdir(evalinfopath)

    # print result files
    #for ind, fp in enumerate(resultfilelist):
        #print '[{}]'.format(ind),'fp:',fp

    ErrDict = dict()
    ErrData = dict()

    for label in ['P','T','Ponset','Poffset','Toffset']:
        ErrData[label] = dict()
        ErrDict[label] = dict()
        errList = []
        FNcnt = 0

        for file_ind in xrange(0,len(resultfilelist)):
            # progress info
            #print 'label:',label
            #print 'file_ind',file_ind

            eva= Evaluation2Leads()
            eva.loadlabellist(resultfilelist[file_ind],label,supress_warning = True)
            eva.evaluate(label)

            # total error
            errList.extend(eva.errList)
            FN = eva.getFNlist()
            FNcnt += FN

            # -----------------
            # error statistics

            #ErrDict[label]['mean'] = np.mean(eva.errList)
            #ErrDict[label]['std'] = np.std(eva.errList)
            #ErrDict[label]['FN'] = eva.getFNlist()

            # debug
            #print '--'
            #print 'record: {}'.format(os.path.split(resultfilelist[file_ind])[-1])
            #print 'Error Dict:','label:',label
            #print ErrDict[label]

            # ======
            #eva.plot_evaluation_result()
            #pdb.set_trace()
        ErrData[label]['errList'] = errList
        ErrData[label]['FN'] = FNcnt

        ErrDict[label]['mean'] = np.mean(errList)
        ErrDict[label]['std'] = np.std(errList)
        ErrDict[label]['FN'] = FNcnt

    print '-'*10
    print 'ErrDict'
    print ErrDict

    # write to json
    with open(os.path.join(evalinfopath,'ErrData.json'),'w') as fout:
        json.dump(ErrData,fout,indent = 4,sort_keys = True)
        print '>>Dumped to json file: ''ErrData.json''.'
    # error statistics
    with open(os.path.join(evalinfopath,'ErrStat.json'),'w') as fout:
        json.dump(ErrDict,fout,indent = 4,sort_keys = True)
        print '>>Dumped to json file: ''ErrStat.json''.'

if __name__ == '__main__':
    load_round_folder = r'F:\LabGit\ECG_RSWT\TestResult\paper\MultiRound4'
    save_round_folder = os.path.join(curfolderpath,'MultiLead4')
    for ind in xrange(1,56):
      print 'Current round:', ind
      #os.mkdir(os.path.join(save_round_folder, 'SWT_GroupRound{}'.format(ind)))
      #SwtGroupRound(ind,load_round_folder,save_round_folder)
      RunEval(ind)
      
    
