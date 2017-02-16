import os
import sys
import math

import matplotlib.pyplot as plt

def Gaussian(m, s, window_length):
    sig = list()
    for ind in xrange(0, window_length):
        val = 1.0 / math.sqrt(2 * math.pi) / s * math.exp( - (ind - m) ** 2 / 2 / s ** 2)
        sig.append(val)

    plt.figure(1)
    plt.plot(sig)
    plt.show()
    
Gaussian(60.0, 10.0, 100)
