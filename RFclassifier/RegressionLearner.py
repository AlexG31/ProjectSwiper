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
import pywt
import logging
import random
import time
import pdb
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestRegressor
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
# from RFclassifier.extractfeature.Regression_Feature import Regression_Feature
import extractfeature.randomrelations as RandRelation
import WTdenoise.wtdenoise as wtdenoise
from QTdata.loadQTdata import QTloader
from MatlabPloter.Result2Mat_Format import reslist_to_mat
from RFclassifier.extractfeature.randomrelations import Window_Pair_Generator

# Global logger
log  = logging.getLogger()

## Main Scripts
# ==========
EPS = 1e-6
tmpmdlfilename = os.path.join(projhomepath,'tmpmdl.txt')

class RegressionLearner:
    def __init__(self,TargetLabel = 'T', SaveTrainingSampleFolder = None):
        # Feature&output for learner.
        self.TargetLabel = TargetLabel
        self.feature_pool_ = []
        self.output_pool_ = []
        self.MaxQRSWidth = 100
        self.MaxHeartBeatWidth = 350
        self.RF_TreeNumber = 40
        self.Tree_Max_Depth = 40
        self.QRSlabels = ('R',)
        self.QRS_segment_expand_length = 30
        self.SWT_diff_feature_expand = 50
        self.SWT_diff_feature_expand_skip_gap = 1

    def TrainQtRecords(self,record_list):
        '''API for QTdb: training model with given record_list.'''
        QTdb = QTloader()

        # Extracting feature from each record.
        for record_name in record_list:
            sig_struct = QTdb.load(record_name)
            raw_signal = sig_struct['sig']
            expert_labels = QTdb.getExpert(record_name)
            self.AddNewTrainingSignal(raw_signal, expert_labels)
            # Logging
            log.info('Extracted features from %s' % record_name)
            print 'Extracted features from %s' % record_name

        # Training with feature pool
        self.training()

    def TestQtRecords(self,save_folder, reclist = []):
        '''API for QTdb: testing given record_list.'''
        QTdb = QTloader()
        lead_result_list = []
        for record_name in reclist:
            sig_struct = QTdb.load(record_name)
            # Test lead1
            raw_signal = sig_struct['sig']
            expert_labels = QTdb.getExpert(record_name)
            predict_position_list = self.testing(raw_signal, expert_labels)
            test_result = zip(predict_position_list,
                    [self.TargetLabel,]*len(predict_position_list))
            lead_result = [record_name, test_result]
            lead_result_list.append(lead_result)
            # Test lead2
            raw_signal = sig_struct['sig2']
            expert_labels = QTdb.getExpert(record_name)
            predict_position_list = self.testing(raw_signal, expert_labels)
            test_result = zip(predict_position_list,
                    [self.TargetLabel,]*len(predict_position_list))
            lead_result = [record_name + '_sig2', test_result]
            lead_result_list.append(lead_result)
            # Save result.
            with open(os.path.join(save_folder, 'result_{}'.format(record_name)), 'w')\
                as fout:
                    json.dump(lead_result_list, fout, indent = 4)
                
    def AddNewTrainingSignal(self,rawsig,expert_marklist):
        '''Form regression feature pool.'''
        # Input with rawsig & marklist.
        # 1. remove QRS from rawsig
        # 2. Do SWT.
        # 3. a) Training of T:
        #      for each T&Toffset:
        #      if there's a QRS in front of it
        #       Extract feature & output
        #    b) Training of P:
        #      for each Ponset&P&Poffset:
        #      if there's a QRS behind it
        #       Extract feature & output
        
        # For debug
        backup_signal = rawsig[:]

        # preprocess
        # expert_marklist is [(pos,label)...]
        # sort by position.
        expert_marklist.sort(key = lambda x:x[0])
        # Set self.cDlist.
        self.nonQRS_swt(rawsig,expert_marklist)

        # a) training T labels.
        # TODO
        self.AddT2feature(rawsig,expert_marklist, debug = True, original_signal = backup_signal)
        # b) training P labels.
        # TODO
    def AddT2feature(self,rawsig,expert_marklist, debug = False, original_signal = None):
        # For each target_label:
        #  get QRS region before and after it.
        #  get segment signal& segment cDlist
        #  get QRS distance array
        target_label = self.TargetLabel
        N_expert_label = len(expert_marklist)
        for ind in xrange(0,N_expert_label):
            pos,label = expert_marklist[ind]
            if label == target_label:
                # Find QRS bebore pos:
                before_label_dict = dict()
                before_ind = -1
                for before_ind in xrange(ind-1,-1,-1):
                    before_pos, before_label = expert_marklist[before_ind]
                    if pos - before_pos > self.MaxHeartBeatWidth:
                        break
                    if before_label not in before_label_dict:
                        before_label_dict[before_label] = before_pos
                        # got QRS before.
                        if all(map(lambda x:x in before_label_dict,self.QRSlabels)):
                            break
                if all(map(lambda x:x in before_label_dict,self.QRSlabels)) == False:
                    log.warning('Can not find QRS before position {}.'.format(pos))
                    # Skip if current label is the first one in label list.
                    if before_ind < 0:
                        continue
                    # It is tolerable if the QRS is outside of self.MaxHeartBeatWidth
                    before_label_dict = self.FillInBlankQRSMark(pos, before_label_dict, min)
                    # qrs_single_position = None
                    # for qrs_label in self.QRSlabels:
                        # if qrs_label not in before_label_dict:
                            # if qrs_single_position is None:
                                # qrs_single_position = pos - self.MaxHeartBeatWidth/2
                            # before_label_dict[qrs_label] = qrs_single_position
                    # else:
                        # qrs_single_position = before_label_dict[qrs_label]
                # Find QRS after pos
                after_label_dict = dict()
                for after_ind in xrange(ind+1,N_expert_label):
                    after_pos, after_label = expert_marklist[after_ind]
                    if after_pos - pos > self.MaxHeartBeatWidth:
                        break
                    if after_label not in after_label_dict:
                        after_label_dict[after_label] = after_pos
                        # got QRS after.
                        if all(map(lambda x:x in after_label_dict,self.QRSlabels)):
                            break
                if all(map(lambda x:x in after_label_dict,self.QRSlabels)) == False:
                    # Skip if current label is the last one in label list.
                    if after_ind >= N_expert_label:
                        log.warning('Can not find QRS after position {}.'.format(pos))
                        continue
                    # It is tolerable if the QRS is outside of self.MaxHeartBeatWidth
                    after_label_dict = self.FillInBlankQRSMark(pos, after_label_dict, max)
                    # qrs_single_position = None
                    # for qrs_label in self.QRSlabels:
                        # if qrs_label not in after_label_dict:
                            # if qrs_single_position is None:
                                # qrs_single_position = pos + self.MaxHeartBeatWidth/2
                            # after_label_dict[qrs_label] = qrs_single_position
                        # else:
                            # qrs_single_position = after_label_dict[qrs_label]
                    
                    
                # Get signal segment.
                # CHECK if position: Q<=R<=S
                self.check_validQRS(before_label_dict)
                self.check_validQRS(after_label_dict)
                # Segment is from Q_before to S_after.
                seg_range = [before_label_dict['R'] - self.QRS_segment_expand_length,after_label_dict['R'] + self.QRS_segment_expand_length]
                # prevent seg_range out of bound
                seg_range[0] = max(0, seg_range[0])
                seg_range[1] = min(len(rawsig)-1, seg_range[1])

                sig_seg = rawsig[seg_range[0]:seg_range[1]+1]
                # Get cDlist segment.
                cDlist_seg = []
                for detail_signal in self.cDlist:
                    cDlist_seg.append(detail_signal[seg_range[0]:seg_range[1]+1])
                # Get QRS distance array.
                seg_len = seg_range[1] + 1 - seg_range[0]
                QRS_distance_before = range(0, seg_len)
                QRS_distance_after = range(seg_len-1, -1, -1)
                QRS_distance_ratio = map(lambda x:float(x)/seg_len,QRS_distance_before)
                # Form current feature vector
                current_feature_vector = self.FormFeature(
                        cDlist_seg,
                        QRS_distance_before,
                        QRS_distance_after,
                        QRS_distance_ratio,
                        sig_seg, debug = debug)
                current_output = pos - seg_range[0]
                # Add to Training Pool
                self.feature_pool_.append(current_feature_vector)
                self.output_pool_.append(current_output)

                # debug
                if debug == True:
                    # Check: 
                    #   1. Position of T mark
                    #   2. The segment of QRS
                    plt.ion()
                    plt.figure(1)
                    plt.clf()

                    # sub figure 1 (Removed QRS signal)
                    plt.subplot(211)
                    plt.title('segment [%d, %d]' % (seg_range[0], seg_range[1]))
                    plt.plot(sig_seg,label = 'ECG')
                    plt.plot(map(lambda x:x-seg_range[0],seg_range),
                            map(lambda x:sig_seg[x-seg_range[0]],seg_range),
                            'ro', label = 'R boundary')
                    plt.plot(pos-seg_range[0],
                            sig_seg[pos-seg_range[0]],
                            'gd', label = self.TargetLabel)
                    plt.grid(True)
                    # subplot 2 (orignal signal)
                    plt.subplot(212)
                    plt.plot(original_signal[seg_range[0]:seg_range[1]+1])
                    plt.grid(True)

                    plt.legend()
                    plt.show()
                    pdb.set_trace()

                


    # Note That boundary_function is either max or min
    # pos is current start position.
    def FillInBlankQRSMark(self, pos, qrs_label_dict, boundary_function):
        '''Fill the missing QRS mark(s).'''
        # Logging
        log.debug('--')
        log.debug('Original qrs_label_dict:')
        log.debug(qrs_label_dict)

        qrs_single_position = None
        for qrs_label in self.QRSlabels:
            if qrs_label in qrs_label_dict:
                if qrs_single_position is None:
                    qrs_single_position = qrs_label_dict[qrs_label]
                else:
                    qrs_single_position = boundary_function(qrs_single_position,qrs_label_dict[qrs_label])
        for qrs_label in self.QRSlabels:
            if qrs_label not in qrs_label_dict:
                if qrs_single_position is None:
                    qrs_single_position = pos + self.MaxHeartBeatWidth/2
                qrs_label_dict[qrs_label] = qrs_single_position
                log.warning('Adding {} to {}'.format(qrs_label,qrs_single_position))
        return qrs_label_dict
    def CropFeatureWindow(self,cDlist_seg,QRS_distance_before, QRS_distance_after,QRS_distance_ratio, sig_seg):
        '''Crop the length of each feature signal to self.MaxHeartBeatWidth.'''
        # All signal segment should have the same length.
        N_current = len(QRS_distance_ratio)
        if N_current < self.MaxHeartBeatWidth:
            # Stuffing polyfoam behind.
            QRS_distance_after.extend([0,]*(self.MaxHeartBeatWidth - N_current))
            QRS_distance_before.extend(range(QRS_distance_before[-1]+1, self.MaxHeartBeatWidth))
            QRS_distance_ratio.extend([1,]*(self.MaxHeartBeatWidth - N_current))
            sig_seg.extend([sig_seg[-1],] * (self.MaxHeartBeatWidth - N_current))
            for ind in xrange(0,len(cDlist_seg)):
                cDlist_seg[ind].extend([cDlist_seg[ind][-1],]*(self.MaxHeartBeatWidth - N_current))
        elif N_current > self.MaxHeartBeatWidth:
            # cutoff the after part
            log.warning('Heart Beat Segment is too long, cutting off the tail part!')
            QRS_distance_after = QRS_distance_after[0:self.MaxHeartBeatWidth]
            QRS_distance_before = QRS_distance_before[0:self.MaxHeartBeatWidth]
            QRS_distance_ratio= QRS_distance_ratio[0:self.MaxHeartBeatWidth]
            sig_seg = sig_seg[0:self.MaxHeartBeatWidth]
            for ind in xrange(0,len(cDlist_seg)):
                cDlist_seg[ind] = cDlist_seg[ind][0:self.MaxHeartBeatWidth]
            
        return (cDlist_seg,QRS_distance_before, QRS_distance_after,QRS_distance_ratio, sig_seg)
            
    def FormFeature(self, cDlist_seg, QRS_distance_before,
            QRS_distance_after, QRS_distance_ratio, sig_seg,
            debug = False 
            ):
        '''Form feature from the segment signal given.'''
        # Normalise the length of each input feature signal.
        cDlist_seg,QRS_distance_before, QRS_distance_after,QRS_distance_ratio, sig_seg = self.CropFeatureWindow(
                  cDlist_seg,
                  QRS_distance_before,
                  QRS_distance_after,
                  QRS_distance_ratio,
                  sig_seg)
        feature_vector = []

        # logging info
        log.info('Only extracting features from SWT level 2 to 6.')

        for detail_level in cDlist_seg[1:6]:
            feature_vector.extend(detail_level)
            feature_vector.extend(map(lambda x:abs(x), detail_level))
            # Add pair features.
            for pair_x in xrange(0, len(detail_level)):
                for pair_y in xrange(pair_x+1,
                        min(pair_x + self.SWT_diff_feature_expand,
                        len(detail_level)),
                        self.SWT_diff_feature_expand_skip_gap):
                    feature_vector.append(detail_level[pair_x] - detail_level[pair_y])
                    feature_vector.append(abs(detail_level[pair_x] - detail_level[pair_y]))
        # Add distance to QRS feature.
        #feature_vector.extend(QRS_distance_after)
        feature_vector.extend(QRS_distance_ratio)
        feature_vector.extend(QRS_distance_before)
        feature_vector.extend(sig_seg)
        # debug
        if debug == True:
            plt.figure(2)
            plt.clf()
            N_subplot_level = 6
            plt.subplot(N_subplot_level, 1, 1)
            plt.plot(sig_seg)
            plt.grid(True)

            for di in range(1, 6):
                plt.subplot(N_subplot_level, 1, di + 1)
                plt.plot(cDlist_seg[di])
                plt.grid(True)
            
        #print type(feature_vector)
        #with open(os.path.join(projhomepath,'tmp.json'),'w') as fout:
            #json.dump(feature_vector,fout)
        #pdb.set_trace()
        return feature_vector

    def check_validQRS(self, label_dict):
        '''Check QRS in label_dict is valid.'''
        if all(map(lambda x:x in label_dict, self.QRSlabels)) == False:
            print label_dict
            raise Exception('QRS not all in label_dict!')
        # if label_dict['Ronset'] > label_dict['R'] or label_dict['R'] - label_dict['Ronset'] > self.MaxQRSWidth:
            # print label_dict
            # raise Exception('QRS mispositioned!')
        # if label_dict['R'] > label_dict['Roffset'] or label_dict['Roffset'] - label_dict['R'] > self.MaxQRSWidth:
            # print label_dict
            # raise Exception('QRS mispositioned!')
            
                


    def training(self):
        '''Train RandomForestClassifier.'''
        self.rfclassifier = RandomForestRegressor(
                n_estimators = self.RF_TreeNumber,
                max_depth = self.Tree_Max_Depth,
                n_jobs =4,
                warm_start = False)
        self.rfclassifier.fit(self.feature_pool_,self.output_pool_)
        self.mdl = self.rfclassifier

    def testing(self,rawsig,expert_marklist):
        '''Testing the position.'''
        expert_marklist.sort(key = lambda x:x[0])
        # Set self.cDlist
        self.nonQRS_swt(rawsig,expert_marklist)
        # Output
        output_prediction_list = []
        # get QRS region.
        N_expert_label = len(expert_marklist)
        for ind in xrange(0, N_expert_label):
            pos,label = expert_marklist[ind]
            # skip other labels
            if label != 'R':
                continue
            # debug
            #print '---testing---'
            #print 'ind = {}, {}'.format(ind,expert_marklist[ind])
            #pdb.set_trace()

            # Find QRS bebore pos:
            before_label_dict = dict()
            for before_ind in xrange(ind,N_expert_label):
                before_pos, before_label = expert_marklist[before_ind]
                if before_pos - pos > self.MaxHeartBeatWidth:
                    break
                if before_label not in before_label_dict:
                    before_label_dict[before_label] = before_pos
                    # got QRS before.
                    if all(map(lambda x:x in before_label_dict,self.QRSlabels)):
                        break
            if all(map(lambda x:x in before_label_dict,self.QRSlabels)) == False:
                log.warning('Can not find QRS before position {}.'.format(pos))
                # Skip if current label is the first one in label list.
                if before_ind < 0:
                    continue
                # It is tolerable if the QRS is outside of self.MaxHeartBeatWidth
                before_label_dict = self.FillInBlankQRSMark(pos, before_label_dict, min)
                # qrs_single_position = None
                # for qrs_label in self.QRSlabels:
                    # if qrs_label not in before_label_dict:
                        # if qrs_single_position is None:
                            # qrs_single_position = pos - self.MaxHeartBeatWidth/2
                        # before_label_dict[qrs_label] = qrs_single_position
                    # else:
                        # qrs_single_position = before_label_dict[qrs_label]
            # Find QRS after pos
            after_label_dict = dict()
            for after_ind in xrange(before_ind,N_expert_label):
                after_pos, after_label = expert_marklist[after_ind]
                if after_pos - pos > self.MaxHeartBeatWidth:
                    break
                if after_label not in after_label_dict:
                    after_label_dict[after_label] = after_pos
                    # got QRS after.
                    if all(map(lambda x:x in after_label_dict,self.QRSlabels)):
                        break
            if all(map(lambda x:x in after_label_dict,self.QRSlabels)) == False:
                # Skip if current label is the last one in label list.
                if after_ind >= N_expert_label:
                    log.warning('Can not find QRS after position {}.'.format(pos))
                    continue
                # It is tolerable if the QRS is outside of self.MaxHeartBeatWidth
                after_label_dict = self.FillInBlankQRSMark(pos, after_label_dict, max)
                # qrs_single_position = None
                # for qrs_label in self.QRSlabels:
                    # if qrs_label not in after_label_dict:
                        # if qrs_single_position is None:
                            # qrs_single_position = pos + self.MaxHeartBeatWidth/2
                        # after_label_dict[qrs_label] = qrs_single_position
                    # else:
                        # qrs_single_position = after_label_dict[qrs_label]
                
                
            # Get signal segment.
            # CHECK if position: Q<R<S
            self.check_validQRS(before_label_dict)
            self.check_validQRS(after_label_dict)
            # Segment is from Q_before to S_after.
            seg_range = [before_label_dict['R'] - self.QRS_segment_expand_length,after_label_dict['R'] + self.QRS_segment_expand_length]
            # prevent seg_range out of bound
            seg_range[0] = max(0, seg_range[0])
            seg_range[1] = min(len(rawsig)-1, seg_range[1])

            sig_seg = rawsig[seg_range[0]:seg_range[1]+1]
            # Get cDlist segment.
            cDlist_seg = []
            for detail_signal in self.cDlist:
                cDlist_seg.append(detail_signal[seg_range[0]:seg_range[1]+1])
            # Get QRS distance array.
            seg_len = seg_range[1] + 1 - seg_range[0]
            # debug:
            if seg_len <= 1 or len(cDlist_seg) == 0 or len(sig_seg) == 0:
                log.warning('Warning: seg_len <= 1!')
                continue
            QRS_distance_before = range(0, seg_len)
            QRS_distance_after = range(seg_len-1, -1, -1)
            QRS_distance_ratio = map(lambda x:float(x)/seg_len,QRS_distance_before)
            # Form current feature vector
            current_feature_vector = self.FormFeature(cDlist_seg,
                    QRS_distance_before,
                    QRS_distance_after,
                    QRS_distance_ratio,
                    sig_seg)
            # Prediction
            current_feature_vector = np.array(current_feature_vector)
            predict_result = self.rfclassifier.predict(
                    current_feature_vector.reshape(1,-1))
            predict_result += seg_range[0]
            # convert predict result to int
            predict_result = predict_result.tolist()
            predict_result = predict_result[0]
            output_prediction_list.append(predict_result)
        return output_prediction_list



    def getNonQRSsig(self,rawsig,MarkList,QRS_width_threshold = 180):
        # QRS width threshold:
        #   The max possible distance between Q & S,
        #    otherwise there's no matching S for Q.

        expert_marklist = MarkList
        
        # Use QRS region to flattern the signal
        expert_marklist = filter(lambda x:'R' in x[1] and len(x[1])>1,expert_marklist)
        # Get QRS region
        expert_marklist.sort(key=lambda x:x[0])
        QRS_regionlist = []
        N_Rlist = len(expert_marklist)
        for ind in xrange(0,N_Rlist-1):
            pos, label = expert_marklist[ind]
            # last one: no match pair
            if ind == N_Rlist - 1:
                break
            elif label != 'Ronset':
                continue
            # get next label
            next_pos,next_label = expert_marklist[ind+1]
            if next_label == 'Roffset':
                if next_pos - pos >=QRS_width_threshold:
                    log.warning('Warning: no matching Roffset found!')
                else:
                    QRS_regionlist.append([pos,next_pos])
                    # print 'Adding:',pos,next_pos
                    # flattern the signal
                    amp_start = rawsig[pos]
                    amp_end = rawsig[next_pos]
                    flat_segment = map(lambda x:amp_start+float(x)*(amp_end-amp_start)/(next_pos-pos),xrange(0,next_pos-pos))
                    for segment_index in xrange(pos,next_pos):
                        rawsig[segment_index] = flat_segment[segment_index-pos]
        return rawsig

    def crop_data_for_swt(self,rawsig):
        # crop rawsig, make the len(rawsig) is 2^N.
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
        return rawsig

    def nonQRS_swt(self,rawsig,expert_marklist,wavelet = 'db6',MaxLevel = 9):
        '''Get swt without QRS regions, modify rawsig whthin this function.'''
        # Get Swt coef for rawsig.
        rawsig = self.getNonQRSsig(rawsig,expert_marklist)
        rawsig = self.crop_data_for_swt(rawsig)

        coeflist = pywt.swt(rawsig,wavelet,MaxLevel)
        cAlist,cDlist = zip(*coeflist)
        # append to self.cDlist
        self.cAlist = []
        self.cDlist = []
        for ind in xrange(0,len(cAlist)):
            self.cAlist.append(cAlist[ind].tolist())
            self.cDlist.append(cDlist[ind].tolist())
        return None

if __name__ == '__main__':
    pass
