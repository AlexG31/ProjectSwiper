import os
import sys
import pdb
import numpy as np
import scipy.io

sys.path.append(r'F:\LabGit\ECG_RSWT\EvaluationSchemes')
sys.path.append(r'F:\LabGit\ECG_RSWT\QTdata')
from loadResult import load_result_simple
from loadResult import load_result
from loadQTdata import QTloader

def list2mat(list_in):
    scipy.io.savemat('test.mat',dict(sig = list_in))
def reslist_to_mat(reslist,mat_filename = 'reslist.mat'):
    label_dict = dict()
    for pos,label in reslist:
        if label in label_dict:
            label_dict[label].append(pos)
        else:
            label_dict[label] = [pos,]
    scipy.io.savemat(mat_filename,label_dict)
    print 'mat file [{}] saved.'.format(mat_filename)

def res_to_mat_fromfilename(res_filename,mat_filename):
    recID,reslist = load_result(res_filename)
    # load QT rawsig
    qt = QTloader()
    sig = qt.load(recID)
    rawsig = sig['sig']
    # save sig and reslist
    label_dict = dict()
    for pos,label in reslist:
        if label in label_dict:
            label_dict[label].append(pos)
        else:
            label_dict[label] = [pos,]
    label_dict['sig'] = rawsig
    scipy.io.savemat(mat_filename,label_dict)
    print 'mat file [{}] saved.'.format(mat_filename)
def res_to_mat_fromResult(recID,reslist,mat_filename):
    # load QT rawsig
    qt = QTloader()
    sig = qt.load(recID)
    rawsig = sig['sig']
    # load expert label
    expert_reslist = qt.getexpertlabeltuple(recID)
    # save sig and reslist
    label_dict = dict()
    for pos,label in reslist:
        if label in label_dict:
            label_dict[label].append(pos)
        else:
            label_dict[label] = [pos,]
    # Expert Labels
    for pos,label in expert_reslist:
        exp_label = 'expert_'+label
        if exp_label in label_dict:
            label_dict[exp_label].append(pos)
        else:
            label_dict[exp_label] = [pos,]
    label_dict['sig'] = rawsig
    scipy.io.savemat(mat_filename,label_dict)
    print 'mat file [{}] saved.'.format(mat_filename)
    
if __name__  == '__main__':
    ResultFolder = r'F:\Python\0502\EXResultMat'
    for ind in xrange(0,58):
        recID,reslist = load_result_simple('r9',ind)
        res_to_mat_fromResult(recID,reslist,os.path.join(ResultFolder,'{}.mat'.format(recID)))
