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
import pydot
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfolderpath)
projhomepath = os.path.dirname(projhomepath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import WTdenoise.wtdenoise as wtdenoise
import QTdata.loadQTdata as QTdb

## Main Scripts
# ==========
EPS = 1e-6
tmpmdlfilename = os.path.join(projhomepath,'tmpmdl.txt')


class DecisionTreeInfo:
    def __init__(self,rfmdl):
        self.rfmdl = rfmdl
        self.trees = rfmdl.estimators_
        pass
    def info(self):
        t0 = self.trees[0]
        # list dir
        for attr in dir(t0):
            print attr
        print 'tree-------------------------'
        for attr in dir(t0.tree_):
            print attr

        pdb.set_trace()
        
    def saveSVG(self,savefilename,tree_ind = 0):
        if tree_ind>= len(self.trees):
            raise Exception('tree index(tree_ind) larger than the number of trees in estimator!')
        tree0 = self.trees[tree_ind]
        self.decisiontree2svg(tree0,savefilename)

    def decisiontree2svg(self,decisiontree_in,outputpath):
        from sklearn.externals.six import StringIO
        dot_data = StringIO()
        pdb.set_trace()
        tree.export_graphviz(decisiontree_in,out_file = dot_data,
                            #feature_names = tree.feature_names,
                            class_names=self.rfmdl.classes_,
                            filled=True,rounded=True,
                            special_characters=True
                )
        graph = pydot.graph_from_dot_data(dot_data.getvalue())
        graph.write_svg(outputpath)




def test_load(filename):
    with open(filename,'r') as fin:
        rfmdl = pickle.load(fin)
        # export a single tree
        trees = rfmdl.estimators_
        tree0 = trees[0]
        decisiontree2pdf(tree0,'treeout.svg')

# =================================
# run script
# =================================
if __name__ == '__main__':
    mdlpath = os.path.join(curfolderpath,'model','trained_model.mdl')
    with open(mdlpath,'r') as fin:
        rfmdl = pickle.load(fin)
    tree_info = DecisionTreeInfo(rfmdl)
    tree_info.saveSVG('tmp.svg')
