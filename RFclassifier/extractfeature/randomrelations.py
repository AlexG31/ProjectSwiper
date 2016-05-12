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
    CenterPos = int(WinLen/2)
    LBound = -int(fs/10)
    LBound = max(0,LBound)
    RBound = int(fs/10)
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
            raise Exception('max value in layer {} is 0!'.format(i))
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
    Ndwt = N
    N_current_layer = Nwt*(2**(Ndwt-1))/((2**Ndwt)-1)
    for cnlist_ind,WinLen_this_level in enumerate(cnlist):
        #----------
        # WinLen: WinLen_this_level
        # number of pairs: N_this_level
        # No repeat pairs
        #----------
        #rel = gen_rand_relations(N_this_level,WinLen_this_level)
        rel = random.sample(Window_Pair_Generator(WinLen_this_level),N_current_layer)
        # ================
        # Add nearby pairs
        # fs = 250
        # [-25,25]
        # [-fs/10,fs/10]
        # ================
        AddNearbyPairs(rel,WinLen_this_level)
        RelList.append(rel)
        if cnlist_ind == len(cnlist)-1:
            # Approximation level pairs
            rel = random.sample(Window_Pair_Generator(WinLen_this_level),N_current_layer)
            AddNearbyPairs(rel,WinLen_this_level)
            RelList.append(rel)
        N_current_layer /=2
    with open(WTrrJsonFileName,'w') as fout:
        json.dump(RelList,fout)
    #==============================================
    #  Generate random relations for time-domain signal
    #==============================================
    print '== Refreshing Random Realtions =='
    fs = conf['fs']
    WinLen = conf['winlen_ratio_to_fs']*fs
    N = conf['windowpairnumber_ratio_to_winlen']*WinLen
    #rel = gen_rand_relations(N,WinLen)
    rel = random.sample(Window_Pair_Generator(WinLen),N)
    with open(os.path.dirname(curfilepath)+os.sep+'ECGrandrel.json','w') as fout:
        json.dump(rel,fout)
    # copyTo result folder:
    if copyTo is not None:
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
    
    
