function [group1, group2] = parse_label(label, min_length)
if nargin < 2
    min_length = 0;
end
% Parse label by its value

% Regulation
if ~isrow(label)
    label = label';
end

assert(size(label, 1) == 1)

% Idx the label
label_idx = [label; 1:length(label)];

group1 = {};
group2 = {};

while 1
    
    % Label 1 detected
    if label_idx(1, 1) == 1
        % Measure block length
        for c = 1 : size(label_idx, 2)
            if label_idx(1, c) ~= 1
                c = c - 1;
                break
            end
        end
        % Only record long enough block
        if c >= min_length
            group1{length(group1)+1} = label_idx(:, 1:c);
        end
        label_idx(:, 1:c) = '';
    end
    
    % Save escape
    if size(label_idx, 2) == 0
        break
    end
    
    % Label 2 detected
    if label_idx(1, 1) == 2
        % Measure block length
        for c = 1 : size(label_idx, 2)
            if label_idx(1, c) ~= 2
                c = c - 1;
                break
            end
        end
        % Only record long enough block
        if c >= min_length
            group2{length(group1)+1} = label_idx(:, 1:c);
        end
        label_idx(:, 1:c) = '';
    end
    
    % Save escape
    if size(label_idx, 2) == 0
        break
    end
    
    % Invalid label detected
    label_idx(:, 1) = '';
    
    % Save escape
    if size(label_idx, 2) == 0
        break
    end
    
end

end