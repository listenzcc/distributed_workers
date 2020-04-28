function send_keep_alive()
% Send KeepAlive package through TCPIP_Client

global TCPIP_Client

% Prepare package
s = struct('mode', 'keepalive',...
    'timestamp', num2str(posixtime(datetime('now'))));

% Send package
fwrite(TCPIP_Client, jsonencode(s))
end
