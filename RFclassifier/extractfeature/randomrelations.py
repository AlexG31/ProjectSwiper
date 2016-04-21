#encoding:utf-8
import os
import math
import sys
import random
import pickle
import json
from shutil import copyfile


# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(projhomepath)
projhomepath = os.path.dirname(projhomepath)

# configure file
# conf is a dict containing keys
conf = None
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)

sys.path.append(projhomepath)

# generate random relations for WT
import WTdenoise.wtfeature as wtf


def gen_rand_relations(N,WinLen):
    # gen N pairs in [0,WinLen)
    window = range(0,WinLen)
    relations = []
    for i in range(0,N):
        relations.append(random.sample(window,2))
    return relations

def refresh_project_random_relations_computeLen(copyTo = None):
    print '== Refreshing WT Randomrelations=='
    #wtfobj = wtf.WTfeature()
    #cnlist = wtfobj.getWTcoefficient_number_in_each_level()
    N = conf['DWT_LEVEL']
    fs = conf['fs']
    FixedWindowLen = conf['winlen_ratio_to_fs']*fs
    # get cnlist(max value of random pairs in each level)
    curWinLen = FixedWindowLen/2
    cnlist = []
    for i in xrange(0,N):
        cnlist.append(curWinLen)
        curWinLen/=2
        if curWinLen == 0:
            raise Exception('max value in this layer is 0!')
    WTrrJsonFileName = os.path.join(curfolderpath,'WTcoefrandrel.json')
    RelList = []
    #==========================================
    # total number of used features
    # ensure total number of random pairs== 
    # conf['WTrandselfeaturenumber_apprx']
    # number of pairs in each level is proportional
    # eg. number of pairs:
    # [500]
    # [250]
    # [125]..
    #==========================================
    Nwt = conf['WTrandselfeaturenumber_apprx']
    Nlevel = N
    Nltimes = (4**Nlevel - 1)/3
    Nl0 = Nwt/Nltimes * 4**(Nlevel-1)
    for coeflength in cnlist:
        rel = gen_rand_relations(Nl0,coeflength)
        RelList.append(rel)
        Nl0/=4
    with open(WTrrJsonFileName,'w') as fout:
        json.dump(RelList,fout)
    #==============================================
    #  Generate random relations for time-domain signal
    #==============================================
    print '== Refreshing Random Realtions =='
    fs = conf['fs']
    WinLen = conf['winlen_ratio_to_fs']*fs
    N = conf['windowpairnumber_ratio_to_winlen']*WinLen
    rel = gen_rand_relations(N,WinLen)
    with open(os.path.dirname(curfilepath)+os.sep+'ECGrandrel.json','w') as fout:
        json.dump(rel,fout)
    # copyTo result folder:
    if copyTo is not None:
        copyfile(WTrrJsonFileName,copyTo)
def refresh_project_random_relations(copyTo = None):
    print '== Refreshing WT Randomrelations=='
    wtfobj = wtf.WTfeature()
    cnlist = wtfobj.getWTcoefficient_number_in_each_level()
    WTrrJsonFileName = os.path.join(curfolderpath,'WTcoefrandrel.json')
    RelList = []
    # total number of used features
    Nwt = conf['WTrandselfeaturenumber_apprx']
    Nlevel = 5
    Nltimes = (4**Nlevel - 1)/3
    Nl0 = Nwt/Nltimes * 4**(Nlevel-1)
    for coeflength in cnlist:
        rel = gen_rand_relations(Nl0,coeflength)
        RelList.append(rel)
        Nl0/=4
    with open(WTrrJsonFileName,'w') as fout:
        json.dump(RelList,fout)
    
    print '== Refreshing Random Realtions =='
    fs = conf['fs']
    WinLen = conf['winlen_ratio_to_fs']*fs
    N = conf['windowpairnumber_ratio_to_winlen']*WinLen
    rel = gen_rand_relations(N,WinLen)
    with open(os.path.dirname(curfilepath)+os.sep+'ECGrandrel.json','w') as fout:
        json.dump(rel,fout)
    # copyTo result folder:
    if copyTo is not None:
        copyfile(WTrrJsonFileName,copyTo)
    

if __name__ == '__main__':
    #print '--- Random relation Test ---'
    #print gen_rand_relations(10,100)
    #print '-'*10
    refresh_project_random_relations()
    
    
    
