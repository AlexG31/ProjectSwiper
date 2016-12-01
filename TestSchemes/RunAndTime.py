#encoding:utf-8
import os
import sys
import time



class RunAndTime:
    def __init__(self,costunit = 'min'):
        self.timecost = 0
        self.costunit = costunit
        pass
    def cost_output(self,prompt):
        cost = self.timecost
        if self.costunit == 'min':
            cost/=60.0
        elif self.costunit == 'h':
            cost/=60*60.0;
        elif self.costunit == 'ms':
            cost *= 1000.0
        else:#sec
            pass
        outputstr = '{} {:.04f} {}'.format(prompt,cost,self.costunit)
        print outputstr
        return outputstr
        
    def run(self,function,params,prompt = ur'Timing Cost:'):
        time0 = time.time()
        # ==============
        # run the function with parameters
        # ==============
        ret = function(*params)
        time1 = time.time()
        self.timecost = time1 - time0
        self.cost_output(prompt)
        return ret


class CostFunc:
    def __init__(self):
        pass
    @staticmethod
    def costfunc1(N,prompt):
        a = 0
        print prompt
        for i in xrange(0,N):
            a += i
        return a


if __name__ == '__main__':
    print 'Run and time evaluation:'
    rtimer = RunAndTime(costunit = 'ms')
    params = [1000000,'ok , let''s begin!']
    
    print 'sum = ',rtimer.run(CostFunc.costfunc1,params)





