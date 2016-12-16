#encoding:utf8
import os
import sys
import glob
import codecs
import matplotlib.pyplot as plt

import subprocess
import numpy as np
import scipy.io as sio
import pdb


def WriteMatlabInputFile(arg_str = '/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/TEST/DTCWT/input_data/100.mat'):
    '''Write txt file with matlab input parameters.'''
    with open('./input_data/matlab_args.txt', 'w') as fout:
        fout.write(arg_str + '\n')
    
def RunMatlab(file_name):
    '''Run matlab file.'''
    subprocess.call(["matlab","-nojvm","<",file_name]);

def ConvertMat2Txt():
    '''Convert Matlab file format to txt.'''
    files = glob.glob("./input_data/*.mat")
    for file_name in files:
        dat = sio.loadmat(file_name)
        sig = dat['sig'];

        dat_name = os.path.split(file_name)[-1]
        dat_name = dat_name.split('.mat')[0]

        output_file_name = os.path.join('./input_data', dat_name + '.txt')
        
        with open(output_file_name, 'w') as fout:
            fout.write('%d\n' % len(sig))
            for val in sig:
                fout.write('%f\n' % val)
        
        

def RunC(file_name, record_name = '100'):
    '''Run c binary.'''
    subprocess.call(["./"+file_name,"./input_data/%s.txt" % record_name])

def Compare():
    '''Compare the results of matlab and C.'''
    
    # error_info_file = open('./output.txt','a+')

    with open('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/matlab_output/QRS_Locations.dat', 'r') as matlab_fin:
        with open('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/c_output/result.dat', 'r') as c_fin:
            line_ind = 1
            while True:
                mat_line = matlab_fin.readline()
                c_line = c_fin.readline()
                if len(mat_line) == 0 and len(c_line) == 0:
                    break

                if len(mat_line) == 0:
                    # raise Exception('Matlab output have less lines!')
                    print ('Matlab output have less lines!')
                    break
                if len(c_line) == 0:
                    # raise Exception('C output have less lines!')
                    print ('C output have less lines!')
                    break

                mat_line = mat_line.strip('\r\n ')
                c_line = c_line.strip('\r\n ')

                if len(mat_line) > 0 and len(c_line) > 0:
                    mat_val = float(mat_line)
                    c_val = float(c_line)
                
                    if abs(c_val - mat_val) > 1.0 + 1e-6:
                        # error_info_file.write('\n[Diff at line %d]\n' % line_ind)
                        print '\n[Diff at line %d]' % line_ind
                        print '[matlab] %s' % mat_line
                        print '[C] %s' % c_line
                        # error_info_file.write('[matlab] %s\n' % mat_line)
                        # error_info_file.write('[c] %s\n' % c_line)
                line_ind += 1
                    
    print 'Total line_ind:', line_ind
    # error_info_file.close()

                

def TestMITdata():
    '''Test and compare DTCWT function on all of the mitdb data.'''
    # First get all the record names in the MITdb
    files = glob.glob('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/TEST/DTCWT/input_data/*.mat')
    len_files = len(files)
    for ind in xrange(0, len_files):
        files[ind] = os.path.split(files[ind])[-1]
        files[ind] = files[ind].split('.mat')[0]
        
    for record_name in files:
        RunC('DTCWT_TEST', record_name)

        WriteMatlabInputFile('./input_data/%s.mat' % record_name)
        RunMatlab('run_DTCWT.m')

        with open('./output.txt', 'a+') as fout:
            fout.write('\nResult of record %s:\n' % record_name)
        Compare()
    

# TestMITdata()
RunC('KPD_test', '100')

WriteMatlabInputFile()
RunMatlab('KPD_test.m')

Compare()


# ConvertMat2Txt()
