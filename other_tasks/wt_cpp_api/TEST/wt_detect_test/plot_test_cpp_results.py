#encoding:utf8
import os
import sys
import matplotlib.pyplot as plt


def plot_result():
    '''Read signal & result txt, and plot result.'''
    file_id = 'real_data'
    result_file_name = 'result.dat'

    sig = list()
    with open('./input_data/%s.txt' % file_id, 'r') as fin:
        len_sig = int(fin.readline())
        for ind in xrange(0, len_sig):
            text = fin.readline()
            if text is None:
                break
            val = float(text)
            sig.append(val)

    results = dict()
    with open('../../c_output/%s' % result_file_name, 'r') as fin:
        len_results = int(fin.readline())
        for ind in xrange(0, len_results):
            text = fin.readline()
            if text is None:
                break
            result_pair = text.split()
            label = result_pair[0]
            pos = int(result_pair[1])

            if label not in results:
                results[label] = list()
            results[label].append(pos)

    plt.plot(sig)
    plt.title('test signal')
    
    for label in ['P', 'R', 'T']:
        amp_list = [sig[x] for x in results[label]]
        plt.plot(results[label], amp_list, '^', markersize = 12, label = label)
    plt.legend()
    plt.show()


plot_result()
