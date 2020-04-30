% Settings
global MAT_FILE_PATH
global MODEL_FILE_PATH

offlineData = load(MAT_FILE_PATH)

data = offlineData.data;
e = size(data, 2);
while data(end, e) ~= 0
    e = e - 1;
end
data = data(:, 1:e);
size(data)
offlineData.data = data;

[Output_acc, Max_line, filter, model_final, mean_temp_final, std_temp_final] = model_dry(offlineData);

save(MODEL_FILE_PATH, 'Max_line', 'filter', 'model_final', 'mean_temp_final', 'std_temp_final');