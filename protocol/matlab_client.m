close all
clear all
clc

tcpipClient = tcpip('localhost', 63356, 'NetworkRole', 'client')
set(tcpipClient,'InputBufferSize', 4500000)
set(tcpipClient,'Timeout', 30)

fopen(tcpipClient)
while (1)
    while tcpipClient.BytesAvailable == 0
        a = 1;
    end
    data = fread(tcpipClient, tcpipClient.BytesAvailable, 'uint8');
    flushinput(tcpipClient)
    data = convertCharsToStrings(char(data));
    disp(data)
    if data == 'q'
        break
    end
    if data == 'td'
        testDialog
    end
end
fclose(tcpipClient)