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


class ListResultConverter(object):
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
        result_out = dict()
        result_out['LeadResult'] = list()

        rec_name = result_in[0][0]
        result_out['recname'] = rec_name

        for cur_name, lead_result in result_in:
            lead_result_dict = dict()
            for result_item in lead_result:
                pos, label = result_item[0:2]
                if len(result_item) >= 3:
                    confidence = result_item[2]

                if label not in lead_result_dict:
                    lead_result_dict[label] = [pos,]
                else:
                    lead_result_dict[label].append(pos)
            result_out['LeadResult'].append(lead_result_dict)
        return result_out
            

## TEST
if __name__ == '__main__':
    result_file_path = '/home/alex/LabGit/ProjectSwiper/result/run-6/round1/result_sel230'
    with open(result_file_path, 'r') as fin:
        result = json.load(fin)
        result = ListResultConverter.convert(result)
        print result.keys()
        print result['LeadResult'][0].keys()
        print result['LeadResult'][0]['P'][0:10]
        pdb.set_trace()
