#encoding:utf-8
"""
ECG classification with Random Forest
Author : Gaopengfei
"""
import os
import sys
import json
import logging
import math
import pickle
import random
import time
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
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
log = logging.getLogger()

# my project components
import extractfeature.extractfeature as extfeature
import extractfeature.randomrelations as RandRelation
import WTdenoise.wtdenoise as wtdenoise
import QTdata.loadQTdata as QTdb
from MatlabPloter.Result2Mat_Format import reslist_to_mat

# Father classifiersdfier
from RFclassifier.ClassificationLearner import timing_for
from RFclassifier.ClassificationLearner import valid_signal_value
from RFclassifier.ClassificationLearner import ECGrf


## Main Scripts
# ==========
EPS = 1e-6

class ParallelRfClassifier(ECGrf):
    '''Like the ClassificationLearner, but in parallel.'''
    def __init__(self, MAX_PARA_CORE = 6, SaveTrainingSampleFolder = None):
        super(ParallelRfClassifier,self).__init__(
                MAX_PARA_CORE = 6,
                SaveTrainingSampleFolder = SaveTrainingSampleFolder)

    def testing_with_extractor(self, rfmdl, signal_length, feature_extractor):
        ''' Testing a feature vector from feature_extractor in test_range.'''

        # Leaving testing Blank Regions in Head&Tail of the tested signal,
        # to avoid feature insufficiency.
        WindowLen = conf['winlen_ratio_to_fs']*conf['fs']
        Blank_Len = WindowLen/2+1

        if conf['QTtest'] == 'FastTest':
            # Only test regions with expert labels for comparing detection result.
            prRange = []
            TestRegionFolder = os.path.join(projhomepath, 'QTdata', 'QT_TestRegions')
            with open(os.path.join(TestRegionFolder,
                '{}_TestRegions.pkl'.format(recname)),'rb') as fin:
                TestRegions = pickle.load(fin)
            for region in TestRegions:
                prRange.extend(range(region[0],region[1]+1))
        else:
            # Default: full range test
            prRange = range(Blank_Len, N_signal - 1 - Blank_Len)
        
        return self.test_with_positionlist(
                    rfmdl,
                    prRange,
                    feature_extractor)
    def testing(
            self,
            reclist,
            rfmdl = None,
            saveresultfolder = None):
        '''Testing ECG record with trained model.'''

        # Default parameters
        if rfmdl is None:
            rfmdl = self.mdl

        # Parallel 
        if conf['ParallelTesting'] == 'True':
            MultiProcess = 'on'
        else:
            MultiProcess = 'off'

        # Test all files in reclist
        PrdRes = []
        for recname in reclist:
            # --------------------
            # start test time
            # --------------------
            # load signal data from QTdb.
            sig = self.QTloader.load(recname)
            # Signal value can not contain inf.
            if valid_signal_value(sig['sig']) == False:
                continue

            # ------------------------
            # test lead I
            # ------------------------
            raw_signal = sig['sig']
            plt.figure(1)
            plt.plot(raw_sig)
            feature_extractor = extfeature.ECGfeatures(raw_signal)
            N_signal = len(raw_signal)

            # Testing
            time_rec0 = time.time()
            record_predict_result = self.testing_with_extractor(
                    rfmdl,
                    N_signal,
                    feature_extractor)
            # Logging testing time.
            time_rec1 = time.time()
            log.info('Testing time for %s lead1 is %d seconds',recname,time_rec1-time_rec0)

            PrdRes.append((recname,record_predict_result))
            
            # ------------------------
            # test lead II
            # ------------------------
            raw_signal = sig['sig2']
            plt.figure(2)
            plt.plot(raw_sig)
            plt.show()
            feature_extractor = extfeature.ECGfeatures(raw_signal)
            N_signal = len(raw_signal)

            # Testing...
            time_rec0 = time.time()
            record_predict_result = self.testing_with_extractor(rfmdl,
                    N_signal, feature_extractor)
            # Logging testing time.
            time_rec1 = time.time()
            log.info('Testing time for %s lead1 is %d seconds',recname,time_rec1-time_rec0)

            PrdRes.append(('{}_sig2'.format(recname), record_predict_result))

        # Save prediction result.
        if saveresultfolder is not None:
            saveresult_filename = os.path.join(saveresultfolder,'result_{}'.format(recname))
            with open(saveresult_filename,'w') as fout:
                # No detection
                if PrdRes is None or len(PrdRes) == 0:
                    PrdRes =()
                json.dump(PrdRes,fout,indent = 4,sort_keys = True)
                print 'Saved prediction result to {}'.format(saveresult_filename)
        return PrdRes

    def test_with_positionlist(self,rfmdl,poslist,featureextractor):
        '''Using rf to test given feature.

        Return:
            List of (position, prediction_result, score) tuples.
        '''
        PrdRes = []
        # prediction probability
        PrdProba = []
        # get class->index dictionary
        dict_class2index = dict()
        cur_index = 0
        for class_label in rfmdl.classes_:
            dict_class2index[class_label] = cur_index
            cur_index += 1

        # testing & show progress
        Ntest = self.MaxTestSample
        Lposlist = len(poslist)
        Nbuckets = int(Lposlist/Ntest)
        if Nbuckets * Ntest < Lposlist:
            Nbuckets += 1
        for i in range(0,Nbuckets):
            # progress bar
            sys.stdout.write('\rTesting: {:02}buckets left.'.format(Nbuckets - i -1))
            sys.stdout.flush()

            # get each bucket's range
            #
            index_L = i*Ntest
            index_R = (i+1)*Ntest
            index_R = min(index_R,Lposlist)
            samples_tobe_tested = map(featureextractor.frompos,poslist[index_L:index_R])
            # predict
            #
            # Benchmark info
            time_predict = time.time()

            res = rfmdl.predict(samples_tobe_tested)
            mean_proba = rfmdl.predict_proba(samples_tobe_tested)
            label_proba_vec = map(lambda x:x[1][dict_class2index[x[0]]],zip(res,mean_proba))

            PrdRes.extend(res.tolist())
            PrdProba.extend(label_proba_vec)

            # Logging
            log.debug('Time cost for predict: %f' % (time.time() - time_predict))
            
            
        if len(PrdRes) != len(poslist):
            print 'len(prd Results) = ',len(PrdRes),'Len(poslist) = ',len(poslist)
            print 'PrdRes:'
            print PrdRes
            print 'poslist:'
            print poslist
            pdb.set_trace()
            raise StandardError('test Error: output label length doesn''t match!')
        return zip(poslist,PrdRes,PrdProba)

    def TestQtRecords(self,saveresultfolder,
            reclist = ['sel103',],mdl = None,TestResultFileName = None):
        '''Parallel testing Qt records with trainied model.'''
        print 'TestQtRecords in ParallelClassifier.'
        # default parameter
        if mdl is None:
            mdl = self.mdl

        # save obj for multi-process testing.
        with open('/tmp/rf-classifier.mdl','wb') as fout:
            pickle.dump(self.mdl, fout)

        pool = Pool(4)
        # Time cost.
        test_start_time = time.time()

        args = zip(reclist,[saveresultfolder,]*len(reclist))

        pool.map(ParallelTesting, args)
        test_end_time = time.time()
        log.info('Total testing time is %d seconds.' % (test_end_time - test_start_time))
        pool.close()
        


# ======================================
# Parallelly Collect training sample for each rec
# ======================================
def Parallel_CollectRecFeature(recname):
    print 'Parallel Collect RecFeature from {}'.format(recname)
    # load blank area list
    blkArea = conf['labelblankrange']
    ## debug log:
    debugLogger.dump('collecting feature for {}\n'.format(recname))
    # load sig
    QTloader = QTdb.QTloader()
    sig = QTloader.load(recname)
    if valid_signal_value(sig['sig']) == False:
        return [[],[]]
    # blank list
    blklist = None
    if recname in blkArea:
        print recname,'in blank Area list.'
        blklist = blkArea[recname]
    tX,ty = ECGrf.collectfeaturesforsig(sig,
            SaveTrainingSampleFolder,
            blankrangelist = blklist,
            recID = recname)
    return (tX,ty)
    
def ParallelTesting(params):
    '''For parallel testing purpose.'''
    recname, result_folder = params
    with open('/tmp/rf-classifier.mdl','rb') as fin:
        trained_model = pickle.load(fin)
    classifier = ECGrf()
    # Load Qt records for testing

    QT_results = list()
    qt = QTdb.QTloader()
    sig = qt.load(recname)
    TestRegionFolder = os.path.join(projhomepath, 'QTdata', 'QT_TestRegions')
    with open(os.path.join(TestRegionFolder,'{}_TestRegions.pkl'.format(recname)),'rb') as fin:
        TestRegions = pickle.load(fin)
    # Lead I
    results = classifier.testing_API(sig['sig'],
            rfmdl = trained_model,
            saveresultfolder = result_folder,
            TestRegions = TestRegions)

    QT_results.append(('{}'.format(recname), results))
    # Lead II
    results = classifier.testing_API(sig['sig2'],
            rfmdl = trained_model,
            saveresultfolder = result_folder,
            TestRegions = TestRegions)
    QT_results.append(('{}_sig2'.format(recname), results))

    # Save Prediction Result
    if result_folder is not None:
        # save results
        saveresult_filename = os.path.join(result_folder,'result_{}'.format(recname))
        with open(saveresult_filename, 'w') as fout:
            json.dump(QT_results,fout,indent = 4,sort_keys = True)
            print 'saved prediction result to %s' % (saveresult_filename)

if __name__ == '__main__':
    pass
