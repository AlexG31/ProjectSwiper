#encoding:utf-8
"""
Train a classification model for feature importance visualization.
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import math
import pickle
import random
import time
import shutil
import numpy as np
import pdb
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)

# Load configure file.
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
sys.path.append(curfolderpath)
#
# my project components
import RFclassifier.extractfeature.extractfeature as extfeature
import QTdata.loadQTdata as QTdb
import RFclassifier.evaluation as ecgEval
import ECG_RandomForest_trainer as ECGRF 
from RFclassifier.ECGRF import timing_for
from QTdata.loadQTdata import QTloader 


# Redirect stdout: reduce memory comsumption, allow larger feature dimension.
input_tmp = raw_input('redirect stdout?(y/n)')
if input_tmp == 'y':
    sys.stdout = open('test.txt','w')

# Function
def backup_configure_file(save_result_folder):
    shutil.copy(os.path.join(projhomepath,'ECGconf.json'),save_result_folder)
def backupobj(obj,savefilename):
    with open(savefilename,'w') as fout:
        pickle.dump(obj,fout)

def TrainModel(save_result_folder):
    '''Train a random forest model with QT records.''' 
    qt_loader = QTloader()
    QTreclist = qt_loader.getQTrecnamelist()
    training_record_list = QTreclist[0:15]
    # training
    Training(save_result_folder,training_record_list)


def Training(save_model_folder,training_record_list):
    '''Training with training_record_list.'''
    ## Training record list
    print
    print 'Totoal number of training list: {}'.format(len(training_record_list))

    rf = ECGRF.ECGrf(SaveTrainingSampleFolder = save_model_folder)
    # Training Target labels only.
    rf.training_target_labels = ['P']

    # Multi Process Testing
    rf.useParallelTest = True 
    rf.TestRange = 'All'

    # ====================
    # Training
    # ====================
    # clear debug logger
    ECGRF.debugLogger.clear()
    ECGRF.debugLogger.dump('\n====Test Start ====\n')

    time_cost_output = []
    timing_for(rf.training, [training_record_list,], 
            prompt = 'Total Training time:',time_cost_output = time_cost_output)
    ECGRF.debugLogger.dump('Total Training time: {:.2f} s\n'.format(
        time_cost_output[-1]))
    # save trained mdl
    backupobj(rf.mdl,os.path.join(save_model_folder,'tmp.mdl'))
    
def get_conf_save_result_folder():
    '''Get save result folder defined by conf.'''
    saveresultpath = projhomepath
    Result_path_conf = conf['ResultFolder_Relative']
    for folder in Result_path_conf:
        saveresultpath = os.path.join(saveresultpath,folder)
    return saveresultpath
if __name__ == '__main__':

    key_word = 'swarmp'
    save_result_folder = os.path.join(curfolderpath,'trained_model')

    # ------------
    # refresh random select feature json file and backup
    #ECGRF.ECGrf.RefreshRandomFeatureJsonFile(copyTo = os.path.join(
        #save_result_folder,'swarmp_random_pairs.json'))

    # Copy to result folder defined by conf.[for extract feature]
    shutil.copy(os.path.join(save_result_folder,'swarmp_random_pairs.json'),
            os.path.join(get_conf_save_result_folder(),'rand_relations.json'))
    # Training the random forest model.
    TrainModel(save_result_folder)
