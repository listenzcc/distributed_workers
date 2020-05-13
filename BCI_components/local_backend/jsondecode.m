function out = jsondecode(str)

    splits = strsplit(str(2:end - 1), ',');

    out = struct();

    for zone = splits
        name_content = strsplit(zone{1}, '": "');
        name = clean(name_content{1});
        content = clean(name_content{2});
        eval(sprintf('out.%s = ''%s''; ', name, content))
    end

end

function out = clean(inp)
    out = inp;

    for c = ['"']
        out = strrep(out, c, '');
    end

end
