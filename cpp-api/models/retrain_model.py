#encoding:utf-8
"""
ECG classification Module
Author : Phil G 
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


def TrainModel():
    '''Test all records in testinglist, training on remaining records in QTdb.'''
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    # Get training record list
    traininglist = QTreclist

    rf_classifier = ECGrf(SaveTrainingSampleFolder = None)
    # Multi Process
    rf_classifier.TestRange = 'All'

    # Training
    time_cost_output = []
    timing_for(rf_classifier.TrainQtRecords,
            [traininglist,],
            prompt = 'Total Training time:',
            time_cost_output = time_cost_output)
    print ('Total training time cost: %.2f seconds' % time_cost_output[-1])
    # save trained mdl
    backupobj(rf_classifier.mdl,os.path.join('.', 'trained_model.mdl'))

    
if __name__ == '__main__':

    number_of_test_record_per_round = 0

    # Refresh randomly selected features json file and backup it.
    random_relation_file_path = os.path.join('.', 'rand_relations.json')
    RandomRelation.RefreshRswtPairs(random_relation_file_path)

    # Training and saving model to file
    TrainModel()

