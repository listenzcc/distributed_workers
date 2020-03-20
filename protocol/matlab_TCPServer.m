close all
clear all
clc


while true
    
t = tcpip('localhost', 63356, 'NetworkRole', 'server')

fopen(t)
    
data = fread(t, t.BytesAvailable);

disp(convertCharsToStrings(char(data)))

end