function main_loop()
% Main loop of BCI function

global TCPIP_Client

if TCPIP_Client.BytesAvailable == 0
    return
end

data = fread(TCPIP_Client, TCPIP_Client.BytesAvailable, 'uint8');
data = convertCharsToStrings(char(data))

if data.startsWith('-')
    s = struct('mode', 'keepalive',...
        'timestamp', num2str(posixtime(datetime('now'))));
    fwrite(TCPIP_Client, jsonencode(s))
    nonono
end

if data == 'quit'
    matlab_client_stop
end

end