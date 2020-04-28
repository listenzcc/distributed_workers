% Close and clear all the timers

% All current timers
timers = timerfindall

% Stop and delete timer one-by-one
for t = timers
    stop(t)
    delete(t)
end

% Timers should be empty
timers = timerfindall