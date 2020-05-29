function [label_pre,trigger]=process_online_dry_long(dataServer,offlineModel)
timeData = 4;
nPoints = timeData * dataServer.sampleRate;
timeStep = 0.2;
isTrigger = true; % is Sync or Async BCI system
data = dataServer.GetBufferData;
label_pre=[];
idxTrigger=[];
Trigger_occ=[];
trigger=[];
persistent Label_num
if isempty(Label_num)
    Label_num=1;
end
% persistent Trigger_occ;
if isTrigger
    % Synchronized BCI, process N seconds data after the trigger, N = timeData
    if ~isempty(find(data(end,:)>0,1))
        label=data(end,:);
        label_loc=find(diff(label)>0)+1;
        idxTrigger = label_loc(length(label_loc));
        trigger=label(idxTrigger);
        if size(data,2)-idxTrigger+1 >= nPoints &&  size(data,2)-idxTrigger+1 <= nPoints+300
            Trigger_occ(Label_num)=idxTrigger;
            Label_num=Label_num+1;
            if length(Trigger_occ)<2
                data_process=data(1:end-1,idxTrigger+1:idxTrigger+nPoints);
                label_pre=CSP_OnLine_dry(data_process,offlineModel,trigger);
                disp(['trigger=',num2str(trigger),'label_pre=',num2str(label_pre)] );
                %             [result, feature] = BCIAlgrithm(data(1:end-1,idxTrigger:idxTrigger+nPoints-1));
                %             disp(['result = ' num2str(result) ', feature = ' num2str(feature)]);

            end
        else
            Label_num=1;
%             disp(['数据长度小于4s'] );
        end
    else
        Label_num=1;
        disp(['未检测到标签'] );
    end
else
    % Asynchronized BCI, process the latest N seconds data every M seconds, N =
    % timeData, M = timeStep
    nUpdate = dataServer.ringBuffer.nUpdate;
    if nUpdate >= timeStep*dataServer.sampleRate
        [result, feature] = BCIAlgrithm(data(1:end-1,end-nPoints+1:end));
        disp(['result = ' num2str(result) ', feature = ' num2str(feature)]);
    end
end

end
