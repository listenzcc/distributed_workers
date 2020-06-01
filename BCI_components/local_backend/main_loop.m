function main_loop()
% Main loop of BCI function

%% Disclare global vars
global TCPIP_Client
global dataServer

global STATE

global MAT_FILE_PATH
global MODEL_FILE_PATH

if TCPIP_Client.BytesAvailable == 0
    return
end

%% Get input data
raw = fread(TCPIP_Client, TCPIP_Client.BytesAvailable, 'uint8');
data = char(raw)';
disp('Got data:')
disp(data)

% Response to 'quit' as escape command
if strcmp(data, 'quit')
    matlab_client_stop
    return
end

% Response to '-' as send-back command
if data(1) == '-'
    fwrite(TCPIP_Client, data)
    return
end

% Easy control start
if strcmp(data, 'start')
    disp('Start collection.')
    dataServer.Open();
    return
end

% Easy control stop
if strcmp(data, 'stop')
    dataServer.Close();
    disp('Stop collection.')
    
    data = dataServer.GetBufferData;
    save data data
    
    matlab_client_stop
    
    return
end

%% Parse data into jsons
try
    jsons = strsplit(data, '}{');
    
    for j = 1:length(jsons)
        
        if jsons{j}(1) ~= '{'
            jsons{j} = ['{', jsons{j}];
        end
        
        if jsons{j}(end) ~= '}'
            jsons{j} = [jsons{j}, '}'];
        end
        
    end
    
catch
    lasterror
    disp('Data is not json, ignore')
    return
end

disp('Splitted data:')
disp(jsons)

%% Response to jsons
for idx = 1:length(jsons)
    json = jsons{idx};
    disp('-')
    disp('Working with json:')
    disp(json)
    
    % Decode json
    try
        json = jsondecode(char(json));
    catch
        lasterror
        disp('Not a json, ignore')
        continue
    end
    
    disp('Decoded json:')
    disp(json)
    
    % Just disp json if it is a reply
    if hasattr(json, 'mode') == 1
        if strcmp(json.mode, 'Reply')
            disp('Got simple reply:')
            disp(json)
            continue
        end
    end
    
    % Check if json has 'cmd' field
    try
        assert(hasattr(json, 'cmd') == 1)
    catch
        disp('Illegal cmd json, ignore')
        disp(json)
        continue
    end
    
    try
        switch json.cmd
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            case 'kaishicaiji'
                
                if strcmp(STATE, 'Busy')
                    disp('Stop offline collection')
                    dataServer.Close();
                    disp('Stop collection.')

                    data = dataServer.GetBufferData;
                    disp(['Saving on ', MAT_FILE_PATH])
                    save(MAT_FILE_PATH, 'data')

                    disp(MAT_FILE_PATH)

                    dataServer.ringBuffer.Reset;

                    dataServer.Close();
                    disp('The dataServer is closed.')

                    STATE = 'Idle'
                end
                
                broadcast('kaishicaiji')
                assert(strcmp(STATE, 'Idle'))
                
                disp('Start offline collection')
                MAT_FILE_PATH = json.mat_path
                MODEL_FILE_PATH = json.model_path
                disp('Start collection.')
                dataServer.Open();
                
                STATE = 'Busy'
                broadcast('kaishicaiji done.')
                
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            case 'jieshucaiji'
                broadcast('jieshucaiji')
                assert(strcmp(STATE, 'Busy'))
                
                disp('Stop offline collection')
                dataServer.Close();
                disp('Stop collection.')
                
                data = dataServer.GetBufferData;
                disp(['Saving on ', MAT_FILE_PATH])
                save(MAT_FILE_PATH, 'data')
                
                disp(MAT_FILE_PATH)
                
                dataServer.ringBuffer.Reset;
                
                dataServer.Close();
                disp('The dataServer is closed.')
                
                STATE = 'Idle'
                broadcast('jieshucaiji done')
                
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
            case 'jianmo'
                broadcast('jianmo')
                MAT_FILE_PATH = json.shujulujing
                MODEL_FILE_PATH = json.moxinglujing
                offlineData = load(MAT_FILE_PATH)
                
                % data = offlineData.data;
                % e = size(data, 2);
                % while data(end, e) ~= 0
                %     e = e - 1;
                % end
                % e = e + 1;
                % data = data(:, e:end);
                % size(data)
                % offlineData.data = data;
                % save offlineData offlineData

                [Output_acc, Max_line, filter, model_final, mean_temp_final, std_temp_final] = model_dry(offlineData);
                Output_acc
                
                save(MODEL_FILE_PATH, 'Max_line', 'filter', 'model_final', 'mean_temp_final', 'std_temp_final');
                
                fwrite(TCPIP_Client, jsonencode(struct(...
                    'mode', 'response', ...
                    'cmd', 'jianmo', ...
                    'zhunquelv', num2str(Output_acc), ...
                    'timestamp', num2str(posixtime(datetime('now'))))))
                
                broadcast('jianmo done')
                
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
            case 'query'
                broadcast('query')
                offlineModel = load(MODEL_FILE_PATH);
                
                [label_pre, Trigger] = process_online_dry_long(dataServer, offlineModel);
                disp('Predicted label is:')
                disp(label_pre)
                disp('Detected label is:')
                disp(Trigger)
                
                if isempty(label_pre)
                    disp('No valid label is predicted, use 0 instead')
                    label_pre = 0;
                end
                
                fwrite(TCPIP_Client, jsonencode(struct(...
                    'mode', 'response', ...
                    'cmd', 'query', ...
                    'gujibiaoqian', num2str(label_pre), ...
                    'timestamp', num2str(posixtime(datetime('now'))))))
                
                broadcast('query done')
        end
    catch
        lasterror
    end
    
end

end
