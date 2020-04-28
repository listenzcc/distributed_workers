% Diary begins

% Setup diary path
mkdir Diaries
diary_path = fullfile('Diaries', sprintf('Diary %s.log', strrep(datestr(datetime), ':', '-')));

% Switch diary to on
diary(diary_path)

% Show variables
whos

% IP and PORT should be correct
IP
PORT
