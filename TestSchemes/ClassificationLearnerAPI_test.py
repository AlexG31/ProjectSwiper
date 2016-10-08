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
# from RFclassifier.ParallelRfClassifier import ParallelRfClassifier as ECGrf
from RFclassifier.ClassificationLearner_API import ECGrf
from RFclassifier.ClassificationLearner import timing_for
from QTdata.loadQTdata import QTloader 
from RunAndTime import RunAndTime


def backup_configure_file(saveresultpath):
    shutil.copy(os.path.join(projhomepath,'ECGconf.json'),saveresultpath)
def backupobj(obj,savefilename):
    with open(savefilename,'wb') as fout:
        pickle.dump(obj,fout)


def TestRecord(saveresultpath):
    '''Test all records in testinglist, training on remaining records in QTdb.'''
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    # Get training record list
    testinglist = QTreclist[0:10]
    # traininglist = QTreclist[0:10]

    # debug
    # traininglist = QTreclist[0:10]
    # testinglist = QTreclist[0:10]
    # log.warning('Using custom testing & training records.')
    # log.warning('Training range: 0-10')
    # log.warning('Testing range: 0-10')

    rf_classifier = ECGrf(SaveTrainingSampleFolder = saveresultpath)
    # Multi Process
    rf_classifier.TestRange = 'All'

    # Load classification model.
    with open(os.path.join(saveresultpath, 'trained_model.mdl'), 'rb') as fin:
        trained_model = pickle.load(fin)
        rf_classifier.mdl = trained_model

    # testing
    log.info('Testing records:\n    %s',', '.join(testinglist))
    for record_name in testinglist:
        sig = qt_loader.load(record_name)
        raw_signal = sig['sig']
        result = rf_classifier.testing(raw_signal, trained_model)
        with open(os.path.join(saveresultpath, 'result_{}'.format(record_name)),'w') as fout:
            json.dump(result,fout,indent = 4)

if __name__ == '__main__':

    saveresultpath = os.path.join(projhomepath, 'result', 'test-api')
    log.info('Save result path is: %s', saveresultpath)

    # create result folder if not exist
    # if os.path.exists(saveresultpath) == True:
        # option = raw_input('Result path "{}" already exists, remove it?'.format(saveresultpath))
        # if option in ['y','Y']:
            # shutil.rmtree(saveresultpath)
            # os.mkdir(saveresultpath)

    TestRecord(saveresultpath)
