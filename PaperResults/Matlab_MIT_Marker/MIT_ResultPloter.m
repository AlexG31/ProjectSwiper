%% 
% Author:Pengfei Gao
% Purpose: Plot MITdb Result(R wave)
% Date: start:2016-5-2
%%


figure(1)
hold on
plot(MIT_rawsig)
title(recname)

% Marks
FalseMarkerSize = 10;
plot(FNlist,MIT_rawsig(FNlist),'kd','markerfacecolor','k','markersize',FalseMarkerSize)
plot(FPlist,MIT_rawsig(FPlist),'ks','markerfacecolor','k','markersize',FalseMarkerSize)


legend('ECG','FN','FP');