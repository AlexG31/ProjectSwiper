#encoding:utf-8
import os
import sys
import codecs
import re


class CSVwriter:
    def __init__(self,filename):
        self.fp = codecs.open(filename,'w','utf-8')
    def output(self,matrix):
        if matrix is None or len(matrix)==0 or len(matrix[0])==0:
            return
        N = len(matrix[0])
        outputstr = []
        for datline in matrix:
            if len(datline)!=N:
                raise StandardError('matrix is not valid!(list with in list should have same lenth)')
            strlist = map(str,datline)
            outputstr.append(','.join(strlist)+'\n')
        self.fp.writelines(outputstr)
    def __del__(self):
        self.fp.close()


if __name__ == '__main__':
    csv = CSVwriter('tmp.csv')
    para = []
    for i in range(0,9):
        para.append([i,i*i,2*i])
    csv.output(para)
    csv.output(para[0:2])
