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
# my project components
import extractfeature.extractfeature as extfeature
import extractfeature.randomrelations as RandRelation
import WTdenoise.wtdenoise as wtdenoise
import QTdata.loadQTdata as QTdb

## Main Scripts
# ==========
EPS = 1e-6
tmpmdlfilename = os.path.join(projhomepath,'tmpmdl.txt')

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

# train and test
class ECGrf:
    def __init__(self,MAX_PARA_CORE = 6):
        # only test on areas with expert labels
        self.TestRange = 'Partial'# or 'All'
        # Parallel
        self.useParallelTest = True
        self.QTloader = QTdb.QTloader()
        self.mdl = None
        self.MAX_PARA_CORE = MAX_PARA_CORE
        # maximum samples for bucket testing
        self.MaxTestSample = 200
    @ staticmethod
    def RefreshRandomFeatureJsonFile():
        # refresh random relations
        RandRelation.refresh_project_random_relations()


    # label proc & convert to feature
    @staticmethod
    def collectfeaturesforsig(\
                sig,\
                blankrangelist = None,\
            ):
        #
        # parameters:
        # blankrangelist : [[l,r],...]
        #
        # collect training features from sig
        #
        # init
        Extractor = extfeature.ECGfeatures(sig['sig'])
        negposlist = []
        posposlist = [] # positive position list
        labellist = [] # positive label list
        tarpos = []
        trainingX,trainingy = [],[]
        # get Expert labels
        QTloader = QTdb.QTloader()
        # =======================================================
        # modified negposlist inside function
        # =======================================================
        ExpertLabels = QTloader.getexpertlabeltuple(None,sigIN = sig,negposlist = negposlist)

        posposlist,labellist = zip(*ExpertLabels)

        # ===============================
        # convert feature & append to X,y
        # Using Map build in function
        # ===============================
        FV = map(Extractor.frompos,posposlist)
        # append to trainging vector
        trainingX.extend(FV)
        trainingy.extend(labellist)
        
        # add neg samples
        Nneg = int(len(negposlist)*conf['negsampleratio'])
        print 'Total number of negposlist =',len(negposlist)
        print '-- Number of Training samples -- '
        print 'Num of pos samples:',len(trainingX)
        print 'Num of neg samples:',Nneg

        if len(negposlist) == 0:
            print '[In function collect feature]\
                    Warning: negtive sample position list length is 0.'
            return 
        # collect negtive sample features
        #
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
        negFv = map(Extractor.frompos,selnegposlist)
        trainingX.extend(negFv)
        trainingy.extend(['white']*Nneg)
        print '\nTime for collect negtive samples:{:.2f}s'.format(time.time() - time_neg0)
        return (trainingX,trainingy) 
        
    def training(self,reclist):
        # training feature vector
        trainingX = []
        trainingy = []

        # Parallel
        # Multi Process
        pool = Pool(self.MAX_PARA_CORE)
        # train with reclist
        # map function (recname) -> (tx,ty)
        time_training0 = time.time()
        trainingTuples = pool.map(Parallel_CollectRecFeature,reclist)
        time_training1 = time.time()
        print 'All records collect feature time {:.2f}'.format(time_training1 - time_training0)
        # close pool
        pool.close()
        pool.join()
        # organize features
        tXlist,tylist = zip(*trainingTuples)
        map(trainingX.extend,tXlist)
        map(trainingy.extend,tylist)


        time_training0 = time.time()
        # train Random Forest Classifier
        rfclassifier = RandomForestClassifier(n_estimators = 30)
        print '正在训练随机森林分类器'.decode('utf-8')
        print 'Training Sample Size : [{} x {}]'.format(len(trainingX),len(trainingX[0]))
        rfclassifier.fit(trainingX,trainingy)
        print '训练结束'.decode('utf-8')
        time_training1 = time.time()
        print 'All records Trainging Classifier time {:.2f}s'.format(time_training1 - time_training0)

        # save&return classifier model
        self.mdl = rfclassifier
        return rfclassifier

    
    def test_signal(self,signal,rfmdl = None,MultiProcess = 'off'):
        # test rawsignal
        if rfmdl is None:
            rfmdl = self.mdl
        if MultiProcess == 'off':
            FeatureExtractor = extfeature.ECGfeatures(signal)
        else:
            raise StandardError('MultiProcess on is not defined yet!')
        if MultiProcess == 'on':
            raise StandardError('MultiProcess on is not defined yet!')
        elif MultiProcess == 'off':
            record_predict_result = self.test_with_positionlist(rfmdl,range(0,len(signal)),FeatureExtractor)
        return record_predict_result

    # testing ECG record with trained mdl
    def testing(\
            self,\
            reclist,\
            rfmdl = None,\
            MultiProcess = 'on',\
            plot_result = 'off'):
        #
        # default parameter
        #
        if rfmdl is None:
            rfmdl = self.mdl

        # Parallel 
        if self.useParallelTest == True:
            MultiProcess = 'on'
        else:
            MultiProcess = 'off'

        # test all files in reclist
        PrdRes = []
        for recname in reclist:
            # start testing time
            time_rec0 = time.time()
            # QT sig data
            sig = self.QTloader.load(recname)
            # valid signal value:
            if valid_signal_value(sig['sig']) == False:
                continue
            # sigle process
            if MultiProcess == 'off':
                FeatureExtractor = extfeature.ECGfeatures(sig['sig'])

            # original rawsig
            rawsig = sig['sig']
            N_signal = len(rawsig)

            # denoise signal
            #
            if MultiProcess == 'on':
                feature_type = conf['feature_type']
                if feature_type == 'wavelet':
                    denoisesig = rawsig
                else:
                    denoisesig = wtdenoise.denoise(rawsig)
                    denoisesig = denoisesig.tolist()
                    N_signal = len(denoisesig)
            
            # init
            prRes = []
            testSamples = []

            #
            # get prRange:
            # testing in the same range as expert labels
            #
            expres = self.QTloader.\
                    getexpertlabeltuple(recname)

            if self.TestRange == 'All':
                WindowLen = conf['winlen_ratio_to_fs']*conf['fs']
                Blank_Len = WindowLen/2+1
                prRange = range(Blank_Len,N_signal - 1-Blank_Len)
            else:
                #
                # expand a little bit outside of the original expert's label range
                #
                test_expand_width = 20
                prRangeLb = min([x[0] for x in expres])-test_expand_width
                prRangeRb = max([x[0] for x in expres])+test_expand_width+1
                prRangeLb = max(0,prRangeLb)
                prRangeRb = min(N_signal - 1,prRangeRb)
                prRange = range(prRangeLb,prRangeRb)
            
            
            debugLogger.dump(\
                    'Testing samples with lenth {}\n'.\
                    format(len(prRange)))
            #
            # pickle dumple modle to file for multi process testing
            #
            with open(tmpmdlfilename,'w') as fout:
                pickle.dump(rfmdl,fout)
            if MultiProcess == 'on':
                record_predict_result = self.\
                        test_with_positionlist_multiprocess(\
                            rfmdl,\
                            prRange,\
                            denoisesig,\
                            origrawsig = rawsig
                        )
            elif MultiProcess == 'off':
                record_predict_result = self.\
                        test_with_positionlist(\
                            rfmdl,\
                            prRange,\
                            FeatureExtractor\
                        )

            #
            # prediction result for each record            
            #
            PrdRes.append((recname,record_predict_result))
            
            # end testing time
            time_rec1 = time.time()
            print 'Testing time for {} is {:.2f} s'.\
                    format(recname,time_rec1-time_rec0)
            debugLogger.dump(\
            'Testing time for {} is {:.2f} s\n'.\
                    format(recname,time_rec1-time_rec0))

        return PrdRes

    def test_with_positionlist(self,rfmdl,poslist,featureextractor):
        # test with buckets
        # 
        # Prediction Result
        # [(pos,label)...]
        PrdRes = []

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
            bkt_L = i*Ntest + poslist[0]
            bkt_R = i*Ntest + Ntest + poslist[0]
            if poslist[-1]+1 < bkt_R:
                bkt_R = poslist[-1]+1
            samples_tobe_tested = map(featureextractor.frompos,range(bkt_L,bkt_R))
            # predict
            #
            res = rfmdl.predict(samples_tobe_tested)
            PrdRes.extend(res.tolist())
            
            
        if len(PrdRes) != len(poslist):
            raise StandardError('test Error: output label length doesn''t match!')
        return zip(poslist,PrdRes)

    def test_with_positionlist_multiprocess(\
            self,\
            rfmdl,\
            poslist,\
            denoisesig,\
            origrawsig
            ):

        # prompt
        print 'testing with multiprocess function'
        # init
        PrdRes = []
        #
        # testing & show progress
        # multi process speedup
        #
        # bucket size
        Ntest = self.MaxTestSample
        Lposlist = len(poslist)
        # compute number of buckets
        Nbuckets = Lposlist/Ntest
        if Nbuckets * Ntest < Lposlist:
            Nbuckets += 1
        # list for multi Map
        bktList = []
        for i in range(0,Nbuckets):
            # progress bar
            sys.stdout.write('\rTesting: {:02}buckets left.'.format(Nbuckets - i -1))
            sys.stdout.flush()

            bkt_L = i*Ntest + poslist[0]
            bkt_R = i*Ntest + Ntest + poslist[0]
            if poslist[-1]+1 < bkt_R:
                bkt_R = poslist[-1]+1
            bktList.append(\
                    range(bkt_L,bkt_R))
        #
        # multi process
        #
        # start multi process pool

        pool = Pool(self.MAX_PARA_CORE)
        # get global configuration file
        feature_type = conf['feature_type']
        if feature_type == 'wavelet':
            ResList = pool.map(Testing_with_ref_to_bucket,zip([denoisesig]*len(bktList),bktList))
        else:
            ResList = pool.map(Testing_with_ref_to_bucket,zip([origrawsig]*len(bktList),bktList))
        # close Pool obj
        pool.close()
        pool.join()
        # format the result
        for res in ResList:
            PrdRes.extend(res)
        
            
        # simple error check
        if len(PrdRes) != len(poslist):
            raise StandardError('test Error: output label length doesn''t match!')
        return zip(poslist,PrdRes)

    @staticmethod
    def Group_Horizon(recgroups):
        # only process onset&offset
        # recgroups:
        # [label,((pos,amplitude),...)]
        # =============================
        label,posGroupwithAmp = recgroups
        posGroupwithAmp.sort(key = lambda x:x[0])
        poslist,amplist = zip(*posGroupwithAmp)

        if 'onset' in label or 'offset' in label:
            pass
        else:
            return (label,poslist)
        # delete Pdel percent of maximum gradient
        Pdel = 0.2
        Ndel = int(Pdel*len(poslist))
        # don't do anything when len(Group) <= TH_low
        TH_low = 3
        # find the largest gradient
        if len(poslist) <= TH_low:
            return (label,poslist)
        # filter
        fposGroupwithAmp = posGroupwithAmp[:]
        for i in xrange(0,Ndel):
            # delete the one with largest grad
            gradlist = [abs(x[1][1]-x[0][1])/float(abs(x[1][0] - x[0][0])) for x in zip(fposGroupwithAmp,fposGroupwithAmp[1:])]
            mval,maxindex = max((val,ind) for ind,val in enumerate(gradlist))
            # delete point
            Pi0,Pi1 = maxindex,maxindex+1
            # =================================
            # delete edge point
            if Pi0 == 0:
                # delete Pi0
                del fposGroupwithAmp[Pi0:Pi0+1]
            elif Pi1 == len(fposGroupwithAmp) -1:
                del fposGroupwithAmp[Pi1:Pi1+1]
            else:
                # delete point with larger other grad
                if gradlist[maxindex-1]<gradlist[maxindex+1]:
                    del fposGroupwithAmp[Pi1:Pi1+1]
                else:
                    del fposGroupwithAmp[Pi0:Pi0+1]
        # Hoirzoned list
        fposlist,famplist = zip(*fposGroupwithAmp)
        return (label,fposlist)

        
        
    @staticmethod
    def result_refiner(Reslist):
        #
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        group_min_thres = 1
        QTloader = QTdb.QTloader()

        fRes = []
        for recname,recres in Reslist:
            sig = QTloader.load(recname)
            posgroup_withAmp = []
            # in var
            prev_label = None
            posGroup = []
            #----------------------
            # [pos,label] in recres
            #----------------------
            for pos,label in recres:
                if prev_label is not None:
                    if label != prev_label:
                        posgroup_withAmp.append((prev_label,posGroup))
                        posGroup = []
                    
                prev_label = label
                posGroup.append((pos,sig['sig'][pos]))
            
            # last one
            if len(posGroup)>0:
                posgroup_withAmp.append((prev_label,posGroup))
            # ======================
            # [(label,posGroup),...]
            # ======================
            posgroup_withAmp = [x for x in posgroup_withAmp if len(x[1]) > group_min_thres]
            # ----------------------
            # earth line algorithm
            # ----------------------
            fposGroup= map(ECGrf.Group_Horizon,posgroup_withAmp)

            # mean position 
            fposGroup = [(int(np.mean(x[1])),x[0]) for x in fposGroup ]
            fRes.append((recname,fposGroup ))
                
        return fRes

    # ====================================================
    # improved group method for near by prediction labels
    # ====================================================
    @staticmethod
    def resfilter_ver_steel(Reslist):
        Max_Gap_Dist = 3
        MinGroupSize = 2
        fReslist = []
        # Ground Filtering
        for recname,recres in Reslist:
            frecres = []
            # sort recres according to pos
            recres.sort(key = lambda x:x[0])
            poslist,labellist = zip(*recres)
            labelset = set(labellist)
            # get position list for each label
            LabelDict = {x:[] for x in labelset}
            LabelGroups= {x:[] for x in labelset}
            pos2labeldict = {pos:label for pos,label in recres}

            map(lambda x:LabelDict[x[1]].append(x[0]),recres)
            # sort 
            for label,labelposlist in LabelDict.iteritems():
                labelposlist.sort()

            # get labelgroups
            for label,labelposlist in LabelDict.iteritems():
                # get grad0
                difflist = [x[1] - x[0] for x in zip(labelposlist,labelposlist[1:])]
                # assert
                if min(difflist)<0:
                    raise StandardError('label list should be ascending!!')
                # if a non-white label is in the diff gap,then set diff value to Max_Gap_Dist + 1
                has_nonwhitelables_in_diffrange = map(lambda x:x[1] if len([pos for pos in range(labelposlist[x[0]]+1,labelposlist[x[0]+1]) if pos2labeldict[pos]!='white'])==0 else Max_Gap_Dist +1,enumerate(difflist))
                difflist = has_nonwhitelables_in_diffrange
                groups = [ind for ind,val in enumerate(difflist) if val > Max_Gap_Dist]
                groups.append(len(difflist))
                groups_start = [0]+groups

                # group number filter
                group_labelposindex = zip(groups_start,groups)
                group_labelposindex = [x for x in group_labelposindex if x[1] - x[0] >= MinGroupSize]

                # into group of positions
                map(lambda x :LabelGroups[label].append(labelposlist[x[0]:x[1]+1]),group_labelposindex)
                # group size filtering
                

            for label,labelgroupposlist in LabelGroups.iteritems():
                # collect filtered results
                map(lambda x:frecres.append((int(np.mean(x)),label)),labelgroupposlist)
            # got groups
            fReslist.append((recname,frecres))
                
        return fReslist

    @staticmethod
    def resfilter(Reslist):
        #
        # Multiple prediction point -> single point output
        ## filter output for evaluation results
        #
        # parameters
        #
        #
        # the number of the group must be greater than:
        #
        group_min_thres = 1

        fRes = []
        for recname,recres in Reslist:
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
            fRes.append((recname,frecres))
                
        return fRes

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
            debugLogger.dump('**Warning: save result to {}'.format(filename_saveresult))

        with open(filename_saveresult,'w') as fout:
            pickle.dump(RecResults ,fout)
            print 'saved prediction result to {}'.\
                    format(filename_saveresult)
        

# =======================
## debug Logger
# =======================
class debugLogger():
    def __init__(self):
        pass
    @staticmethod
    def dump(text):
        loggerpath = os.path.join(\
                projhomepath,\
                'classification_process.log')
        with open(loggerpath,'a') as fin:
            fin.write(text)
    @staticmethod
    def clear():
        loggerpath = os.path.join(\
                projhomepath,\
                'classification_process.log')
        fp = open(loggerpath,'w')
        fp.close()

##======================
# for multi process
##======================

def Testing_with_ref_to_bucket(Param):    
    #
    # for testing with multi process
    #
    # Params:
    # [test_sig,bkt_range]
    tested_signal,bkt_range = Param

    # Collect features
    samples_tobe_tested = map(extfeature.frompos_with_denoisedsig,zip([tested_signal]*len(bkt_range),bkt_range))
    #
    # test with RF classifier
    #
    # pickle load rfmdl file
    #
    with open(tmpmdlfilename,'r') as fin:
        rfmdl = pickle.load(fin)
    res = rfmdl.predict(samples_tobe_tested)
    return res

# ======================================
# Parallelly Collect training sample for each rec
# ======================================
def Parallel_CollectRecFeature(recname):
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
    tX,ty = ECGrf.collectfeaturesforsig(sig,blankrangelist = blklist)
    return (tX,ty)
    

if __name__ == '__main__':
    pass
