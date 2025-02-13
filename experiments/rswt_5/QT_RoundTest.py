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
projhomepath = os.path.dirname(curfolderpath)
if os.path.split(projhomepath)[-1] != 'ProjectSwiper':
    raise Exception(
            'Project home path is not correct!\n'
            ' current: %s' % projhomepath)
# Configuration file
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
from RFclassifier.ParallelRfClassifier import ParallelRfClassifier as ECGrf
from RFclassifier.ClassificationLearner import timing_for
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime


def backup_configure_file(saveresultpath):
    shutil.copy(
            os.path.join(projhomepath,'ECGconf.json'),
            saveresultpath)
def backupobj(obj,savefilename):
    with open(savefilename,'wb') as fout:
        pickle.dump(obj,fout)

def Round_Test(
        saveresultpath,
        RoundNumber = 1,
        number_of_test_record_per_round = 30,
        round_start_index = 1):
    '''Randomly select records from QTdb to test.
        Args:
            RoundNumber: Rounds to repeatedly select records form QTdb & test.
            number_of_test_record_per_round: Number of test records to randomly
            select per round.
    '''
    
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()

    # To randomly select 30 records from may_testlist
    may_testlist = QTreclist
    # Remove records that must be in the training set
    must_train_list = [
        "sel35", 
        "sel36", 
        "sel31", 
        "sel38", 
        "sel39", 
        "sel820", 
        "sel51", 
        "sele0104", 
        "sele0107", 
        "sel223", 
        "sele0607", 
        "sel102", 
        "sele0409", 
        "sel41", 
        "sel40", 
        "sel43", 
        "sel42", 
        "sel45", 
        "sel48", 
        "sele0133", 
        "sele0116", 
        "sel14172", 
        "sele0111", 
        "sel213", 
        "sel14157", 
        "sel301"
            ]
    may_testlist = list(set(may_testlist) - set(must_train_list))
    N_may_test = len(may_testlist)
    
    # Start testing.
    log.info('Start Round Testing...')
    for round_ind in xrange(round_start_index, RoundNumber+1):
        # Generate round folder.
        round_folder = os.path.join(saveresultpath, 'round{}'.format(round_ind))
        os.mkdir(round_folder)
        # Randomly select test records.
        test_ind_list = random.sample(xrange(0,N_may_test),number_of_test_record_per_round)
        testlist = map(lambda x:may_testlist[x], test_ind_list)
        # Run the test warpper.
        TestAllQTdata(round_folder, testlist, round_ind)

def TestAllQTdata(saveresultpath, testinglist, round_ind):
    '''Test all records in testinglist, training on remaining records in QTdb.'''
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    # Get training record list
    traininglist = list(set(QTreclist) - set(testinglist))

    # debug
    # traininglist = QTreclist[0:10]
    # testinglist = QTreclist[0:10]
    # log.warning('Using custom testing & training records.')
    # log.warning('Training range: 0-10')
    # log.warning('Testing range: 0-10')

    log.info('Totoal QTdb record number:%d, training %d, testing %d',
            len(QTreclist), len(traininglist), len(testinglist))

    rf_classifier = ECGrf(SaveTrainingSampleFolder = saveresultpath)
    # Multi Process
    rf_classifier.TestRange = 'All'

    # Training
    time_cost_output = []
    timing_for(rf_classifier.TrainQtRecords,
            [traininglist,],
            prompt = 'Total Training time:',
            time_cost_output = time_cost_output)
    log.info('Total training time cost: %.2f seconds', time_cost_output[-1])
    # Save trained mdl
    backupobj(rf_classifier.mdl,os.path.join(saveresultpath,'trained_model.mdl'))

    # testing
    log.info('Testing records:\n    %s',', '.join(testinglist))
    rf_classifier.TestQtRecords(saveresultpath,reclist = testinglist)

    
if __name__ == '__main__':

    # Debug
    number_of_test_record_per_round = 30

    saveresultpath = projhomepath
    Result_path_conf = conf['ResultFolder_Relative']
    for folder in Result_path_conf:
        saveresultpath = os.path.join(saveresultpath,folder)
    log.info('Save result path is: %s', saveresultpath)

    # create result folder if not exist
    if os.path.exists(saveresultpath) == True:
        option = raw_input(
                'Result path "%s" already exists, remove it?(y/n)' % saveresultpath)
        if option in ['y', 'Y']:
            shutil.rmtree(saveresultpath)
            os.mkdir(saveresultpath)
    else:
        os.mkdir(saveresultpath)
    # Refresh randomly selected features json file and backup it.
    random_relation_file_path = os.path.join(saveresultpath, 'rand_relations.json')
    RandomRelation.RefreshRswtPairs(random_relation_file_path)

    #backup configuration file
    backup_configure_file(saveresultpath)

    Round_Test(saveresultpath,
            number_of_test_record_per_round = number_of_test_record_per_round,
            RoundNumber = 30,
            round_start_index = 1)
