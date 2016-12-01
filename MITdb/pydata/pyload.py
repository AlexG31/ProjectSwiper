import os
import sys
import pickle
import pdb


with open('100_sig1','r') as fin:
    sig = pickle.load(fin)
    pdb.set_trace()
    print type(sig)
    print 'sig[0] = ',sig[0]
