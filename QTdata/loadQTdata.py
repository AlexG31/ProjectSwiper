#encoding:utf-8
import os
import sys
import pickle
import json
import glob
import marshal
import matplotlib.pyplot as plt
import pdb
from scipy.io import matlab
import numpy as np
from matplotlib import pyplot as plt
# project homepath
curfilepath =  os.path.realpath(__file__)
projhomepath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(projhomepath)
# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)

class QTloader:
    def __init__(self):
        # get QT records list
        self.rec_dir_path = os.path.join(os.path.dirname(curfilepath),'QTdb_full')
        extension = r'.mat'
        self.extension = extension
        files = glob.glob(os.path.join(self.rec_dir_path,'*{}'.format(extension)))
        # get *.txt
        files = map(lambda x:os.path.split(x)[1],files)
        # strip '.txt'
        files = map(lambda x:x.split(extension)[0],files)
        self.reclist = files

        # display records info
        #print files
        #print '--- number of records:',len(files),'---'

    def load(self,recname = 'sel103'):
        filename = os.path.join(self.rec_dir_path,recname+self.extension)
        mat = matlab.loadmat(filename)
        sig = self.matdata_format_sigdata(mat)
        return sig

    def matdata_format_sigdata(self,mat):
        ret = dict()
        # only first lead
        leadnum = 0
        sig = mat['sig'][leadnum].tolist()
        time = mat['time'].tolist()
        marks = dict()
        labels = mat['code_label'][0].tolist()
        labels = ['R','P','T','lp','rp']
        for ind,label in enumerate(labels):
            cplist = mat['markercell'][0][ind]
            while len(cplist)>0 and isinstance(cplist[0],np.ndarray) == True:
                cplist = cplist[0]
            marks[label] = cplist.tolist()
        ret['sig'] = sig
        ret['time'] = time
        ret['marks'] = marks
        ret['sig2'] = mat['sig'][1-leadnum].tolist()
        return ret
    def getQTrecnamelist(self):
        return self.reclist
    def getExpert(self,recname):
        # alias
        return self.getexpertlabeltuple(recname)

    def plotrec(self,recname = 'sel103',showExpertLabel = False):
        # show rawsig&labels
        sig = self.load(recname)
        plt.figure(1)
        Labels = self.getexpertlabeltuple(recname)
        lpos = [x[0] for x in Labels]
        Amps = [sig['sig'][x] for x in lpos]
        plt.plot(sig['sig'])
        plt.plot(lpos,Amps,'ro')
        plt.xlim(lpos[0]-100,lpos[-1]+100)
        plt.title(recname)
        plt.show()

    def PlotAndSaveRec(self,recname = 'sel103',showExpertLabel = False,xWinLen = 400,savefolderpath = 'TmpImg'):
        # show rawsig&labels
        sig = self.load(recname)

        plt.figure(num = 1,figsize = (20,10))
        Labels = self.getexpertlabeltuple(recname)

        lpos = [x[0] for x in Labels]
        Amps = [sig['sig'][x] for x in lpos]
        plt.plot(sig['sig'])
        plt.plot(lpos,Amps,'ro')
        # text box
        #bbox_props = dict(boxstyle="rarrow,pad=0.3", fc="cyan", ec="b", lw=2)
        #t = ax.text(0, 0, "Direction", ha="center", va="center", rotation=45,size=15,bbox=bbox_props)
        xylist = zip(lpos,Amps)
        for ind,xy_val in enumerate(xylist):
            plt.annotate(s= Labels[ind][1],xy = xy_val)
        # xlim
        x_left = lpos[0]-100
        #x_right = lpos[-1]+100
        x_right = x_left + xWinLen
        plt.xlim(x_left,x_right)

        plt.title(recname)
        plt.savefig(os.path.join(savefolderpath,recname+'.png'))
        #plt.show()
        plt.clf()

    def getreclist(self):
        return self.reclist
    def getexpertlabeltuple(self,recname,sigIN = None,negposlist = None):
        # get QT sig
        if sigIN is not None:
            sig = sigIN
        else:
            sig = self.load(recname)
        # init
        posposlist = [] # positive position list
        labellist = [] # positive label list
        tarpos = []

        # shallow copy
        mks = sig['marks']
        for kk in mks.keys():
            tarpos.extend(zip(mks[kk],[kk]*len(mks[kk])))
        # sort target labels according to kpos
        tarpos.sort(key = lambda x:x[0])

        excludedist = conf['training_excludedist']
        # start extracting positive observasions
        prev_tarpos = None
        for ti,tarpair in enumerate(tarpos):
            if prev_tarpos is not None:
                # add negpos
                # add neg list in [lnegpos,rnegpos]
                #
                rnegpos = tarpair[0] - excludedist
                lnegpos = prev_tarpos + excludedist
                if rnegpos < lnegpos:
                    # no enough space for negtive samples
                    pass

                else:
                    # add to candidate neg sample list
                    if negposlist is not None:
                        negposlist.extend(range(lnegpos,rnegpos+1))

            
            # use this var to find lnegboundaries
            prev_tarpos = tarpair[0]
            # current label
            curlabel = None
            # ====================
            # possible tarpair[1]:
            # T,P,R,lp,rp
            # ====================
            if tarpair[1] in ['T','P','R']:
                curlabel = tarpair[1]
            elif tarpair[1] == 'lp':
                # find corresponding wave label
                curlabel = None
                if ti+1 <len(tarpos):
                    npair = tarpos[ti+1]
                    if npair[1] in ['T','R','P']:
                        curlabel = npair[1]+'onset'
                if curlabel is None:
                    # some records have U wave boundaries
                    continue
            elif tarpair[1] == 'rp':
                # find corresponding wave label
                curlabel = None
                if ti-1 >= 0:
                    npair = tarpos[ti-1]
                    if npair[1] in ['T','R','P']:
                        curlabel = npair[1]+'offset'
                if curlabel is None:
                    # Possible U wave
                    continue
            else:
                raise StandardError('original label is [{}], this is unexpected.'.format(tarpair[1]))
                
            # ignore Tonset
            if curlabel == 'Tonset':
                continue
            #===========================
            # add to list
            # for map build in function
            #===========================
            posposlist.append(tarpair[0])
            labellist.append(curlabel)

        # --------------------
        # return type
        # [ [pos,label],....]
        # --------------------
        return zip(posposlist,labellist)




if __name__ == '__main__':
    pass
    #invalidlist = conf['InvalidRecords']
    #qt = QTloader()
    #recname = invalidlist[0]
    #recname = 'sel232'
    #sig = qt.load(recname)
    ##self defined plot
    ##plt.figure(1)
    ##plt.plot(sig['sig'])
    ##pdb.set_trace()
    #qt.plotrec(recname)
    #pdb.set_trace()
