#encoding:utf-8
"""
Evaluation ECG classification Result
Author : Gaopengfei
"""
import os
import sys
import json
import math
import pickle
import random
import time
import bisect
import pdb

import numpy as np
## machine learning methods
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# project homepath
# 
curfilepath =  os.path.realpath(__file__)
curfolderpath = os.path.dirname(curfilepath)
projhomepath = curfolderpath
projhomepath = os.path.dirname(projhomepath)
# configure file
# conf is a dict containing keys
with open(os.path.join(projhomepath,'ECGconf.json'),'r') as fin:
    conf = json.load(fin)
sys.path.append(projhomepath)
#
# my project components
import extractfeature.extractfeature as extfeature
import QTdata.loadQTdata as QTdb
from EvaluationSchemes.csvwriter import CSVwriter


class ECGstatistics:
    def __init__(self,fResultList):
        # result list:
        # ((recname,record result)...)
        # 
        # record result:
        # ((pos,label)...)

        self.fResultList = fResultList
        self.QTloader = QTdb.QTloader()
        self.pErr = None
        self.pFN = None
        self.pFP = None

    def bsMatchLabel(self,\
            expertLabelList,\
            recname,\
            predictLabelList,\
            pErr,\
            pFN):
        #
        # expertLabel:(epos,elabel)
        # predictLabelList:[(tpos,tlabel),...]
        #
        predictPosList = [x[0] for x in predictLabelList]
        
        Ner = len(expertLabelList)
        boundary_width_th = 15

        for e_index,expertLabel in enumerate(expertLabelList):
            epos,elabel = expertLabel[0],expertLabel[1]
            Lb,Rb = 1,-1
            if e_index-1 < 0:
                Lb = epos-boundary_width_th
            else:
                Lb = expertLabelList[e_index-1][0]
            if e_index+1 >= Ner:
                Rb = epos+boundary_width_th
            else:
                Rb = expertLabelList[e_index+1][0]
            # 1. find Lb&Rb where epos can be predicted:(Lb,Rb)
            #Lb,Rb = None,None
            # 2. bw search
            
            bLi,bRi = bisect.bisect_right(predictPosList,Lb),\
                    bisect.bisect_left(predictPosList,Rb)
            matchposlist = [x[0] for x in predictLabelList[bLi:bRi]\
                    if x[1] == elabel]
            if len(matchposlist) == 0:
                # FN
                pFN['pos'].append(epos)
                pFN['label'].append(elabel)
                pFN['recname'].append(recname)
            else:
                # find the closet
                curerr = matchposlist[0] - epos
                for ppos in matchposlist:
                    if abs(ppos-epos)<abs(curerr):
                        curerr = ppos - epos
                # predicted pos = pErr['pos']+pErr['err']
                # Err
                pErr['err'].append(curerr)
                pErr['pos'].append(epos)
                pErr['label'].append(elabel)
                pErr['recname'].append(recname)
        
        
    def eval(self,debug = False):
        # Param:
        # debug: show match pairs
        #
        # Find error and FN and False Positive
        #=======================================
        # statistics in this round
        #=======================================
        # False Negtive
        pFN =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
        # False Positive
        pFP =  {
                'pos':[],
                'label':[],
                'recname':[]
                }
        # Error
        pErr = {
                'err':[],
                'pos':[],
                'label':[],
                'recname':[]
                }
        print 
        print '[Eval]','='*30
        for recname,reslist in self.fResultList:
            sig = self.QTloader.load(recname)
            # --------------------------------------
            # expert result and rf prediction result
            # --------------------------------------
            expres = self.QTloader.getexpertlabeltuple(recname)
            reslist.sort(key = lambda x:x[0])
            # find closest predicted label with bw search
            self.bsMatchLabel(expres,recname,reslist,pErr,pFN)
            # get False Positive number
            self.get_FalsePositive_InExpertLabelRange(reslist,pErr,pFP,recname)
                
            # debug each recname per paragraph
            print '[record{}]len pFN = {},mean= {:.2f} ms,stdvar = {:.2f} ms'.format(recname,len(pFN['pos']),np.nanmean(pErr['err'])*4.0,np.nanstd(pErr['err'])*4.0)
            if debug:
                print 

        self.pErr = pErr
        self.pFN = pFN
        self.pFP = pFP
        return (pErr,pFN)

    def get_FalsePositive_InExpertLabelRange(self,reslist,pErr,pFP,recname,skip_Thres = 100):
        ExpertPos_ErrorList = zip(pErr['pos'],pErr['err'])
        matched_poslist = map(lambda x:x[0]+x[1],ExpertPos_ErrorList)
        #raw_prediction_poslist = map(lambda x:x[0],reslist)
        raw_prediction_poslist = reslist
        # sort two list
        matched_poslist.sort()
        raw_prediction_poslist.sort(key = lambda x:x[0])
        # find FP
        FirstTime = True
        raw_ind = 0
        N_matched = len(matched_poslist)
        for mpos_ind,mpos in enumerate(matched_poslist):
            if mpos == raw_prediction_poslist[raw_ind][0]:
                #print 'mpos=',mpos,'raw predict:',raw_prediction_poslist[raw_ind]
                #pdb.set_trace()
                raw_ind += 1
            else:
                while mpos != raw_prediction_poslist[raw_ind][0]:
                    # find FP!
                    if FirstTime == False:
                        pFP['pos'].append(raw_prediction_poslist[raw_ind][0])
                        pFP['label'].append(raw_prediction_poslist[raw_ind][1])
                        pFP['recname'].append(recname)
                    raw_ind += 1
                FirstTime = False
                #print 'mpos=',mpos,'raw predict:',raw_prediction_poslist[raw_ind],'and raw_ind=',raw_ind
                #pdb.set_trace()
                raw_ind += 1
            # skip FP in large gap
            if mpos_ind+1<N_matched and matched_poslist[mpos_ind+1]-mpos>=skip_Thres:
                # skip False Positives inbetween,
                # because these FP canbe real characteristic point without expert label
                #print 'mpos = ',mpos
                #print 'next mpos = ',matched_poslist[mpos_ind+1]
                #print 'dist = ',matched_poslist[mpos_ind+1]-mpos
                #pdb.set_trace()
                FirstTime = True

        #print 'number of False Positive :{}'.format(len(pFP['pos']))
        #pdb.set_trace()
        return None
    def get_FalsePositive(self,reslist,pErr,pFP,recname):
        pass
        ExpertPos_ErrorList = zip(pErr['pos'],pErr['err'])
        matched_poslist = map(lambda x:x[0]+x[1],ExpertPos_ErrorList)
        #raw_prediction_poslist = map(lambda x:x[0],reslist)
        raw_prediction_poslist = reslist
        # sort two list
        matched_poslist.sort()
        raw_prediction_poslist.sort(key = lambda x:x[0])
        # find FP
        print 'number of False Positive :{}'.format(len(raw_prediction_poslist) - len(matched_poslist))
        pdb.set_trace()
        raw_ind = 0
        # Error !! what about FP after the matched_poslist[-1]?
        raise Exception('what about FP after the matched_poslist[-1]?')
        for mpos in matched_poslist:
            if mpos == raw_prediction_poslist[raw_ind][0]:
                raw_ind += 1
            else:
                while mpos != raw_prediction_poslist[raw_ind][0]:
                    # find FP!
                    pFP['pos'].append(raw_prediction_poslist[raw_ind][0])
                    pFP['label'].append(raw_prediction_poslist[raw_ind][1])
                    pFP['recname'].append(recname)
                    raw_ind += 1
                raw_ind += 1
        pdb.set_trace()
        return None
        
    def PlotMarkerList(self):
        return [
                'ro',
                'go',
                'bo',
                'r<',
                'r>',
                'g<',
                'g>',
                'b<',
                'b>',
                'w.']
    def Label2PlotMarker(self,label):
        if label == 'T':
            mker = 'ro'
        elif label == 'R':
            mker = 'go'
        elif label == 'P':
            mker = 'bo'
        elif label == 'Tonset':
            mker = 'r<'
        elif label == 'Toffset':
            mker = 'r>'
        elif label == 'Ronset':
            mker = 'g<'
        elif label == 'Roffset':
            mker = 'g>'
        elif label == 'Ponset':
            mker = 'b<'
        elif label == 'Poffset':
            mker = 'b>'
        else:# white
            mker = 'w.'
        return mker
    def plotresult(\
            self,\
            prdResult_rec,\
            figureID = 1,\
            showExpertLabel = False,\
            subplotID = None,\
            sig_input = None,\
            xLimtoLabelRange = True):
#
        # parameter check
        if len(prdResult_rec)!=2:
            raise StandardError('\
                    input prdRes must be of form\
                    (recname,recResult)!')
        ## plot signal waveform & labels
        recname,recRes = prdResult_rec

        # create figure & subplot
        plt.figure(figureID);
        if subplotID is not None:
            plt.subplot(subplotID)

        # load signal
        if sig_input is not None:
            sig = sig_input
        else:
            sig = self.QTloader.load(recname)

        rawsig = sig['sig']
        # plot sig 
        plt.plot(rawsig)
        # for xLim
        Label_xmin ,Label_xmax = recRes[0][0],recRes[0][0]
        plotmarkerlist = self.PlotMarkerList()
        PlotMarkerdict = {x:[] for x in plotmarkerlist}
        map(lambda x:PlotMarkerdict[self.Label2PlotMarker(x[1])].append((x[0],rawsig[x[0]])),recRes)

        # for prdpair in recRes:
            # label = prdpair[1]
            # pos = prdpair[0]
            # # for xLim
            # Label_xmin = min(Label_xmin,pos)
            # Label_xmax= max(Label_xmax,pos)

            # mker = 'kh'
            # mker = self.Label2PlotMarker(label)

        # for each maker
        for mker,posAmpList in PlotMarkerdict.iteritems():
            if len(posAmpList) ==0:
                continue
            poslist,Amplist = zip(*posAmpList)
            Label_xmin = min(Label_xmin,min(poslist))
            Label_xmax = max(Label_xmax ,max(poslist))
            plt.plot(poslist,Amplist,mker)
        # plot expert marks
        if showExpertLabel:
            # blend together
            explbpos = self.QTloader.getexpertlabeltuple(recname)
            explbpos = [x[0] for x in explbpos]
            explbAmp = [rawsig[x] for x in explbpos]
            # plot expert labels
            h_expertlabel = plt.plot(explbpos,explbAmp,'rx')
            # set plot properties
            plt.setp(h_expertlabel,'ms',12)
        if xLimtoLabelRange == True:
            plt.xlim(Label_xmin-100,Label_xmax+100)

        plt.title(recname)

    def plotevalresofrec(self,recname,ResultList):
        # Parameters:
        # ResultList:[[recname,recResult],...]
        #
        # --Purpose--
        # plot rec prediction result
        # plot expertlabel
        # plot eval relation line between expert label&prediction result
        #

        # load signal
        sig = self.QTloader.load(recname)
        # 1.subplot 1:raw prediction results
        rawRes = [x for x in ResultList if x[0] == recname]
        rawRes = rawRes[0]
        self.plotresult(rawRes,showExpertLabel = True,subplotID = 311,sig_input = sig)
        # 2.subplot2: filtered results
        fltRes = [x for x in self.fResultList if x[0] == recname]
        fltRes = fltRes[0]
        self.plotresult(fltRes,subplotID = 312,sig_input = sig)
        # 3.subplot3: relation between expertlabels & filtered results
        self.plotresult(fltRes,showExpertLabel = True,subplotID = 313,sig_input = sig)
        #find pErr&pFN,plot line and big circle for FN
        recFN = zip(\
                self.pFN['pos'],\
                self.pFN['label'],\
                self.pFN['recname']\
                )
        recErr = zip(\
                self.pErr['err'],\
                self.pErr['pos'],\
                self.pErr['label'],\
                self.pErr['recname']\
                )
        recFN = [x for x in recFN if x[2] == recname]
        recErr = [x for x in recErr if x[3] == recname]

        #print recErr
        #print '='*20,'recErr'
        #print recFN
        #print '='*20,'recFN'

        # plot line
        plt.figure(1)
        plt.subplot(313)
        for i in range(0,len(recErr)):
            epos = recErr[i][1]
            prdpos = epos + recErr[i][0]
            Amp_epos = sig['sig'][epos]
            Amp_prdpos = sig['sig'][prdpos]
            plt.plot([epos,prdpos],[Amp_epos,Amp_prdpos],'k',linewidth = 3.0)
        # plot FN
        for i in range(0,len(recFN)):
            epos = recFN[i][0]
            Amp_epos = sig['sig'][epos]
            h_FN = plt.plot(epos,Amp_epos,'kD')
            plt.setp(h_FN,'ms',12)
        
        recerrlist = [x[0] for x in recErr]
        plt.title('#FN = {},mean(Err) = {},stdvar(Err) = {}'.\
                format(\
                    len(recFN),\
                    np.nanmean(recerrlist),\
                    np.nanstd(recerrlist)\
                ))
        plt.show()


    @staticmethod 
    def pFN_analysis_to_log(\
            logfilename,\
            labellist,\
            pFN):

        # number of FN for each label
        #
        numofFN = dict()
        for label in labellist:
            cnt = len([x for x in pFN['label'] if x == label])
            numofFN[label] = cnt
        

        with open(logfilename,'a') as fout:
            fout.write('\n===FN Number for each label===\n')
            for label,num in numofFN.iteritems():
                fout.write('FN[{}] = {}\n'.format(label,num))
        return numofFN

    @staticmethod
    def pErr_analysis_to_log(\
            logfilename,\
            labellist,\
            pErr ,\
            debug_showErrhist = False):

        # number of FN for each label
        #
        numofErr = dict()
        labelErr = dict()
        errlabellist = zip(pErr['err'],pErr['label'])
        for label in labellist:
            labelErr[label] = [x[0] for x in errlabellist if x[1] == label]
            cnt = len(labelErr[label])
            numofErr[label] = cnt
            if debug_showErrhist == True:
                # hist of each label's error list
                plt.hist(labelErr[label])
                plt.title('{}''s Error Histogram'.format(label))
                plt.xlabel('Error(samples)')
                plt.show()
        

        with open(logfilename,'a') as fout:
            fout.write('\n===classificatio precision Number for each label===\n')
            for label,num in numofErr.iteritems():
                fout.write('Err[{}] = {}\n'.format(label,num))
        return numofErr

    def stat_record_analysis(self,pErr,pFN,LogFileName):
        # write record analysis to log file
        # inorder to find out which record is worst in accuracy
        #
        recnameset = set(pErr['recname'])
        recnameset |= set(pFN['recname'])
        recnamelist = [recname for recname in recnameset]
        # LabelList
        LabelList = [
                'P',
                'R',
                'T',
                'Ponset',
                'Poffset',
                'Ronset',
                'Roffset',
                'Toffset'
                ]
        # Err & FN
        ErrRec = {recname:{label:[] for label in LabelList} for recname in recnamelist}
        FNRec = {recname:{label:[] for label in LabelList} for recname in recnamelist}
        ## Now They are to the form ErrRec[recname][labelname]

        # get the stats
        errinfo = zip(pErr['err'],pErr['label'],pErr['recname'])
        fninfo = zip(pFN['pos'],pFN['label'],pFN['recname'])
        # assign to dict
        map(lambda x: ErrRec[x[2]][x[1]].append(x[0]), errinfo)
        map(lambda x: FNRec[x[2]][x[1]].append(x[0]), fninfo)

        # output stat to log
        ResultStatArray = []
        CSVTitles = ['Record Name',]
        #CSVTitles.extend(map(lambda x:'{} FN number'.format(x),LabelList))
        for clabel in LabelList:
            CSVTitles.append('{} mean error'.format(clabel))
            CSVTitles.append('{} std error'.format(clabel))
        # add csv title
        ResultStatArray.append(CSVTitles)
        with open(LogFileName,'a') as fout:
            for recname in recnameset:
                # for csv file,a row of record data
                curResultStat = [recname,]
                # get False Negtive number 
                #for csvlabel in LabelList:
                    #csvFN= len(FNRec[recname].get(csvlabel,[]))
                    #curResultStat.append(csvFN)
                for labelname in LabelList:
                    errs = ErrRec[recname][labelname]
                    meanval = np.nanmean(errs)*4.0 if len(errs)>0 else -1
                    stdval = np.nanstd(errs)*4.0 if len(errs)>0 else -1
                    curResultStat.append(meanval)
                    curResultStat.append(stdval)
                # to array
                ResultStatArray.append(curResultStat)

                fout.write(os.linesep+'Record[{}]'.format(recname)+'='*20+os.linesep)
                # if some label is totally overlooked
                overlook_label = {'P':1,'T':1,'R':1}
                # FNstat
                for labelname in LabelList:
                    # FN stat
                    numofFN = len(FNRec[recname][labelname])
                    fout.write('[#FN]{} = {}'.format(labelname,numofFN)+os.linesep)
                    # overlook
                    for tlabel in ['P','R','T']:
                        if tlabel in labelname:
                            if numofFN ==0 :
                                overlook_label[tlabel] =0
                # overlook check
                for tlabel,ov_mark in overlook_label.iteritems():
                    if ov_mark >0:
                        print '\n**recname [{}] label({}) is totally overlooked!!\n'.format(recname,tlabel)
                        
                # Err stat 
                for labelname in LabelList:
                    errs = ErrRec[recname][labelname]
                    meanval = np.nanmean(errs)*4.0 if len(errs)>0 else -1
                    stdval = np.nanstd(errs)*4.0 if len(errs)>0 else -1
                    fout.write('Err({}) mean({:03.2f} ms), std var({:03.2f} ms)'.format(labelname,meanval,stdval)+os.linesep)
        # write to csv file
        csvfilepath = os.path.join(os.path.dirname(LogFileName),'results.csv')
        from EvaluationSchemes.csvwriter import CSVwriter
        csvwriter = CSVwriter(csvfilepath)
        csvwriter.output(ResultStatArray)

        return ResultStatArray

    def FN2CSV(self,FN,Err,csv_output_filename):
        # [Se] = TP/(TP+FN)
        ResultStatArray = []
        # labels list
        labellist = [
                'P',
                'R',
                'T',
                'Ponset',
                'Poffset',
                'Ronset',
                'Roffset',
                'Toffset'
                ]
        # add title line
        title_line = ['Record Name',]
        for label in labellist:
            title_line.append(label+' FN')
        ResultStatArray.append(title_line)
        # dictionary of FN for each label
        FNdict = dict()
        TPdict = dict()
        recname_set = set()
        for label in labellist:
            FNdict[label] = []
            TPdict[label] = 0
        # total FN for each label
        totalFN_line = ['Total',]
        FNtuple = zip(FN['pos'],FN['label'],FN['recname'])
        for pos,label,recname in FNtuple:
            recname_set.add(recname)
            FNdict[label].append((pos,recname))
        for label in labellist:
            totalFN_line.append(len(FNdict[label]))
        ResultStatArray.append(totalFN_line)
        # get TP number for each label
        for label in Err['label']:
            TPdict[label] += 1
        # for False Negtive is Sensitivity
        PplusRate_line = ['Se value',]
        for label in labellist:
            TP_label = TPdict[label]
            FN_label = len(FNdict[label])
            PplusRate_line.append(float(TP_label)/(TP_label+FN_label))
        ResultStatArray.append(PplusRate_line)
        
        # for each recname
        for recname in recname_set:
            recname_line = [recname,]
            for label in labellist:
                FN_cnt = 0
                for pos,pos_recname in FNdict[label]:
                    if pos_recname == recname:
                        FN_cnt += 1
                recname_line.append(FN_cnt)
            ResultStatArray.append(recname_line)


        from EvaluationSchemes.csvwriter import CSVwriter
        csvwriter = CSVwriter(csv_output_filename)
        csvwriter.output(ResultStatArray)
    def FP2CSV(self,FP,Err,csv_output_filename):
        # [P+] = TP/(TP+FP)
        ResultStatArray = []
        # labels list
        labellist = [
                'P',
                'R',
                'T',
                'Ponset',
                'Poffset',
                'Ronset',
                'Roffset',
                'Toffset',
                'white'
                ]
        # add title line
        title_line = ['Record Name',]
        for label in labellist:
            title_line.append(label+' FP')
        ResultStatArray.append(title_line)
        # dictionary of FP for each label
        FPdict = dict()
        TPdict = dict()
        recname_set = set()
        for label in labellist:
            FPdict[label] = []
            TPdict[label] = 0
        # total FP for each label
        totalFP_line = ['Total',]
        FPtuple = zip(FP['pos'],FP['label'],FP['recname'])
        for pos,label,recname in FPtuple:
            recname_set.add(recname)
            FPdict[label].append((pos,recname))
        for label in labellist:
            totalFP_line.append(len(FPdict[label]))
        ResultStatArray.append(totalFP_line)
        # get TP number for each label
        for label in Err['label']:
            TPdict[label] += 1
        PplusRate_line = ['P+ value',]
        for label in labellist:
            TP_label = TPdict[label]
            FP_label = len(FPdict[label])
            if TP_label+FP_label ==0:
                Pp_val = 'nan'
            else:
                Pp_val = float(TP_label)/(TP_label+FP_label)
            PplusRate_line.append(Pp_val)
        ResultStatArray.append(PplusRate_line)
        
        # for each recname
        for recname in recname_set:
            recname_line = [recname,]
            for label in labellist:
                FP_cnt = 0
                for pos,pos_recname in FPdict[label]:
                    if pos_recname == recname:
                        FP_cnt += 1
                recname_line.append(FP_cnt)
            ResultStatArray.append(recname_line)


        from EvaluationSchemes.csvwriter import CSVwriter
        csvwriter = CSVwriter(csv_output_filename)
        csvwriter.output(ResultStatArray)
    @staticmethod
    def dispstat0(pFN = None ,pErr = None,LogFileName = None,LogText = None,OutputFolder = None):
        # =====================================================================
        # statistics: display statistics about the test result
        #           write output to log file
        # =====================================================================
        if pFN is None: 
            print 'Error:stat0**Please use eval() first**'
            return
        # error for each label
        labellist = [
                'P',
                'R',
                'T',
                'Ponset',
                'Poffset',
                'Ronset',
                'Roffset',
                'Toffset'
                ]
        errvec = zip(pErr['err'],pErr['label'])
        stats = []

        # get stats
        for label in labellist:
            Errs = [x[0] for x in errvec if x[1] == label]
            stats.append((np.nanmean(Errs),np.nanstd(Errs)))
        # Convert to ms
        #
        stats = [[x[0]*4.0,x[1]*4.0] for x in stats]
        ## format output mean&std for each label
        #
        print ('#False Negtive:{}'.format(len(pFN['pos'])))
        print 'labels:','   '.join([x if len(x)>1 else x+'    ' for x in labellist])
        print 'mean:   ',
        print '  '.join(map(lambda x:'{:.2f}ms'.format(x),[x[0] for x in stats]))
        print 'std var:',
        print '  '.join(map(lambda x:'{:03.2f}ms'.format(x),[x[1] for x in stats]))
        # CSE tolerance
        CSEtolerance = [
                0,
                0,
                0,
                3,
                3,
                2,
                3,
                7,
                ]
        # to ms
        CSEtolerance = [x*4.0 for x in CSEtolerance]
        print 'CSEtol: ',
        print '  '.join(map(lambda x:'{:.2f}ms'.format(x),CSEtolerance))
        print '-'*60
        # output to CSV file
        if OutputFolder is not None:
            csvMat = []
            mean_arr,std_arr = zip(*stats)

            label_line = [LogText,]
            label_line.extend(labellist)
            csvMat.append(label_line)
            # mean
            mean_line = ['mean error',]
            mean_line.extend(mean_arr)
            csvMat.append(mean_line)
            # std error
            std_line = ['standard error',]
            std_line.extend(std_arr)
            csvMat.append(std_line)

            # output 
            csv_output_filename = os.path.join(OutputFolder,'Total_Stats.csv'.format())
            csvwriter = CSVwriter(csv_output_filename)
            csvwriter.output(csvMat)
        # output to Log file
        if LogFileName is not None:
            with open(LogFileName,'w') as fout:
                # write additional text
                if LogText is not None:
                    fout.write(LogText+'\n')
                # stat log 
                fout.write('Total #False Negtive = {}\n\n'.format(len(pFN['pos'])))
                fout.write('-'*60+'\n')
                fout.write('  \t'+'\t'.join(labellist)+'\n')
                fout.write('mean:   ')
                fout.write('\t'.join(map(\
                        lambda x:'{:03.2f}ms'.format(x),\
                        [x[0] for x in stats]))+'\n')
                fout.write('std var:')
                fout.write('\t'.join(map(\
                        lambda x:'{:03.2f}ms'.format(x),\
                        [x[1] for x in stats]))+'\n')
                fout.write('CSEtol: ')
                fout.write('\t'.join(map(\
                        lambda x:'{:03.2f}ms'.format(x),\
                        CSEtolerance))+'\n')
            ## number analysis
            pFNstat = ECGstatistics.pFN_analysis_to_log(LogFileName,labellist,pFN)
            pErrstat = ECGstatistics.pErr_analysis_to_log(LogFileName,labellist,pErr,debug_showErrhist = False)
            # ==================
            # pFN percentage
            # ==================
            with open(LogFileName,'a') as fout:
                fout.write('\n==================False Negtive Percentage===================\n\n')
                falsenegtive_perc_list = []
                for label in labellist:
                    labelN_FN = pFNstat[label]
                    labelN_Err = pErrstat[label]
                    perc = 100.0*labelN_FN/float(labelN_FN+labelN_Err)
                    falsenegtive_perc_list.append((label,perc))

                    print 'percentage FN[{}] = {:.3f}%'.format(label,perc)
                    fout.write('FN%[{}] = {:.3f}%,'.format(label,perc))
                fout.write('\n---Positive Prediction Rate---\n')
                for label,perc in falsenegtive_perc_list:
                    fout.write('PD%[{}] = {:.3f}%,'.format(label,100 - perc))

        
        return (labellist,stats)
                


# user defined evaluation function
def evaluate_result_file(picklefilename):
    with open(picklefilename,'r') as fin:
        Results = pickle.load(fin)
    rfobj = ECGRF.ECGrf()
    fResults = rfobj.recfilter(Results)
    # show filtered results & raw results
    rfobj.plotres(Results)
    rfobj.plotres(fResults,figureID = 2,showExpertLabel = True)

    
    
                


if __name__ == '__main__':
    #clseval = ClsEval([['sel103',[]]])
    #clseval.eval()
    #clseval.dispstat0()
    evaluate_result_file(os.path.join(\
            os.path.dirname(curfilepath),\
            'ECGRF_prediction_output.txt')\
            )

