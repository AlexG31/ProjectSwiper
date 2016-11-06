#encoding:utf8
import numpy as np
from smop.core import *
import pywt
import pdb
# 
    ## ERROR:
# * No fs adaption.
    
def arange(start,stop,step=1,**kwargs):
    """
    >>> a=arange(1,10) # 1:10
    >>> size(a)
    matlabarray([[ 1, 10]])
    """
    extend_value = 1 if step > 0 else -1
    return matlabarray(np.arange(start,
                                 stop+extend_value,
                                 step,
                                 **kwargs).reshape(1,-1),**kwargs)
def end():
    '''The index of the last element in the array.'''
    return 0
def squeeze_to_python(A):
    '''Similar to np.squeeze, but squeeze to list.'''
    return np.squeeze(np.array(A)).tolist()
    # return np.squeeze(np.array(A))
    # return A.astype(np.int32, copy = False)

def matlab_wavedec(
        sig_in,
        n_level,
        low_pass,
        high_pass,
        **kwargs):
    '''API for matlab wavedec.'''
    # Type conversion
    # TODO: Style change
    sig_in = np.array(sig_in)
    sig_in = np.squeeze(sig_in)
    sig_in = sig_in.tolist()

    low_pass = np.squeeze(np.array(low_pass)).tolist()
    high_pass = np.squeeze(np.array(high_pass)).tolist()


    my_wavelet = pywt.Wavelet('my_wt', [low_pass, high_pass,low_pass, high_pass])

    coef_list = pywt.wavedec(sig_in, my_wavelet, level = n_level)

    # L = [x.size for x in coef_list]
    coef_list_size = len(coef_list)
    L = [0,] * coef_list_size
    for ind in xrange(0, coef_list_size):
        L[ind] = coef_list[ind].size
    # Append length of the signal
    L.append(len(sig_in))

    C = np.array([])
    for layer in coef_list:
        C = np.append(C, layer)
    
    # Type conversion
    C = matlabarray(C)
    L = matlabarray(L)
    return [C, L]

def matlab_waverec(
        C,
        L,
        low_pass,
        high_pass,
        **kwargs):
    '''API for matlab waverec.'''
    # Type conversion
    C = np.squeeze(np.array(C))
    L = np.squeeze(np.array(L))
    L = L[0:L.size - 1]


    # Will pad zeros when length(C) < expect_length
    expect_length = np.sum(L)
    if C.size < expect_length:
        C = np.append(C, np.zeros(expect_length - C.size))


    coef_list = []
    cnt = 0
    for layer_len in L:
        layer_list = C[cnt:cnt + layer_len]
        coef_list.append(layer_list)
        cnt += layer_len

    my_wavelet = pywt.Wavelet('my_wt', [low_pass, high_pass,low_pass, high_pass])

    sig_out = pywt.waverec(coef_list, my_wavelet)
    
    # Type conversion
    sig_out = matlabarray(sig_out)

    return sig_out

@function
def DTCWT(Signal,DecLevel,Wavelet_Remain,*args,**kwargs):
    nargin = sys._getframe(1).f_locals["nargin"]
    varargin = sys._getframe(1).f_locals["varargin"]
    nargout = sys._getframe(1).f_locals["nargout"]
    
    # Signal=[0 diff(Signal1)];
    L=length(Signal)
# DTCWT.m:5
    HL=matlabarray(cat(0.03516384,0,- 0.08832942,0.23389032,0.76027237,0.5875183,0,- 0.11430184,0,0))
# DTCWT.m:6
    #   HL=[0.00325314 -0.00388321 0.03466035 -0.03887280 -0.11720389 0.27529538 0.75614564 0.56881042 0.01186609 -0.10671180 0.02382538 0.01702522 -0.00543948 -0.00455690];
#  HL=[-0.00228413 0.00120989 -0.01183479 0.00128346 0.04436522 -0.05327611 -0.11330589 0.28090286 0.75281604 0.56580807 0.02455015 -0.12018854 0.01815649 0.03152638 -0.00662879 -0.00257617 0.00127756 0.00241187];
    
    # if Wavelet_Remain(1)==1
    
    #     Fend=1;
#     Wavelet_Remain1=1:Wavelet_Remain(end)-1;
    
    
    # else
    
    #     Fend=0;
#     Wavelet_Remain1=Wavelet_Remain-1;
# end
    
    H00a,H01a,H10a,H11a,H00b,H01b,H10b,H11b=Qshift(HL,nargout=8)
# DTCWT.m:23
    #[Lp1_D,Hp1_D,Lp1_R,Hp1_R] = wfilters('bior4.4');
    Lp1_D=matlabarray(cat(0,0.0378284555073,- 0.0238494650196,- 0.110624404418,0.377402855613,0.852698679009,0.377402855613,- 0.110624404418,- 0.0238494650196,0.0378284555073))
# DTCWT.m:26
    Hp1_D=matlabarray(cat(0,- 0.0645388826287,0.0406894176092,0.418092273222,- 0.788485616406,0.418092273222,0.0406894176092,- 0.0645388826287,0,0))
# DTCWT.m:27
    Lp1_R=matlabarray(cat(0,- 0.0645388826287,- 0.0406894176092,0.418092273222,0.788485616406,0.418092273222,- 0.0406894176092,- 0.0645388826287,0,0))
# DTCWT.m:28
    Hp1_R=matlabarray(cat(- 0.0238494650196,0.110624404418,0.377402855613,- 0.852698679009,0.377402855613,0.110624404418,- 0.0238494650196,- 0.0378284555073))
# DTCWT.m:29
    C1,L1=matlab_wavedec(Signal,1,Lp1_D,Hp1_D,nargout=2)
# DTCWT.m:31
    Ca1,La1=matlab_wavedec(Signal,Wavelet_Remain[end()],H00a,H01a,nargout=2)
# DTCWT.m:34
    Cb1,Lb1=matlab_wavedec(Signal,Wavelet_Remain[end()],H00b,H01b,nargout=2)
# DTCWT.m:35
    La1_sum=ones(1,length(La1))
# DTCWT.m:37
    for ii in arange(2,length(La1)).reshape(-1):
        Ctmp=matlabarray([])
# DTCWT.m:40
        La1_sum[ii]=sum(La1[1:ii - 1])
# DTCWT.m:41
        #     Ctmp=Ca1(La1_sum(ii-1):La1_sum(ii));
#     subplot(length(La1)-1,1,ii-1)
#     plot(Ctmp)
    
    Sa_rec=zeros(length(Wavelet_Remain) + 1,length(Signal))
# DTCWT.m:47
    Sb_rec=zeros(length(Wavelet_Remain) + 1,length(Signal))
# DTCWT.m:48
    for jj in arange(1,length(Wavelet_Remain)).reshape(-1):
        C_tmp=zeros(1,La1_sum[end()])
# DTCWT.m:51
        St = length(La1) - Wavelet_Remain[jj]
# DTCWT.m:52
        Sp = length(La1) - Wavelet_Remain[jj] + 1
# DTCWT.m:53
        # print 'St =' , St
        # print 'Sp =' , Sp
        # print 'La1_sum[St] = ', La1_sum[St]
        # print 'type C_tmp:', type(C_tmp)
        # pdb.set_trace()
        # St = np.squeeze(St)
        # Sp = np.squeeze(Sp)
        # La1_sum = np.squeeze(La1_sum)

        C_tmp[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]=Ca1[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]
        C_tmp[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]=Ca1[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]
# DTCWT.m:54
        # print 'La1:', La1
        # print 'H10a:', H10a
        # print 'H11a:', H11a
        # pdb.set_trace()

        Sa_rec[jj,:]=matlab_waverec(C_tmp,La1,H10a,H11a)



# DTCWT.m:55
        C_tmp=zeros(1,squeeze_to_python(La1_sum[end()]))
# DTCWT.m:57
        St = length(La1) - Wavelet_Remain[jj]
# DTCWT.m:58
        Sp=length(La1) - Wavelet_Remain[jj] + 1
# DTCWT.m:59
        C_tmp[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]=Cb1[squeeze_to_python(La1_sum[St]) + 1:squeeze_to_python(La1_sum[Sp])]
# DTCWT.m:60
        Sb_rec[jj,:]=matlab_waverec(C_tmp,La1,H10b,H11b)
# DTCWT.m:61
    
    C_tmp=zeros(1,squeeze_to_python(La1_sum[end()]))
# DTCWT.m:64
    C_tmp[1:squeeze_to_python(La1_sum[2])]=Ca1[1:squeeze_to_python(La1_sum[2])]
# DTCWT.m:65
    Sa_rec[jj + 1,:]=matlab_waverec(C_tmp,La1,H10a,H11a)
# DTCWT.m:66
    C_tmp=zeros(1,squeeze_to_python(La1_sum[end()]))
# DTCWT.m:67
    C_tmp[1:squeeze_to_python(La1_sum[2])]=Cb1[1:squeeze_to_python(La1_sum[2])]
# DTCWT.m:68
    Sb_rec[jj + 1,:]=matlab_waverec(C_tmp,La1,H10b,H11b)
# DTCWT.m:69
    S_rec=(Sa_rec + Sb_rec) / 2
# DTCWT.m:70
    return S_rec
    
    
@function
def Qshift(HL,*args,**kwargs):
    nargin = sys._getframe(1).f_locals["nargin"]
    varargin = sys._getframe(1).f_locals["varargin"]
    nargout = sys._getframe(1).f_locals["nargout"]

    #QSHIFT Summary of this function goes here
#   Detailed explanation goes here
    L=length(HL)
# DTCWT.m:76
    Coef_HL=matlabarray([])
# DTCWT.m:77
    H00a=matlabarray([])
# DTCWT.m:78
    H01a=matlabarray([])
# DTCWT.m:79
    H10a=matlabarray([])
# DTCWT.m:80
    H11a=matlabarray([])
# DTCWT.m:81
    H00b=matlabarray([])
# DTCWT.m:82
    H01b=matlabarray([])
# DTCWT.m:83
    H10b=matlabarray([])
# DTCWT.m:84
    H11b=matlabarray([])
# DTCWT.m:85
    for ii in arange(L,1,- 1).reshape(-1):
        Coef_HL[L - ii + 1]=ceil(L / 2) + 1 - ii
# DTCWT.m:89
    
    for ii in arange(1,L).reshape(-1):
        H00a[ii]=HL[L + 1 - ii]
# DTCWT.m:95
        H01a[ii]=dot(((- 1) ** Coef_HL[ii]),HL[ii])
# DTCWT.m:97
        H00b[ii]=HL[ii]
# DTCWT.m:99

        H01b[ii]=dot(((- 1) ** Coef_HL[L + 1 - ii]),HL[L + 1 - ii])
# DTCWT.m:101
        H10a[ii]=HL[ii]
# DTCWT.m:103
        H11a[L + 1 - ii]=H01a[ii]
# DTCWT.m:105
        H10b[ii]=HL[L + 1 - ii]
# DTCWT.m:107
        H11b[L + 1 - ii]=H01b[ii]
# DTCWT.m:109
    
    return H00a,H01a,H10a,H11a,H00b,H01b,H10b,H11b
    

def TEST1():
    '''Test function.'''
    import sys
    import matplotlib.pyplot as plt

    sys.path.append('/home/alex/LabGit/ProjectSwiper/QTdata')
    from loadQTdata import QTloader
    qt = QTloader()
    sig = qt.load('sel100')

    # Process ECG signal
    raw_sig = sig['sig']

    sig_in = matlabarray(raw_sig)
    s_rec = DTCWT(sig_in, matlabarray(9), arange(1, 9))
    
    plt.figure(1)
    for ind in xrange(1, 10):
        coef = np.squeeze(np.array(s_rec[ind,:]))
        plt.subplot(5, 2, ind)
        plt.plot(coef)
        plt.title('Level %d' % ind)
        plt.grid(True)
    plt.show()
    
def TEST2():
    '''Test function.'''
    import sys
    import matplotlib.pyplot as plt

    sys.path.append('/home/alex/LabGit/ProjectSwiper/MITdb')
    from MITdbLoader import MITdbLoader
    qt = MITdbLoader()
    sig = qt.load('100')

    # Process ECG signal
    raw_sig = sig

    sig_in = matlabarray(raw_sig)
    s_rec = DTCWT(sig_in, 9, arange(1, 9))
    
    plt.figure(1)
    for ind in xrange(1, 11):
        coef = np.squeeze(np.array(s_rec[ind,:]))
        plt.subplot(5, 2, ind)
        plt.plot(coef)
        plt.title('Level %d' % ind)
        plt.grid(True)
    plt.show()
    

if __name__ == '__main__':
    # sig = matlabarray([1,2,2,3,34,3,45,213])
    # print sig
    # print type(sig)
    # print size(sig)
    # pdb.set_trace()
    TEST2()
    pdb.set_trace()

    N = 10000
    sig = arange(1, N)
    Wavelet_Remain = matlabarray(range(1,10))
    s_rec = DTCWT(sig, 9, Wavelet_Remain)
    
