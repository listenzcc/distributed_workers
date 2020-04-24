close all
clear all
clc

tcpipClient = tcpip('localhost', 63365, 'NetworkRole', 'client')
set(tcpipClient,'InputBufferSize', 4500000)
set(tcpipClient,'Timeout', 30)

fopen(tcpipClient)
while (1)
    disp('Waiting...')
    while tcpipClient.BytesAvailable == 0
        a = 1;
    end
    data = fread(tcpipClient, tcpipClient.BytesAvailable, 'uint8');
    flushinput(tcpipClient)
    data = convertCharsToStrings(char(data));
    disp(data)
    if data == 'quit'
        break
    end
    if data == 'td'
        simulate_workload
%         for j = 1 : 5
%             pause(1)
%             disp('.')
%         end
%         testDialog
    end
end
fclose(tcpipClient)