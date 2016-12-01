%% Training Samples Analysis
% Author: Pengfei Gao
% Date : 2016-05-13
%-------------

TrainingSampleFolder = 'F:\LabGit\ECG_RSWT\TestResult\pc\A_12\TrainingSamples\';
QTdbFolder = 'F:\TU\ÐÄµç\QTDatabase\Matlab\matdata_processed\';
filelist_trainingsamples = dir(TrainingSampleFolder);
for ind = 1:length(filelist_trainingsamples)
    if filelist_trainingsamples(ind).isdir == 1
        continue
    end
    filename = filelist_trainingsamples(ind).name;
    filename_elem = strsplit(filename,'.');
    extension = filename_elem{2};
    recordname = filename_elem{1};
    if strcmp(extension,'mat') == 0
        continue;
    end
    % file name is like 'sel30.mat'
    Samples = load([TrainingSampleFolder,filename]);
    QTdata = load([QTdbFolder,recordname,'.mat']);
    sig = QTdata.sig(1,:);
    fieldlist_samples = fieldnames(Samples);
    PositiveSamples = [];
    for field_i = 1:length(fieldlist_samples)
        if strcmp(fieldlist_samples{field_i},'white') == 1
            continue;
        end
        marklist = getfield(Samples,fieldlist_samples{field_i});
        if size(marklist,1)>size(marklist,2)
            marklist = transpose(marklist);
        end
        PositiveSamples = [PositiveSamples marklist];
    end
    figure(1)
    plot(sig);
    hold on;
%     plot(Samples.R,sig(Samples.R),'ro');
    plot(PositiveSamples,sig(PositiveSamples),'ro');
    plot(Samples.white,sig(Samples.white),'kd');
    
    T_mark = QTdata.markercell{1,3};
    plot(T_mark,sig(T_mark),'k.');
    legend('ECG','Positive Samples','white mark');
    title(['QTdb Record ',recordname]);
    
end


% 
% function Plot_Selected_Samples(sig,Samples)
%     figure(1)
%     plot(sig)
% 
% end