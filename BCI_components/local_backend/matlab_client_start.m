
% Init TCP/IP client
global TCPIP_Client
TCPIP_Client = tcpip(IP, PORT, 'NetworkRole', 'client');
set(TCPIP_Client,'InputBufferSize', 4500000)
set(TCPIP_Client,'Timeout', 30)

% Open and init TCP/IP client
fopen(TCPIP_Client);
flushinput(TCPIP_Client)

% Setup and start KeepAliveTimer
KeepAliveTimer = timer(...
    'Name', 'KeepAliveTimer',...
    'Period', 10,...
    'TimerFcn', 'send_keep_alive',...
    'ErrorFcn', 'matlab_client_stop',...
    'ExecutionMode', 'fixedRate');
start(KeepAliveTimer)

% Setup and start MainLoopTimer
MainLoopTimer = timer(...
    'Name', 'MainLoopTimer',...
    'Period', 1,...
    'TimerFcn', 'main_loop',...
    'ErrorFcn', 'matlab_client_stop',...
    'ExecutionMode', 'fixedRate');
start(MainLoopTimer)

disp('The client is started.')

% % Main loop
% % Todo: change it into a timer
% while (1)
%     disp('Waiting...')
%     while TCPIP_Client.BytesAvailable == 0
%         a = 1;
%     end
%     data = fread(TCPIP_Client, TCPIP_Client.BytesAvailable, 'uint8');
%     data = convertCharsToStrings(char(data))
%     
%     if data.startsWith('-')
%         s = struct('mode', 'keepalive',...
%             'timestamp', num2str(posixtime(datetime('now'))));
%         fwrite(TCPIP_Client, jsonencode(s))
%     end
% 
%     if data == 'quit'
%         break
%     end
% end
% 
% % Clear known timers
% stop(KeepAliveTimer)
% delete(KeepAliveTimer)
% 
% % Close TCP/IP client
% fclose(TCPIP_Client)

