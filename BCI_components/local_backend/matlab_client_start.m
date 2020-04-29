% Init dataServer
global dataServer
device = 'DSI-24';
nChan = 25;
sampleRate = 300; % sampling rate of the device
bufferSize = 600; % buffer size in seconds
dataServer = DataServer(device, IP_EEG_DEVICE, PORT_EEG_DEVICE, nChan, sampleRate, bufferSize);
disp('The dataServer is started.')

% Init controllers
global IS_COLLECTING
IS_COLLECTING = false;

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
    'ExecutionMode', 'fixedRate',...
    'BusyMode', 'queue');
start(KeepAliveTimer)

% Setup and start MainLoopTimer
MainLoopTimer = timer(...
    'Name', 'MainLoopTimer',...
    'Period', 0.1,...
    'TimerFcn', 'main_loop',...
    'ErrorFcn', 'matlab_client_stop',...
    'ExecutionMode', 'fixedRate',...
    'BusyMode', 'queue');
start(MainLoopTimer)

disp('The client is started.')

