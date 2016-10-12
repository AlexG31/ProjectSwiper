"""
This is ECG feature extractor class
Aiming to extract feature for training and classification

Author: Gaopengfei
"""

#encoding:utf-8
import os
import sys
import json
import math
import logging
import pdb
import pywt
import array

import matplotlib.pyplot as plt
# project homepath
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(curfilepath)
projhomepath = os.path.dirname(projhomepath)
projhomepath = os.path.dirname(projhomepath)

# configure file
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
import WTdenoise.wtdenoise as wtdenoise
import WTdenoise.wtfeature as wtf


# Logging
log = logging.getLogger()

EPS = 1e-6

class ECGfeatures:
    '''Collect ECG feature with SWT.

    1. Must initialise with raw ecg signal.
    2. then the frompos() function can be used to extract feature
        for position provided.
    '''
    def __init__(
                self,
                rawsig,
                isdenoised = True,
                wavelet = 'db6',
                swt_max_level = 7,
                random_relation_path = None,
            ):
        # Validation Check
        if not isinstance(rawsig,list) and not isinstance(rawsig,array.array):
            raise StandardError('Input rawsig is not a list type![WTdenoise]')

        # Default value of random relation files.
        self.random_relation_path_ = random_relation_path
        # May denoise rawsig to get sig
        self.signal_in = rawsig
        self.rawsig = rawsig

        self.fixed_window_length = conf['fs'] * conf['winlen_ratio_to_fs']
        log.info('Fixed window length by ECGconf.json: %d' % self.fixed_window_length)

        # Do SWT once for all.
        wt_level = conf['WT_LEVEL']
        rawsig = self.crop_data_for_swt(rawsig)
        coeflist = pywt.swt(rawsig,wavelet,wt_level)
        cAlist,cDlist = zip(*coeflist)
        self.cAlist = cAlist
        self.cDlist = cDlist
        
        
    def crop_data_for_swt(self,rawsig):
        '''Padding zeros to make the length of the signal to 2^N.'''
        # crop rawsig
        base2 = 1
        N_data = len(rawsig)
        if len(rawsig)<=1:
            raise Exception('len(rawsig)={},not enough for swt!',len(rawsig))
        crop_len = base2
        while base2<N_data:
            if base2*2>=N_data:
                crop_len = base2*2
                break
            base2*=2
        # Extending this signal input with its tail element.
        if N_data< crop_len:
            rawsig += [rawsig[-1],]*(crop_len-N_data)
        return rawsig

    @staticmethod
    def signal_preprocessing(rawsig):
        # wavelet denoise:
        sig = wtdenoise.denoise(rawsig)

        return sig

    def frompos(self,pos):
        '''WT feature Warpper.'''
        return self.getWTfeatureforpos(pos)

    
    def getWindowedSignal(self,x,sig, fixed_window_length):
        '''Get windowed signal segment centered in x.'''
        # Padding with head or tail element when out of bound.

        # get windowed signal from original signal
        # padding zeros if near boundaries
        FixedWindowLen = fixed_window_length
        winlen_hlf = int(fixed_window_length/ 2)
        # return windowed sig 
        winsig = []
        if x <winlen_hlf:
            # use sig[0] to extend left
            winsig.extend([sig[0]]*(winlen_hlf-x))
            # original sigal
            winsig.extend(sig[0:x])
        else:
            winsig.extend(sig[x-winlen_hlf:x])
        # for odd & even FixedWindowLen
        right_bound = x+winlen_hlf +1
        if FixedWindowLen%2 == 0:
            right_bound -= 1
        if right_bound > len(sig):
            winsig.extend(sig[x:])
            winsig.extend([sig[-1],]*(right_bound - len(sig)))
        else:
            winsig.extend(sig[x:right_bound])
        # debug
        if len(winsig) != FixedWindowLen:
            # error : the returned windowed signal must be a fix-length signal
            print 'error : the returned windowed signal must be a fix-length signal!'
            pdb.set_trace()

        return winsig

    def GetWindowedMatrix(self, position):
        '''Windowing the rawsignal and SWT coefficients.'''
        fixed_window_length = self.fixed_window_length

        windowed_matrix = []
        
        # Adding time-domain windowed signal.

        windowed_matrix.append(self.getWindowedSignal(position, self.rawsig, fixed_window_length))
        # Apply the window in each level of swt coefficients.
        for detail_coefficients in self.cDlist:
            windowed_matrix.append(self.getWindowedSignal(position, detail_coefficients, fixed_window_length))
        # Adding approximation level.
        windowed_matrix.append(self.getWindowedSignal(position, self.cAlist[-1], fixed_window_length))

        return windowed_matrix

    def debug_PlotWindowedMatrix(self,matrix,max_level = 4):
        '''Plot matrix in figure.'''
        
        plt.figure()
        plt.grid(True)
        axes_index = 1
        for signal in matrix:
            if axes_index > max_level:
                break
            plt.subplot(max_level,1, axes_index)
            axes_index += 1
            plt.plot(signal)
        plt.show()

        
    def getWTfeatureforpos(self,pos,WithNormalPairFeature = False):
        '''Get WT feature from position in ECG time-domain waveform.'''
        pos = int(pos)
        if pos<0 or pos >= len(self.signal_in):
            raise StandardError('input position posx must in range of sig indexs!')
        rawsig = self.rawsig
        
        # Stateful... Apply window in each level of swt coefficients.
        windowed_matrix = self.GetWindowedMatrix(pos)

        # debug to see if the windowed matrix is correct.
        #self.debug_PlotWindowedMatrix(windowed_matrix)
        #pdb.set_trace()

        # normalization
        windowed_ecg = windowed_matrix[0]
        Ampmax = max(windowed_ecg)
        Ampmin = min(windowed_ecg)
        sig_height = float(Ampmax-Ampmin)
        if sig_height <= EPS:
            sig_height = 1
        windowed_matrix = [[(val-Ampmin)/sig_height for val in signal]
                for signal in windowed_matrix]

        features = []

        # Load Random Relations.
        Result_path_conf = conf['ResultFolder_Relative']
        saveresultpath = projhomepath
        for folder in Result_path_conf:
            saveresultpath = os.path.join(saveresultpath,folder)

        # Default value for random relations json file.
        # For API.
        if self.random_relation_path_ is None:
            WTrrJsonFileName = os.path.join(saveresultpath,'rand_relations.json')
        else:
            WTrrJsonFileName = os.path.join(self.random_relation_path_,'rand_relations.json')
        with open(WTrrJsonFileName,'r') as fin:
            wt_pair_list = json.load(fin)

        for signal ,pair_list in zip(windowed_matrix[1:],wt_pair_list):
            fv = [signal[x[0]] - signal[x[1]] for x in pair_list]
            features.extend(fv)
            fv = [abs(signal[x[0]] - signal[x[1]]) for x in pair_list]
            features.extend(fv)
        
        return features


## for multiProcess
def frompos_with_denoisedsig(Params):
    # 
    # map function should have only 1 Param
    # ,so I wrapped them into one
    #
    denoisedsig,pos = Params
    fvExtractor = ECGfeatures(denoisedsig,isdenoised = True)
    return fvExtractor.frompos(pos)


# debug
if __name__ == '__main__':
    from QTdata.loadQTdata import QTloader
    qt = QTloader()

    sigStruct = qt.load('sel100')
    #ft = ECGfeatures(sigStruct['sig'])
    #ft.getWTfeatureforpos(1000)



