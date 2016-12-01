% Date : 2016-05-06
% Author: Pengfei Gao
% [Save FN images]
ECG_dataPath='F:\LabGit\ECG_RSWT\PaperResults\Matlab_MIT_Marker\ver1_0\MIT_result_data\';
filelist = dir(ECG_dataPath);
matlist = {};
for ind = 1:length(filelist)
    if filelist(ind).isdir == 1
        continue;
    end
    curext = strsplit(filelist(ind).name,'.');
    if length(curext) == 2 && strcmp(curext{2},'mat')==1
        matlist = [matlist,filelist(ind).name];
    end
end

%% Plot FN
for ind = 1:length(matlist)
    mit = load([ECG_dataPath,matlist{ind}]);
    % get 100,101,203...
    recID = strsplit(matlist{ind},'.');
    recID = recID{1};


    signal = mit.MIT_rawsig;
    FNlist = mit.FNlist;
    FilteredFN = [];
    %---------------------
    % keep in/keep out
    %---------------------
    KeepInFolder = 'F:\LabGit\ECG_RSWT\PaperResults\Matlab_MIT_Marker\ver1_0\MIT_keepin_Region\';
    KeepOutFolder = 'F:\LabGit\ECG_RSWT\PaperResults\Matlab_MIT_Marker\ver1_0\MIT_keepout_Region\';
    MarkFileName = [KeepInFolder,recID,'_humanMarks.mat'];
    if exist(MarkFileName)>0
        hMarks = load(MarkFileName);
        if numel(FNlist)>0
            for fni = 1:length(FNlist)
                fnpos = FNlist(fni);
                InRegionMark = 0;
                for RegionInd = 1:size(hMarks.region,1)
                    if fnpos>=hMarks.region(RegionInd,1)&&hMarks.region(RegionInd,2)>=fnpos
                        InRegionMark = 1;
                        break;
                    end
                end
                if InRegionMark == 1
                    FilteredFN = [FilteredFN;fnpos];
                end
            end
        end
    end

    % Keep Out
    MarkFileName = [KeepOutFolder,recID,'_humanMarks.mat'];
    if exist(MarkFileName)>0
        hMarks = load(MarkFileName);
        if numel(FNlist)>0
            for fni = 1:length(FNlist)
                fnpos = FNlist(fni);
                InRegionMark = 0;
                for RegionInd = 1:size(hMarks.region,1)
                    if fnpos>=hMarks.region(RegionInd,1)&&hMarks.region(RegionInd,2)>=fnpos
                        InRegionMark = 1;
                        break;
                    end
                end
                if InRegionMark == 0
                    FilteredFN = [FilteredFN;fnpos];
                end
            end
        end
    end


    FNlist = FilteredFN;
    if numel(FNlist) == 0
        continue;
    end
    %Plot
    % plot FN
    saveFN_path = 'F:\LabGit\ECG_RSWT\PaperResults\MITdb_R_Evaluation\FN_pic\';

    hfig = figure(1);
    clf(hfig);
    plot(signal);
    hold on
    title(['Record ',recID]);
    plot(FNlist,signal(FNlist),'ro');
    legend('ECG','False Negtive');
    Span = [-400,400];

    for FNi = 1:length(FNlist)
        fnpos = FNlist(FNi);
        xlim(Span+fnpos);
        saveas(hfig,[saveFN_path,recID,'_FNpos',num2str(fnpos),'.jpg']);
    end
end