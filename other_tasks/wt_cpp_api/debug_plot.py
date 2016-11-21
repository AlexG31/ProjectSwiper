#encoding:utf8
import os
import sys
import glob
import pdb
import matplotlib.pyplot as plt;

fig_count = 1

def PlotData(file_name = None, title = 'title'):
    if file_name is None:
        file_name = "/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/tmp.out"
    with open(file_name, 'r') as fin:
        sig_len = int(fin.readline())
        sig = []
        for ind in xrange(0, sig_len):
            val = float(fin.readline())
            sig.append(val)
    
    global fig_count
    plt.figure(fig_count)
    fig_count += 1

    plt.plot(sig)
    plt.title(title)
    plt.show(block = False)

def PlotS_rec(file_name = None):
    s_rec_folder = "/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/s_rec"

    s_rec_files = glob.glob(os.path.join(s_rec_folder, "*.txt"))
    s_rec_files.sort()

    plt.figure(1)
    coef_index = 1

    for s_rec_filename in s_rec_files:
        fileID = os.path.split(s_rec_filename)[1]

        # Load signal from file.
        with open(s_rec_filename, 'r') as fin:
            sig_len = int(fin.readline())
            sig = []
            for ind in xrange(0, sig_len):
                val = float(fin.readline())
                sig.append(val)
    
        # Plot subband signal
        plt.subplot(len(s_rec_files), 1, coef_index)
        coef_index += 1
        plt.plot(sig)
        plt.title(fileID)
        plt.grid(True)
        plt.xlim(0, 4500)

    # show()
    plt.show()

if __name__ == '__main__':
    PlotData(title = 'cpp tmp.out')
    # PlotData('./ecg-samples/mit-100.txt')
    # PlotData('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/tmp.out')
    PlotData(('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/'
        'matlab_output/tmp.out'), title = 'matlab tmp.out')
    # PlotData('/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/s_rec/s_rec0.txt')
    # PlotS_rec()
    pdb.set_trace()
