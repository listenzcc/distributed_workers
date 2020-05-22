function res = hasattr(stru, attr)
% Whether [stru] has attribute [attr]

% Get field names
names = fieldnames(stru);

% Check one-by-one
for j = 1 : length(names)
    name = names{j};
    if strcmp(name, attr)
        % Found one, return 1 and escape
        res = 1;
        return
    end
end

% Failed on finding one
res = 0;
return

end