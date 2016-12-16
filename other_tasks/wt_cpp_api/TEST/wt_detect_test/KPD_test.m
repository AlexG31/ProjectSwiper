%% Load MIT data and get DTCWT coefficients

addpath('/home/alex/code/matlab/KPD');

files = dir('./input_data/');
len_files = length(files);


%for ind = 1:len_files
    %name = files(ind).name;
    
    arg_fin = fopen('./input_data/matlab_args.txt','r')
    args = fgets(arg_fin)
    args = strsplit(args, '\n');
    args = args{1};
    fclose(arg_fin)

    mat_data = load(args);

    data_raw = mat_data.sig;
    DecLvl = 9;
    Num_Subbands = 1:9;
    fs = 360;

    S_rec = DTCWT(data_raw,DecLvl,Num_Subbands);
%     for ind = 1:10
%         subplot(10,1,ind)
%         plot(S_rec(ind,:))
%         title(['s_rec ', num2str(ind)])
%     end
    %WriteToTxt(S_rec(1, :));
    
    % L_sig �� The record is segmend into L_sig signal fragments, each of them contains 12s' ECG data
    L_sig = floor((length(data_raw) - 2 * fs)/(fs*10)); 
    
    L_overlap = 2*fs;
    QRS_Location=[];T_Location_raw=[];P_Location_raw=[];
    
    S_ref=sum(S_rec);
    
    for jj = 1 : L_sig
        
        if jj <= 20
            jj;
        end
        
        x_start = 1+(jj-1)*fs*10;
        x_stop = (jj-1)*fs*10 + fs*10 + L_overlap;
        l=length(x_start:x_stop);
        
        % ECG with wavelet sub-levels 1 to 8, is equal to high pass filter
        ECG_ori=sum( S_rec( 1:8, x_start:x_stop));
        
        % QRS_detector is used to detect qrs complex, whose energy is
        % concentrate at 10 - 50 Hz
        QRS_matrix = S_rec( 3:5, x_start:x_stop);
        QRS_detector =sum( abs(QRS_matrix));
        
        % QRS_detector is used to detect T and P wave, whose energy is
        % concentrate at 1 - 10 Hz
        T_matrix = S_rec(4:8, x_start:x_stop);        
        T_detector = sum((T_matrix));
        
        %  QRS complex detection algorithm
        [y_QRS x_QRS]   = QRS_detection( QRS_detector ,fs );
        
        % QRS_Location_cur contains all QRS locations detected this 12s' window
        % [error]
        %QRS_Location_cur = x_QRS+x_start;
        QRS_Location_cur = x_QRS+x_start - 1;

        % Return on jj = 1

        
        %  T and P wave detection       
        [ T_Location_cur , P_Location_cur] = T_detection( T_detector, fs ,x_QRS , x_start );
        
        
        % This part is gona to detect the repetitive detection in 2s'
        % overlap between two adjacent windows
        if jj == 1
            
            QRS_Location = [QRS_Location, QRS_Location_cur];
            
            if T_Location_cur(1) > 0
                T_Location_raw = [T_Location_raw, T_Location_cur];
            end
            if P_Location_cur(1) > 0
                P_Location_raw = [P_Location_raw,P_Location_cur];
            end
        else
            
            if QRS_Location_cur(1) - QRS_Location(end) > floor(fs/20)
                
                QRS_Location = [QRS_Location, QRS_Location_cur];
            else
                
                QRS_Location = [QRS_Location, QRS_Location_cur(2:end)];
            end
            
            if T_Location_cur(1) > 0
                if T_Location_cur(1) -T_Location_raw(end) > floor(fs/20)
                    
                    T_Location_raw = [T_Location_raw, T_Location_cur];
                else
                    
                    T_Location_raw = [T_Location_raw, T_Location_cur(2:end)];
                end
            end
            
            if P_Location_cur(1) > 0
                P_Location_raw = [P_Location_raw,P_Location_cur];
            end
            
        end
        
        
%             plot( ECG_ori , 'g' ); 
%             hold on; 
%             plot(QRS_Location_cur-x_start, ECG_ori(QRS_Location_cur-x_start),'r.');
%             plot(T_Location_cur-x_start, ECG_ori(T_Location_cur-x_start),'bo');
%             plot(P_Location_cur-x_start, ECG_ori(P_Location_cur-x_start),'ko'); 
%             hold off;
    end
    %plot(S_ref,'g'); hold on;  
    %plot(QRS_Location,S_ref(QRS_Location),'r.');
    %plot(T_Location_raw, S_ref(T_Location_raw), 'bo');
    %plot(P_Location_raw, S_ref(P_Location_raw), 'ro');
    %hold off;

    WriteToTxt(QRS_Location, 'QRS_Locations.dat')
