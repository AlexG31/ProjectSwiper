#encoding:utf-8
"""
Start Date: 2016.10.8
ECG Regression Test
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
            '%s.log' % datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')),
        format = (
            '%(asctime)-15s[%(levelname)s]%(filename)s:%(lineno)d,'
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
# from RFclassifier.ParallelRfClassifier import ParallelRfClassifier as ECGrf
from RFclassifier.RegressionLearner import RegressionLearner as ECGrf
from RFclassifier.ClassificationLearner import timing_for
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime


def backup_configure_file(save_result_path):
    shutil.copy(os.path.join(projhomepath,'ECGconf.json'),save_result_path)
def backupobj(obj,savefilename):
    with open(savefilename,'wb') as fout:
        pickle.dump(obj,fout)


def Round_Test(
        saveresultpath,
        RoundNumber = 1,
        number_of_test_record_per_round = 30,
        round_start_index = 1,
        target_label = 'T'):
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
        round_folder = os.path.join(saveresultpath,'round{}'.format(round_ind))
        os.mkdir(round_folder)
        # Randomly select test records.
        test_ind_list = random.sample(xrange(0,N_may_test),number_of_test_record_per_round)
        testlist = map(lambda x:may_testlist[x],test_ind_list)
        # Run the test warpper.
        TestAllQTdata(round_folder,testlist,target_label = target_label)

def TestAllQTdata(save_result_path, testinglist, training_list = None, target_label = 'T'):
    '''Test Regression Learner with QTdb.'''
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    # Get training record list
    if training_list is None:
        training_list = list(set(QTreclist) - set(testinglist))

    # debug
    # training_list = QTreclist[0:10]
    # testinglist = QTreclist[0:10]
    # log.warning('Using custom testing & training records.')
    # log.warning('Training range: 0-10')
    # log.warning('Testing range: 0-10')

    log.info('Totoal QTdb record number:%d, training %d, testing %d',
            len(QTreclist),
            len(training_list),
            len(testinglist))

    rf_classifier = ECGrf(
            TargetLabel = target_label,
            SaveTrainingSampleFolder = save_result_path)
    # Multi Process
    rf_classifier.TestRange = 'All'

    # Training
    # ====================
    log.info('Start training...')
    print 'training...'

    # training the rf_classifier classifier with reclist
    time_cost_output = []
    timing_for(rf_classifier.TrainQtRecords,[training_list,],prompt = 'Total Training time:',time_cost_output = time_cost_output)
    log.info('Total training time cost: %.2f seconds', time_cost_output[-1])
    # save trained mdl
    backupobj(rf_classifier.mdl,os.path.join(save_result_path,'trained_model.mdl'))

    # testing
    log.info('Testing records:\n    %s',', '.join(testinglist))
    rf_classifier.TestQtRecords(save_result_path,reclist = testinglist)


    
def TEST1(save_result_path, target_label = 'T'):
    qt_loader = QTloader()
    qt_record_list= qt_loader.getQTrecnamelist()

    # testing& training set
    training_list = qt_record_list[0:4]
    testing_list = qt_record_list[41:50]

    # Start traing & testing
    TestAllQTdata(save_result_path, testing_list, training_list, target_label = target_label)

if __name__ == '__main__':

    # Get save_result_path from config file.
    save_result_path = os.path.join(projhomepath,
            'result',
            'regression-test4')
    target_label = 'T'
    number_of_rounds = 100

    # logging
    logging.basicConfig(
        filename = os.path.join(save_result_path, 'log.txt'))
    log = logging.getLogger()
    log.info('Save result to: %s', save_result_path)

    # create result folder if not exist
    if os.path.exists(save_result_path) == True:
        option = raw_input(
                'Result path "{}" already exists, remove it(y/n)?'.format(save_result_path))
        if option in ['y','Y']:
            shutil.rmtree(save_result_path)
            os.mkdir(save_result_path)
    else:
        os.mkdir(save_result_path)

    # Refresh randomly selected features json file and backup it.
    random_relation_file_path = os.path.join(save_result_path,'rand_relations.json')
    RandomRelation.refresh_project_random_relations_computeLen(
            copyTo = random_relation_file_path)

    # logging
    log.info('Copied random relation file to %s', random_relation_file_path)

    # Backup configuration file.
    backup_configure_file(save_result_path)

    # Customized testing
    # TEST1(save_result_path, target_label = target_label)
    Round_Test(save_result_path,
            RoundNumber = number_of_rounds,
            round_start_index = 1,
            target_label = target_label)
