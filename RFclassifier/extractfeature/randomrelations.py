#encoding:utf-8
import os
import math
import sys
import logging
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

log = logging.getLogger()

# generate random relations for WT
import WTdenoise.wtfeature as wtf


class Window_Pair_Generator(object):
    def __init__(self,WinLen):
        self.WinLen = WinLen
    def __len__(self):
        WinLen = self.WinLen
        if WinLen<=1:
            return 0
        else:
            N = self.WinLen
            return N*(N-1)/2
    def __iter__(self):
        return self.gen()
    def gen(self):
        WinLen = self.WinLen
        for i in xrange(0,WinLen-1):
            for j in xrange(i+1,WinLen):
                yield (i,j)
#def gen_rand_relations(N,WinLen):
    ## gen N pairs in [0,WinLen)
    ## with no repeat
    
    #window = range(0,WinLen)
    #relations = []
    #for i in range(0,N):
        #while True:
            #new_pair = random.sample(window,2)
            ## not in relations list
            #is_repeat  = False
            #for old_pair in relations:
                #if old_pair[0] == new_pair[0] and old_pair[1] == new_pair[1]:
                    #is_repeat = True
                    #break
            #if is_repeat == True:
                #continue
            #relations.append(random.sample(window,2))
    #return relations
def AddNearbyPairs(rel,WinLen,fs = 250):
    '''Hack method: add pairs with one point at center of the window.'''
    CenterPos = int(WinLen/2)
    LBound = CenterPos-int(fs/10)
    LBound = max(0,LBound)
    RBound = CenterPos + int(fs/10)
    RBound = min(WinLen - 1,RBound)
    for pair_right in xrange(LBound,RBound+1):
        if pair_right == CenterPos:
            continue
        elif CenterPos < pair_right:
            new_pair = (CenterPos,pair_right)
        else:
            new_pair = (pair_right,CenterPos)
        # not in rel
        is_in_rel = False
        for old_pair in rel:
            if old_pair[0] == new_pair[0] and old_pair[1] == new_pair[1]:
                is_in_rel = True
                break
        if is_in_rel == False:
            rel.append(new_pair)

def refresh_project_random_relations_computeLen(copyTo = None):
    '''Refresh random select relations.'''
    print 'Refreshing WT Randomrelations=='

    # Level of wavelet transform.
    wt_level = conf['WT_LEVEL']
    sampling_frequency = conf['fs']
    FixedWindowLen = conf['winlen_ratio_to_fs'] * sampling_frequency

    WTrrJsonFileName = os.path.join(curfolderpath,'WTcoefrandrel.json')
    # Relation list per level.(total:wt_level + 1)
    RelList = []
    total_pair_number = conf['WTrandselfeaturenumber_apprx']

    # Why divide by 2? the pairs diff&abs are added to feature vector,
    # therefore there's 2-fold feature for a pair.
    pair_number_per_layer = total_pair_number / (wt_level + 1.0) / 2.0
    pair_number_per_layer = int(pair_number_per_layer)

    for level_index in xrange(0, wt_level + 1):
        rel = random.sample(Window_Pair_Generator(FixedWindowLen), pair_number_per_layer)
        RelList.append(rel)

    log.info('Generated random relations, %d levels, %d pairs per level.', len(RelList), pair_number_per_layer)
    with open(WTrrJsonFileName,'w') as fout:
        json.dump(RelList,fout,indent = 4)
    if copyTo is not None:
        log.info('Copying %s to %s' %(WTrrJsonFileName, copyTo))
        copyfile(WTrrJsonFileName,copyTo)

if __name__ == '__main__':
    #print '--- Random relation Test ---'
    #print gen_rand_relations(10,100)
    #print '-'*10
    #refresh_project_random_relations()
    #for val in Window_Pair_Generator(6):
        #print val
    N1 = 100
    N2 = 4
    rel = random.sample(Window_Pair_Generator(N1),N2)
    for val in rel:
        print val
    
    
