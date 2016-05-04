%% Analyse Error with human Labels & RF detector results
% ECG QT database
% 2015-11-16

clc;
clear
% close all;

%% Load Records
FolderPath_rf = 'F:\TU\心电\DNN\TreeBagger_windowedMethod\CP_Detector20151114\Results\tmp\';
FolderPath_human = 'F:\TU\心电\GUI_ECG_Marker\ECGMarkData\';
File_rf = [FolderPath_rf,'sel100.mat_T;wave.mat'];
File_human = [FolderPath_human,'sel100_humanMarks.mat'];

load(File_human);
% struct : humanMarks
% Field  : index     label

rf_data = load(File_rf);
% Field : sig prd_ind  tMark

%% find Min distance
fs = 250;
target_label = 'T';
ti=1;

%% nearest index,signed
IndErr = [];

for ti =1:length(humanMarks.index)
    if humanMarks.label(ti) ~= target_label
        continue;
    end
    
    [~,mi] = min(abs(rf_data.prd_ind-humanMarks.index(ti)));

    Min_Dist = (rf_data.prd_ind(mi) - humanMarks.index(ti));

    IndErr = [IndErr ; Min_Dist];
end




