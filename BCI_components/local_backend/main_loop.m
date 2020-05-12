function main_loop()
% Main loop of BCI function

global TCPIP_Client
global dataServer

global STATE

global MAT_FILE_PATH
global MODEL_FILE_PATH

if TCPIP_Client.BytesAvailable == 0
    return
end

raw = fread(TCPIP_Client, TCPIP_Client.BytesAvailable, 'uint8');
data = convertCharsToStrings(char(raw))

% Response to 'quit' as escape command
if strcmp(data, 'quit')
    matlab_client_stop
    return
end

% Response to '-' as send-back command
if data.startsWith('-')
    fwrite(TCPIP_Client, data)
    return
end

% Easy control
if strcmp(data, 'start')
    disp('Start collection.')
    dataServer.Open();
    return
end

if strcmp(data, 'stop')
    dataServer.Close();
    disp('Stop collection.')
    
    data = dataServer.GetBufferData;
    save data data
    
    matlab_client_stop
    
    return
end

if strcmp(data, 'query')
    offlineModel = load('model.mat');
    [label_pre, Trigger] = process_online_dry_long(dataServer, offlineModel)
end

try
    jsons = strsplit(data, '}{');
    
    for j = 1 : length(jsons)
        if jsons{j}(1) ~= '{'
            jsons{j} = ['{', jsons{j}];
        end
        if jsons{j}(end) ~= '}'
            jsons{j} = [jsons{j}, '}'];
        end
    end
catch
    disp('Data is not json, ignore')
    return
end

for json = jsons
    try
        json = jsondecode(char(json));
    catch
        disp('Not a json, ignore')
        continue
    end
    
    % Start Collection
    try
        if strcmp(json.cmd, 'kaishicaiji')
            assert(strcmp(STATE, 'Idle'))
            
            disp('Start offline collection')
            MAT_FILE_PATH = json.mat_path
            MODEL_FILE_PATH = json.model_path
            disp('Start collection.')
            dataServer.Open();
            
            STATE = 'Busy'
        end
    catch
        disp('Not start collection, continue')
    end
    
    % Stop Collection
    try
        if strcmp(json.cmd, 'jieshucaiji')
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
        end
    catch
        disp('Not stop collection, continue')
    end
    
    % Build model
    try
        if strcmp(json.cmd, 'jianmo')
            MAT_FILE_PATH = json.shujulujing
            MODEL_FILE_PATH = json.moxinglujing
            offlineData = load(MAT_FILE_PATH)
            
            data = offlineData.data;
            e = size(data, 2);
            while data(end, e) ~= 0
                e = e - 1;
            end
            data = data(:, 1:e);
            size(data)
            offlineData.data = data;
            
            [Output_acc, Max_line, filter, model_final, mean_temp_final, std_temp_final] = model_dry(offlineData);
            Output_acc
            
            save(MODEL_FILE_PATH, 'Max_line', 'filter', 'model_final', 'mean_temp_final', 'std_temp_final');
            
            fwrite(TCPIP_Client, jsonencode(struct(...
                'mode', 'response',...
                'cmd', 'jianmo',...
                'zhunquelv', num2str(Output_acc),...
                'timestamp', num2str(posixtime(datetime('now'))))))
            
        end
    catch
        disp('No model building, continue')
        % keyboard
    end
    
    % Query
    try
        if strcmp(json.cmd, 'query')
            offlineModel = load(MODEL_FILE_PATH);
            
            datetime
            
            [label_pre, Trigger] = process_online_dry_long(dataServer, offlineModel)
            
            if isempty(label_pre)
                label_pre = 0
            end
            
            fwrite(TCPIP_Client, jsonencode(struct(...
                'mode', 'response',...
                'cmd', 'query',...
                'gujibiaoqian', num2str(label_pre),...
                'timestamp', num2str(posixtime(datetime('now'))))))
        end
    catch
        disp('Not query, continue')
    end
end

end






