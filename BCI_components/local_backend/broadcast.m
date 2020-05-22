function broadcast(messages)
if ~iscell(messages)
    messages = {messages};
end

disp(['------------------------------------------------', messages{1}])

disp(datetime)

if length(messages) > 1
    for j = 2 : length(messages)
        disp(messages{j})
    end
end

end