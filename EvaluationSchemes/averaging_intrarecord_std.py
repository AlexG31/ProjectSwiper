#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Date: 2016.10.10
ECG Grouping Evaluation module
Author : Gaopengfei

This file find the bad performance record, print its round number and record name.

1. This file tries to group the results as single outputs around the ground truth position.
2. This file computes the intra-record standard deviation with police object.
3. This file output stats in ms.
4. This file keep the smallest error between two leads.

"""

import os
import sys
import json
import glob
import string
import bisect
import math
import pickle
import shutil
import random
import time
import importlib
import pdb
import pywt

import numpy as np

## machine learning methods

from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
#

curfilepath = os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
sys.path.append(projhomepath)

#
# my project components

from EvaluationSchemes.Group2LeadsResults import GroupResult2Leads
from EvaluationSchemes.EvaluationMultiLeads import EvaluationMultiLeads
from TextLogger import TextLogger


# Classes and functions used in evaluation
from EvaluationSchemes.regression_evaluation import FindBadRecord as FindBadRecord
from EvaluationSchemes.regression_evaluation import GroupingRawResults as GroupingRawResults
from EvaluationSchemes.regression_evaluation import ConverterFactory as ConverterFactory
from EvaluationSchemes.regression_evaluation import ResetFolder as ResetFolder



if __name__ == '__main__':

    # Name of the experiment

    experiment_name = 'swt-paper-4'
    total_round_number = 55
    result_filename_pattern = '*.json'

    # Labels to extract statistics from.

    possible_label_list = [
        'T',
        'P',
        'Toffset',
        'Ponset',
        'Poffset',
        'Ronset',
        'R',
        'Roffset',
        ]

    # Get converter

    result_converter = ConverterFactory('simple-converter')

    # Set folder path.

    prediction_result_folder = os.path.join(projhomepath, 'result',
            experiment_name)
    evaluation_result_path = os.path.join(projhomepath,
            'EvaluationSchemes', 'results', experiment_name)

    # Grouping given result.

    should_group_result = \
        raw_input('Grouping given result folder:{}?'.format(prediction_result_folder))
    if should_group_result in ['y', 'Y']:
        print 'Grouping...'

        # Remove existing folders

        ResetFolder(evaluation_result_path)
        new_group_result_folder = os.path.join(evaluation_result_path,
                'group-result')
        ResetFolder(new_group_result_folder)

        for ind in xrange(1, total_round_number + 1):
            GroupingRawResults(ind, prediction_result_folder,
                               new_group_result_folder)
        prediction_result_folder = new_group_result_folder
        result_converter = ConverterFactory('simple-converter')

    # clear Log file

    log_file_path = os.path.join(evaluation_result_path,
                                 'Log_which_record_is_bad.txt')
    if os.path.exists(log_file_path) == True:
        shutil.rmtree(log_file_path)

    # Construct Police object

    police_obj = FindBadRecord(
        10,
        13,
        20,
        20,
        possible_label_list=possible_label_list,
        result_converter=result_converter)

    for RoundInd in xrange(1, total_round_number + 1):
        print 'processing Round :', RoundInd
        GroupResultFolder = os.path.join(prediction_result_folder,
                'round{}'.format(RoundInd))

        result_file_list = glob.glob(os.path.join(GroupResultFolder, result_filename_pattern))
        police_obj.RunEval(RoundInd,
                GroupResultFolder,
                result_file_list)

    # Compute error statistics

    police_obj.ComputeStatistics()

    # Display error statistics
    police_obj.display_error_statistics()
    police_obj.dump_statistics_to_HTML(os.path.join(evaluation_result_path,
            'evaluation-statistics.html'))
