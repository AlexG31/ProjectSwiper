#encoding:utf-8
"""
single function: load testresult
"""
import os
import sys
import json
import glob
import math
import pickle
import random
import time
import pdb

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
from QTdata.loadQTdata import QTloader

def load_result(filename):
    with open(filename,'r') as fin:
        recID,reslist = pickle.load(fin)
    print 'result for record [{}] loaded.'.format(recID)
    return (recID,reslist)

def load_result_simple(round_name,index,recID = None):
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           round_name)
    result_file_list = glob.glob(os.path.join(RFfolder,'result*'))
    filename = result_file_list[index]
    with open(filename,'r') as fin:
        recID,reslist = pickle.load(fin)
    print 'result for record [{}] loaded.'.format(recID)
    return (recID,reslist)

if __name__ == '__main__':
    
    RFfolder = os.path.join(\
           projhomepath,\
           'TestResult',\
           'pc',\
           'r7')
    result_file_list = glob.glob(os.path.join(RFfolder,'result*'))
    load_result(result_file_list[0])
