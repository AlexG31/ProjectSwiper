#encoding:utf8
import os
import sys
import pdb
import numpy as np
import matplotlib.pyplot as plt

def prettify(ax, raw_sig, pairs, importance_list, center_index):
    '''Discretize RSWT pair importance.'''
    ax.plot(raw_sig, 'black')
    # plt.plot(raw_sig)
    # plt.plot(center_index, raw_sig[center_index], 'ro',
            # markersize = 12,
            # label = 'Center Index')

    # print 'Lenght of pairs:', len(pairs)
    # for ind in xrange(0, 10):
        # print pairs[ind]
    # print 'length of signal:', len(raw_sig)
    # print '-' * 21

    # Fill triangles
    max_height = np.max(raw_sig)
    region_width = len(raw_sig) / 8
    max_alpha = 0
    for region_left in xrange(0, len(raw_sig), region_width):
        region_right = region_left + region_width
        # Number of pairs in this region
        weight = sum(map(lambda x:x[1],
                filter(lambda x: (x[0][0][0] >= region_left and
                    x[0][0][0] < region_right),
                zip(pairs, importance_list))))
        alpha = 0.0 + float(weight) * 0.2
        max_alpha = max(max_alpha, alpha)
        ax.fill([region_left, center_index, region_right],
                [raw_sig[0], max_height, raw_sig[0]],
                color = (0.3, 0.3, 0.3),
                alpha = alpha)
    # plt.title('ECG')
    ax.grid(True)
    print 'Maximum alpha value: %f' % max_alpha
    

if __name__ == '__main__':
    prettify()
