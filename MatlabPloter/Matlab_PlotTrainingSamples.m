%% 
% Author:Pengfei Gao
% Purpose: Plot QTdb Samples Selection Result
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
plot(samples.P,sig(samples.P),'go','markerfacecolor','g'); 
Legend_Cell = [Legend_Cell,'P'];
plot(samples.T,sig(samples.T),'yo','markerfacecolor','y'); 
Legend_Cell = [Legend_Cell,'T'];
plot(samples.R,sig(samples.R),'bo','markerfacecolor','b'); 
Legend_Cell = [Legend_Cell,'R'];
plot(samples.Ronset,sig(samples.Ronset),'m<','markerfacecolor','m'); 
Legend_Cell = [Legend_Cell,'Ronset'];
plot(samples.white,sig(samples.white),'ko','markerfacecolor','w','markersize',10); 
Legend_Cell = [Legend_Cell,'white'];


legend(Legend_Cell);