
clear_timers


global dataServer
dataServer.Close();
disp('The dataServer is closed.')

global TCPIP_Client
fclose(TCPIP_Client);
disp('The client is closed.')