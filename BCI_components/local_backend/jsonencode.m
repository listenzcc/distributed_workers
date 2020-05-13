function out = jsonencode(stru)

    stru;
    names = fieldnames(stru);

    out = '{';

    for j = 1:length(names)
        field = names{j};
        eval(sprintf('value = stru.%s;', field))
        out = sprintf('%s"%s":"%s",', out, field, value);
    end

    out(end) = '}';

end
