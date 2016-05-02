%% 
% Author:Pengfei Gao
% Purpose: Plot RSWT detection result on QTdb
% Date: start:2016-5-2

%% load mat file
% clear
% clc
% matfilename = 'F:\Python\0502\sel104.mat';
% load(matfilename)
%% plot result
figure(1)
Legend_Cell = {};
plot(sig);
Legend_Cell = [Legend_Cell,'sig'];
hold on  
% Plot Result Labels
plot(P,sig(P),'go','markerfacecolor','g'); 
Legend_Cell = [Legend_Cell,'P'];
plot(T,sig(T),'yo','markerfacecolor','y');
Legend_Cell = [Legend_Cell,'T'];
plot(R,sig(R),'bo','markerfacecolor','b');
Legend_Cell = [Legend_Cell,'R'];
% plot(P,sig(P),'go','markerfacecolor','g');
% plot(P,sig(P),'go','markerfacecolor','g');
% plot(P,sig(P),'go','markerfacecolor','g');
% plot(P,sig(P),'go','markerfacecolor','g');

% Plot Expert labels
if exist('expert_P') == 1
    plot(expert_P,sig(expert_P),'kd','markerfacecolor','k'); 
    Legend_Cell = [Legend_Cell,'Expert P'];
end
plot(expert_T,sig(expert_T),'kd','markerfacecolor','b'); 
Legend_Cell = [Legend_Cell,'Expert T'];
plot(expert_R,sig(expert_R),'kd','markerfacecolor','r'); 
Legend_Cell = [Legend_Cell,'Expert R'];


legend(Legend_Cell);