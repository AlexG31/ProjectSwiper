#encoding:utf8
import os
import sys
import pdb
import matplotlib.pyplot as plt
import numpy as np

from QTdata.loadQTdata import QTloader


def show():
    '''Show ECG sample from QT database.'''
    qt = QTloader()
    sig = qt.load('sel103')
    raw_sig = sig['sig']

    expert_annotations = qt.getExpert('sel103')
    pos_list = [x[0] for x in expert_annotations]
    amp_list = [raw_sig[x[0]] for x in expert_annotations]
    labels = set([x[1] for x in expert_annotations])
    plot_range = (min(pos_list) - 10, min(pos_list) + 200)
    # raw_sig = raw_sig[plot_range[0]: plot_range[1]]

    plt.figure(1)
    time_ratio = 0.25
    # time_list = [x / time_ratio for x in xrange(plot_range[0], plot_range[1])]
    time_list = [x / time_ratio for x in xrange(0, len(raw_sig))]
    plt.plot(time_list, raw_sig, 'black')
    plt.title('QT database record sel103')
    marker_dict = dict(
            Ponset = dict(marker = '<', markerfacecolor = 'grey', fillstyle = 'left'),
            P = dict(marker = '^', markerfacecolor = 'grey', fillstyle = 'left'),
            Poffset = dict(marker = '>', markerfacecolor = 'grey', fillstyle = 'right'),
            Ronset = dict(marker = '<', markerfacecolor = 'grey', fillstyle = 'full'),
            R = dict(marker = 'p', markerfacecolor = 'grey', fillstyle = 'full'),
            Roffset = dict(marker = '>', markerfacecolor = 'grey', fillstyle = 'full'),
            T = dict(marker = '*', markerfacecolor = 'grey', fillstyle = 'top'),
            Toffset = dict(marker = 'D', markerfacecolor = 'grey', fillstyle = 'right'),
            )
    for label in labels:
        pos_list = [x[0] for x in expert_annotations if (x[1] == label and
            x[0] >= plot_range[0] and x[0] < plot_range[1])]
        amp_list = [sig['sig'][x] for x in pos_list]
        pos_list = [x / time_ratio for x in pos_list]
        display_label = label if len(label) > 1 else label + ' peak'
        plt.plot(pos_list, amp_list,
                label = display_label,
                markersize = 16,
                linestyle = 'none',
                markeredgecolor = 'black',
                **marker_dict[label])
    plt.grid()
    plt.legend(numpoints= 1)
    print 'Plot range:', plot_range
    plot_range = [x / time_ratio for x in plot_range]
    plt.xlim(plot_range[0], plot_range[1])
    plt.ylabel('Amplitude')
    plt.xlabel('Time(ms)')
    plt.show()

if __name__ == '__main__':
    show()
