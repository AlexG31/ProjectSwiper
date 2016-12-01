#encoding:utf-8
"""
Result Converter
Author : Gaopengfei
"""
import os
import sys
import json
import glob
import math
import pickle
import random
import bisect
import time
import pdb


class OriginalConverter(object):
    def __init__(self):
        pass
    @staticmethod
    def convert(result_in):
        '''Convert list result format.
            Inputformat:
                [
                    [
                        "sel100",
                        [
                            [1,'white',0.3],
                            [2,'P',0.8],
                            ...
                        ]
                    ],
                    [...],
                ]
            Outputformat:
                {
                    'recname': [],
                    'LeadResult': [
                        {
                            'P':[],
                            'T':[],
                        },
                        {
                            'P':[],
                            'T':[],
                        },
                    ],
                }
        '''
        return result_in 
            

## TEST
if __name__ == '__main__':
    result_file_path = '/home/alex/LabGit/ProjectSwiper/result/run-6/round1/result_sel230'
    with open(result_file_path, 'r') as fin:
        result = json.load(fin)
        result = OriginalConverter.convert(result)
        print 'len(result):',len(result)
        print 'len(result[0]):',len(result[0])
        print 'len(result[0][1]):',len(result[0][1])
        pdb.set_trace()
