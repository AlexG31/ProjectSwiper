#encoding:utf-8
"""
ECG classification Module
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import datetime
import math
import pickle
import logging
import random
import time
import shutil
import numpy as np
import pdb
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# Get current file path & project homepath.
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
curfolderpath = os.path.dirname(curfolderpath)
projhomepath = curfolderpath;
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
# Logging config.
logging.basicConfig(
        filename = os.path.join(
            projhomepath,
            'logs',
            '%s.log'%datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')),
        format = ('%(asctime)-15s[%(levelname)s]%(filename)s:%(lineno)d,'
            ' in function:%(funcName)s\n    %(message)s'),
        level = 10
        )
# Logging
log = logging.getLogger()

# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import RFclassifier.extractfeature.randomrelations as RandomRelation
import QTdata.loadQTdata as QTdb
import RFclassifier.evaluation as ecgEval
import RFclassifier.ECGRF as ECGRF 
from RFclassifier.ECGRF import timing_for
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime


def TestingAndSaveResult():
    sel1213 = conf['sel1213']
    time0 = time.time()
    rf = ECGRF.ECGrf()
    rf.training(sel1213[0:1])
    time1 = time.time()
    print 'Training time:',time1-time0
    ## test
    rf.testmdl(reclist = sel1213[0:1])
def backup_configure_file(saveresultpath):
    shutil.copy(os.path.join(projhomepath,'ECGconf.json'),saveresultpath)
def backupobj(obj,savefilename):
    with open(savefilename,'wb') as fout:
        pickle.dump(obj,fout)

def Round_Test(saveresultpath,RoundNumber = 100,number_of_test_record_per_round = 30):
    '''Randomly select records from QTdb to test.
        Args:
            RoundNumber: Rounds to repeatedly select records form QTdb & test.
            number_of_test_record_per_round: Number of test records to randomly select per round.
    '''
    
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()

    # To randomly select 30 records from may_testlist
    may_testlist = QTreclist
    N_may_test = len(may_testlist)
    
    # Start testing.
    log.info('Start Round Testing...')
    for round_ind in xrange(1,RoundNumber+1):
        log.info('Test round %d', round_ind)
        return
        round_folder = os.path.join(saveresultpath,'Round{}'.format(round_ind))
        os.mkdir(round_folder)
        test_ind_list = random.sample(xrange(0,N_may_test),number_of_test_record_per_round)
        testlist = map(lambda x:may_testlist[x],test_ind_list)
        TestAllQTdata(round_folder,testlist)



def TestAllQTdata(saveresultpath,testinglist):
    '''Test all records in testinglist, training on remaining records in QTdb.'''
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    print 'Totoal QT record number:{}'.format(len(QTreclist))
    ## Training record list
    #testinglist = conf["selQTall0_test_set"]
    traininglist = list(set(QTreclist) - set(testinglist))

    rf = ECGRF.ECGrf(SaveTrainingSampleFolder = saveresultpath)
    # Multi Process
    rf.TestRange = 'All'

    # clear debug logger
    ECGRF.debugLogger.clear()
    # ====================
    # Training
    # ====================
    ECGRF.debugLogger.dump('\n====Test Start ====\n')

    # training the rf classifier with reclist
    #
    # dump to debug logger
    time_cost_output = []
    timing_for(rf.training,[traininglist,],prompt = 'Total Training time:',time_cost_output = time_cost_output)
    ECGRF.debugLogger.dump('Total Training time: {:.2f} s\n'.format(time_cost_output[-1]))
    # save trained mdl
    backupobj(rf.mdl,os.path.join(saveresultpath,'trained_model.mdl'))

    ## test
    print '\n>>Testing:',testinglist
    ECGRF.debugLogger.dump('\n======\n\nTest Set :{}'.format(testinglist))
    rf.testrecords(saveresultpath,reclist = testinglist)


    
if __name__ == '__main__':

    saveresultpath = projhomepath
    Result_path_conf = conf['ResultFolder_Relative']
    for folder in Result_path_conf:
        saveresultpath = os.path.join(saveresultpath,folder)
    log.info('Save result path is: %s', saveresultpath)

    # create result folder if not exist
    if os.path.exists(saveresultpath) == False:
        os.mkdir(saveresultpath)
    # Refresh randomly selected features json file and backup it.
    random_relation_file_path = os.path.join(saveresultpath,'rand_relations.json')
    RandomRelation.refresh_project_random_relations_computeLen(copyTo = random_relation_file_path)
    log.info('Copied random relation file to %s', random_relation_file_path)

    #backup configuration file
    backup_configure_file(saveresultpath)

    Round_Test(saveresultpath)
