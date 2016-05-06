function varargout = ECG_MarkerV1_0(varargin)
% ECG_MARKERV1_0 MATLAB code for ECG_MarkerV1_0.fig
%      ECG_MARKERV1_0, by itself, creates a new ECG_MARKERV1_0 or raises the existing
%      singleton*.
%
%      H = ECG_MARKERV1_0 returns the handle to a new ECG_MARKERV1_0 or the handle to
%      the existing singleton*.
%
%      ECG_MARKERV1_0('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in ECG_MARKERV1_0.M with the given input arguments.
%
%      ECG_MARKERV1_0('Property','Value',...) creates a new ECG_MARKERV1_0 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before ECG_MarkerV1_0_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to ECG_MarkerV1_0_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help ECG_MarkerV1_0

% Last Modified by GUIDE v2.5 04-May-2016 13:07:32

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @ECG_MarkerV1_0_OpeningFcn, ...
                   'gui_OutputFcn',  @ECG_MarkerV1_0_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

% --- Executes just before ECG_MarkerV1_0 is made visible.
function ECG_MarkerV1_0_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to ECG_MarkerV1_0 (see VARARGIN)

% Choose default command line output for ECG_MarkerV1_0
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% This sets up the initial plot - only do when we are invisible
% so window can get raised using ECG_MarkerV1_0.
if strcmp(get(hObject,'Visible'),'off')
    global signal ;
    signal = rand(5);
    plot(signal);
end

% UIWAIT makes ECG_MarkerV1_0 wait for user response (see UIRESUME)
% uiwait(handles.figure1);

%% Key Parameters
global ECG_dataPath;
ECG_dataPath='F:\LabGit\ECG_RSWT\PaperResults\Matlab_MIT_Marker\ver1_0\MIT_result_data\';
global curMarkInd;
curMarkInd = -1;
global humanMarks;

global curHumanMarkerinFigure;
curHumanMarkerinFigure = [];
global curRegion;
curRegion = [-1,-1];

% --- Outputs from this function are returned to the command line.
function varargout = ECG_MarkerV1_0_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;

% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
axes(handles.axes1);
cla;

global signal ;


popup_sel_index = get(handles.popupmenu1, 'Value');
switch popup_sel_index
    case 1
        signal = rand(5);
        plot(signal);
    case 2
        plot(sin(1:0.01:25.99));
    case 3
        bar(1:.5:10);
    case 4
        plot(membrane);
    case 5
        surf(peaks);
end


% --------------------------------------------------------------------
function FileMenu_Callback(hObject, eventdata, handles)
% hObject    handle to FileMenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function OpenMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to OpenMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
file = uigetfile('*.fig');
if ~isequal(file, 0)
    open(file);
end

% --------------------------------------------------------------------
function PrintMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to PrintMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
printdlg(handles.figure1)

% --------------------------------------------------------------------
function CloseMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to CloseMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selection = questdlg(['Close ' get(handles.figure1,'Name') '?'],...
                     ['Close ' get(handles.figure1,'Name') '...'],...
                     'Yes','No','Yes');
if strcmp(selection,'No')
    return;
end

delete(handles.figure1)


% --- Executes on selection change in popupmenu1.
function popupmenu1_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns popupmenu1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu1


% --- Executes during object creation, after setting all properties.
function popupmenu1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
     set(hObject,'BackgroundColor','white');
end

set(hObject, 'String', {'plot(rand(5))', 'plot(sin(1:0.01:25))', 'bar(1:.5:10)', 'plot(membrane)', 'surf(peaks)'});


% --- Executes on button press in pushbutton_Ginput.
function pushbutton_Ginput_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_Ginput (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


[x,y] = ginput(1);
% msgbox(['X = ',num2str(x),'Y = ',num2str(y)]);

%% set visible
global curRegion;
if curRegion(1) == -1
    set(handles.pushbutton_confirm1,'visible','on');
else
    set(handles.pushbutton_confirm2,'visible','on');
end
% set(handles.pushbutton_save_region,'visible','on');

%% Mark corresponding points in the curve

global signal;
global sig;
%global time;
global curHumanMarkerinFigure;
% x_index = 1:length(signal);
%[~,mi] = min(abs(time-x));
mi = int32(x);

%% clear former humanMarker and plot a new one
if numel(curHumanMarkerinFigure) ~=0
    curHumanMarkerinFigure.delete();
    curHumanMarkerinFigure = [];
end

axes(handles.axes1);
hold on;
curHumanMarkerinFigure = plot(mi,sig(mi),'ro');

global curMarkInd;
curMarkInd = mi;

% --- Executes on button press in pushbutton_zoom.
function pushbutton_zoom_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_zoom (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

zoom ;


% --- Executes on button press in pushbutton4.
function pushbutton4_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% set button visibility
set(handles.pushbutton_showECG,'visible','on');
set(handles.pushbutton1,'visible','off');

global ECG_dataPath;
QT_files = dir(ECG_dataPath);

FileListCell=[];



for ind = 3:length(QT_files)

        %% Get Correct Filename
        FileName = QT_files(ind).name;
        if numel(strfind(FileName,'.mat')) ==0
            continue;
        end
        %% 载入波形数据：
        % Include 'time','sig','marks'
        % FileName = 'sel33.mat';
        FileListCell = [FileListCell,{FileName}];
        
        
end

%% add to menu

set(handles.popupmenu1,'string',FileListCell);


% --- Executes on button press in pushbutton_showECG.
function pushbutton_showECG_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_showECG (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

%% get FileName

FileInd = get(handles.popupmenu1,'Value');
FileStr = get(handles.popupmenu1,'string');
FileName = cell2mat(FileStr(FileInd));
FileName_pure = strsplit(FileName,'.mat');
FileName_pure = cell2mat(FileName_pure(1));
%--
% FileName_pure is like 'sel102'
%--

%% Plot 
global ECG_dataPath;
%global time;
global sig;
global markFileName;
global humanMarks;

humanMarks = [];
% FP&FN marker size
FalseMarkerSize = 10;

%% load MITdb record
mit = load([ECG_dataPath,FileName]);
sig = mit.MIT_rawsig;
% now:----
%    time/sig/marks
%    ----

axes(handles.axes1);
hold off;

plot(sig);
grid on;
title(['False Negtive & False Positive of ',mit.recname]);
% Plot False Negtives&False Positives
hold on;
plot(mit.FPlist,sig(mit.FPlist),'ks','markerfacecolor','r','markersize',FalseMarkerSize)
plot(mit.FNlist,sig(mit.FNlist),'kd','markerfacecolor','k','markersize',FalseMarkerSize)

%% Load Marks
MarkFilePath = 'F:\LabGit\ECG_RSWT\PaperResults\Matlab_MIT_Marker\ver1_0\MIT_keepin_Region\';
markFileName = [MarkFilePath,FileName_pure,'_humanMarks.mat'];

%% struct humanMarks
% 
% humanMarks . index
% humanMarks . label

% File exist in the path
if exist(markFileName) ==2
    old_mks = load(markFileName);
    if isfield(old_mks,'region') >0
        humanMarks = old_mks.region;
        hold on;
        % plot T marks
        for ind =1:size(old_mks.region,1)
            marked_range = old_mks.region(ind,1):old_mks.region(ind,2);
            plot(marked_range,sig(marked_range),'r.','MarkerFaceColor','y');
        end
        hold off;
    end
end

% --- Executes on selection change in popupmenu_tag.
function popupmenu_tag_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu_tag (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu_tag contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu_tag


% --- Executes during object creation, after setting all properties.
function popupmenu_tag_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu_tag (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_confirm1.
function pushbutton_confirm1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_confirm1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

global curMarkInd;
global humanMarks;
global curRegion;

curRegion(1) = curMarkInd;

set(hObject,'visible','off');
% set(handles.pushbutton_confirm2,'visible','on');
% set marker visible = off
global curHumanMarkerinFigure;
if numel(curHumanMarkerinFigure) ~=0
    curHumanMarkerinFigure.delete();
    curHumanMarkerinFigure = [];
end

% call ginput
pushbutton_Ginput_Callback(handles.pushbutton_Ginput,[],handles);

% --- Executes on button press in pushbutton_save_region.
function pushbutton_save_region_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_save_region (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


global humanMarks;
global markFileName;

region = humanMarks;
save(markFileName,'region');
set(hObject,'visible','off');



function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit1 as text
%        str2double(get(hObject,'String')) returns contents of edit1 as a double


% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit2_Callback(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit2 as text
%        str2double(get(hObject,'String')) returns contents of edit2 as a double


% --- Executes during object creation, after setting all properties.
function edit2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_confirm2.
function pushbutton_confirm2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_confirm2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

global curHumanMarkerinFigure;
if numel(curHumanMarkerinFigure) == 0
    return
end
global curMarkInd;
global humanMarks;
global curRegion;

curRegion(2) = curMarkInd;
% swap if nessasary
if curRegion(1)>curRegion(2)
    tmp = curRegion(2);
    curRegion(2) = curRegion(1);
    curRegion(1) = tmp;
end
humanMarks = [humanMarks;curRegion];


% Plot marked Region
global sig;
axes(handles.axes1);
hold on;
cur_range = curRegion(1):curRegion(2);
marked_range = plot(cur_range,sig(cur_range),'r.');

set(hObject,'visible','off');
set(handles.pushbutton_save_region,'visible','on');
% init
curRegion = [-1,-1];
