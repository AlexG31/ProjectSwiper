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

## Main Scripts
# ==========
EPS = 1e-6

def Testing(raw_signal, model_path):
    '''Testing API.'''
    saveresultpath = model_path
    rf_classifier = ECGrf(SaveTrainingSampleFolder = saveresultpath)
    # Multi Process
    rf_classifier.TestRange = 'All'

    # Load classification model.
    with open(os.path.join(saveresultpath, 'trained_model.mdl'), 'rb') as fin:
        trained_model = pickle.load(fin)
        rf_classifier.mdl = trained_model

    result = rf_classifier.testing(raw_signal, trained_model)
    with open(os.path.join(saveresultpath, 'test_result_cc'),'w') as fout:
        json.dump(result,fout,indent = 4)
    return result

def show_drawing(folderpath = os.path.join(\
        os.path.dirname(curfilepath),'..','QTdata','QTdata_repo')):
    with open(os.path.join(folderpath,'sel103.txt'),'r') as fin:
        sig = pickle.load(fin)
    # sig with 'sig','time'and 'marks'
    ECGfv = extfeature.ECGfeatures(sig['sig'])
    fv = ECGfv.frompos(3e3)

def valid_signal_value(sig):
    # check Nan!
    # check Inf!
    float_inf = float('Inf')
    float_nan = float('Nan')
    if float_inf in sig or float_nan in sig:
        return False
    return True
def timing_for(function_handle,params,prompt = 'timing is',time_cost_output = None):
    time0 = time.time()
    ret = function_handle(*params)
    time1 = time.time()
    info_str = '{} [time cost {} s]'.format(prompt,time1-time0)
    print info_str
    # output
    if time_cost_output is not None and isinstance(time_cost_output,list):
        time_cost_output.append(time1-time0) 
    # return value
    return ret

class ECGrf(object):
    '''This class only intended to export the testing function.'''    
    def __init__(self,MAX_PARA_CORE = 6,SaveTrainingSampleFolder = None):
        # only test on areas with expert labels
        self.TestRange = 'Partial'# or 'All'
        # Parallel
        self.QTloader = QTdb.QTloader()
        self.mdl = None
        self.MAX_PARA_CORE = MAX_PARA_CORE
        # maximum samples for bucket testing
        self.MaxTestSample = 200
        # Save training samples folder.
        if SaveTrainingSampleFolder is None:
            ResultFolder = projhomepath
            ResultFolder_conf = conf['ResultFolder_Relative']
            for folder in ResultFolder_conf:
                ResultFolder = os.path.join(ResultFolder,folder)
            self.SaveTrainingSampleFolder = ResultFolder
        else:
            self.SaveTrainingSampleFolder = SaveTrainingSampleFolder
    @ staticmethod
    def RefreshRandomFeatureJsonFile(copyTo = None):
        # refresh random relations
        RandRelation.refresh_project_random_relations_computeLen(copyTo = copyTo)


    @staticmethod
    def collectfeaturesforsig(raw_signal, expert_labels,
            blankrangelist = None,recID = None):
        '''Label process & convert to feature.'''
        #
        # parameters:
        # blankrangelist : [[l,r],...]
        #
        # collect training features from raw_signal
        feature_extractor = extfeature.ECGfeatures(raw_signal)
        negposlist = []
        posposlist = [] # positive position list
        labellist = [] # positive label list
        tarpos = []
        # Including positive samples & negtive samples.
        trainingX,trainingy = [],[]
        # get Expert labels
        QTloader = QTdb.QTloader()
        # =======================================================
        # modified negposlist inside function
        # =======================================================
        posposlist,labellist = zip(*expert_labels)

        # ===============================
        # convert feature & append to X,y
        # Using Map build in function
        # ===============================
        FV = map(feature_extractor.frompos,posposlist)
        # append to trainging vector
        trainingX.extend(FV)
        trainingy.extend(labellist)
        
        # add neg samples
        Nneg = int(len(negposlist)*conf['negsampleratio'])
        #print 'Total number of negposlist =',len(negposlist)
        #print '-- Number of Training samples -- '
        #print 'Num of pos samples:',len(trainingX)
        #print 'Num of neg samples:',Nneg

        # If Number of Neg>0 then add negtive samples.
        if len(negposlist) == 0 or Nneg <= 0:
            print '[In function collect feature] Warning: negtive sample position list length is 0.'
        else:
            # collect negtive sample features
            #
            # leave blank for area without labels
            #
            negposset = set(negposlist)
            if blankrangelist is not None:
                blklist = []
                for pair in blankrangelist:
                    blklist.extend(range(pair[0],pair[1]+1))
                blkset = set(blklist)
                negposset -= blkset
                
            selnegposlist = random.sample(negposset,Nneg)
            time_neg0 = time.time()
            negFv = map(feature_extractor.frompos,selnegposlist)
            trainingX.extend(negFv)
            trainingy.extend(['white']*Nneg)
            print '\nTime for collect negtive samples:{:.2f}s'.format(time.time() - time_neg0)
        return (trainingX,trainingy) 
        
    def CollectRecFeature(self,recname):
        log.info('Collecting feature for %s', recname)

        # Load signal.
        QTloader = QTdb.QTloader()
        sig = QTloader.load(recname)
        expert_labels = QTloader.getExpert(recname)
        if valid_signal_value(sig['sig']) == False:
            return [[],[]]
        tX,ty = ECGrf.collectfeaturesforsig(sig['sig'],blankrangelist = None)
        return (tX,ty)

    def TrainQtRecords(self,reclist):
        '''Warpper for model training on QTdb.'''
        # Multi Process
        #pool = Pool(self.MAX_PARA_CORE)
        pool = Pool(2)

        training_samples, training_labels = [], []
        # single core:
        trainingTuples = timing_for(map,[self.CollectRecFeature,reclist],prompt = 'All records collect feature time')
        # close pool
        pool.close()
        pool.join()
        # organize features
        tXlist,tylist = zip(*trainingTuples)

        # tylist is a list of training_labels for each record,
        # similar is for tXlist
        map(training_samples.extend, tXlist)
        map(training_labels.extend, tylist)

        # train Random Forest Classifier
        Tree_Max_Depth = conf['Tree_Max_Depth']
        RF_TreeNumber = conf['RF_TreeNumber']
        rfclassifier = RandomForestClassifier(n_estimators = RF_TreeNumber,max_depth = Tree_Max_Depth,n_jobs =4,warm_start = False)
        log.info('Random Forest Training Sample Size : [%d samples * %d features]',len(training_samples),len(training_samples[0]))
        timing_for(rfclassifier.fit,(training_samples,training_labels),prompt = 'Random Forest Fitting')
        # save&return classifier model
        self.mdl = rfclassifier
        return rfclassifier
    
    def testing(self, raw_signal, rfmdl = None):
        '''Testing ECG record with trained model.'''
        # default parameters
        if rfmdl is None:
            rfmdl = self.mdl

        PrdRes = []
        if valid_signal_value(raw_signal) == False:
            raise Exception('Input signal value is not valid!(may contain inf)')
        feature_extractor = extfeature.ECGfeatures(raw_signal)
        N_signal = len(raw_signal)

        # Testing...
        record_predict_result = self.testing_with_extractor(rfmdl,
                N_signal, feature_extractor)

        PrdRes = record_predict_result
        return PrdRes

    def testing_with_extractor(self, rfmdl, signal_length, feature_extractor):
        ''' Testing a feature vector from feature_extractor in test_range.'''

        # Leaving testing Blank Regions in Head&Tail of the tested signal,
        # to avoid feature insufficiency.
        WindowLen = conf['winlen_ratio_to_fs']*conf['fs']
        Blank_Len = WindowLen/2+1
        # Test samples position list.
        # prRange = range(Blank_Len, signal_length - 1 - Blank_Len)
        prRange = range(0,1000)
        
        return self.test_with_positionlist(
                    rfmdl,
                    prRange,
                    feature_extractor 
                )
    def test_with_positionlist(self,rfmdl,poslist,featureextractor):
        # test with buckets
        # 
        # Prediction Result
        # [(pos,label)...]
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
            res = rfmdl.predict(samples_tobe_tested)
            mean_proba = rfmdl.predict_proba(samples_tobe_tested)
            label_proba_vec = map(lambda x:x[1][dict_class2index[x[0]]],zip(res,mean_proba))
            # debug
            #print 'probability shape:',mean_proba.shape
            #print 'array of classes:',rfmdl.classes_
            ### sample to make sure
            #n_debug = 30
            #print 'predict label & its proba:',zip(res,label_proba_vec)[0:n_debug]
            #pdb.set_trace()
            PrdRes.extend(res.tolist())
            PrdProba.extend(label_proba_vec)
            
            
        if len(PrdRes) != len(poslist):
            print 'len(prd Results) = ',len(PrdRes),'Len(poslist) = ',len(poslist)
            print 'PrdRes:'
            print PrdRes
            print 'poslist:'
            print poslist
            pdb.set_trace()
            raise StandardError('test Error: output label length doesn''t match!')
        return zip(poslist,PrdRes,PrdProba)

    def plotresult(\
            self,\
            prdResult_rec,\
            figureID = 1,\
            showExpertLabel = False):
#
        # parameter check
        if len(prdResult_rec)!=2:
            raise StandardError('\
                    input prdRes must be of form\
                    (recname,recResult)!')
        ## plot signal waveform & labels
        recname,recRes = prdResult_rec

        plt.figure(figureID);
        sig = self.QTloader.load(recname)
        rawsig = sig['sig']
        # plot sig 
        plt.plot(rawsig)
        # plot prd indexes
        #raw_input('input sth...')
        for prdpair in recRes:
            label = prdpair[1]
            pos = prdpair[0]
            mker = 'kh'

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
            plt.plot(pos,rawsig[pos],mker)
        # plot expert marks
        if showExpertLabel:
            # blend together
            explbpos = self.QTloader.getexpertlabeltuple(recname)
            explbpos = [x[0] for x in explbpos]
            explbAmp = [rawsig[x] for x in explbpos]
            # plot expert labels
            h_expertlabel = plt.plot(\
                    explbpos,explbAmp,'rx')
            # set plot properties
            plt.setp(h_expertlabel,'ms',12)

        plt.title(recname)
        #plt.xlim((145200,151200))
        plt.show()

    def plot_testing_result(self,RecResults,figureID = 1):
        for recname,recRes in RecResults:
            print recRes
            raw_input('recRes...')
            #recname = rec

            plt.figure(figureID);
            sig = self.QTloader.load(recname)
            rawsig = sig['sig']
            # plot sig 
            plt.plot(rawsig)
            # plot prd indexes
            #raw_input('input sth...')
            for prdpair in recRes:
                label = prdpair[1]
                pos = prdpair[0]
                mker = 'kh'

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
                plt.plot(pos,rawsig[pos],mker)
            plt.title(recname)
            #plt.xlim((145200,151200))
            plt.show()
        
    def testmdl(\
                self,\
                reclist = ['sel103',],\
                mdl = None,\
                TestResultFileName = None\
            ):
        # default parameter
        if mdl is None:
            mdl = self.mdl

        # testing
        RecResults = self.testing(reclist)
        #
        # save to model file 
        if TestResultFileName is not None:
            filename_saveresult = TestResultFileName
        else:
            filename_saveresult = os.path.join(\
                    curfolderpath,\
                    'testresult{}.out'.format(\
                    int(time.time())))

            # warning :save to default folder
            print '**Warning: save result to {}'.format(filename_saveresult)
            log.info('Saving result to %s', filename_saveresult)

        with open(filename_saveresult,'w') as fout:
            pickle.dump(RecResults ,fout)
            print 'saved prediction result to {}'.\
                    format(filename_saveresult)
    def TestQtRecords(self,saveresultfolder,
            reclist = ['sel103',],mdl = None,TestResultFileName = None):
        '''Test Qt records with trainied model.'''
        # default parameter
        if mdl is None:
            mdl = self.mdl
        #saveresultfolder = os.path.dirname(filename_saveresult)
        for recname in reclist:
            # testing
            RecResults = self.testing([recname,],saveresultfolder = saveresultfolder)
        


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
    tX,ty = ECGrf.collectfeaturesforsig(sig,SaveTrainingSampleFolder,blankrangelist = blklist,recID = recname)
    return (tX,ty)
    

if __name__ == '__main__':
    Testing([2.2,]*1000)
