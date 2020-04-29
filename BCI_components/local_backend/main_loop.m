function main_loop()
% Main loop of BCI function

global TCPIP_Client
global dataServer

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
        if jsons{j}(1) == '{'
            jsons{j} = ['{', jsons{j}];
        end
        if ~jsons{j}(end) == '}'
            jsons{j} = [jsons{j}, '}'];
        end
    end
catch
    disp('Data is not json, ignore')
    return
end

jsons

for json = jsons
    try
        if strcmp(json.mode, 'offline') && strcmp(json.mode, 'kaishicaiji')
            disp('Start offline collection')
        end
    catch
        disp('Not offline collection, continue')
    end
end

end






