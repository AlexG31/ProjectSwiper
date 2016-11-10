#encoding:utf8
import os
import glob
import sys
import subprocess


def ch_name():
    file_list = glob.glob("./*.c");
    for file_name in file_list:
        new_file = file_name + 'c'
        with open(file_name, "r") as fin:
            with open(new_file, 'w') as fout:
                # fout.write('#include "stdafx.h"');
                for line in fin:
                    fout.write(line)
    print file_list


if __name__ == '__main__':
    ch_name();
