function flabel=CSP_OnLine_dry(data,offlineModel,trigger)

Max_line = offlineModel.Max_line;
model = offlineModel.model_final;
mean_temp= offlineModel.mean_temp_final;
std_temp = offlineModel.std_temp_final;
result = offlineModel.filter;
% %% �����������4s�ģ���ȡ0.5s��3.5s��������
% lengthOfData = size(data,1);
% data = data(501:3500,:);

% data = data;
% %% ȥ������ĵ�����ʣ��32��
% a = ones(1,66);
% b= [1 2 3 4 5 6 7 9 11 13 14 15 23 24 32 33 34 42 43 44 45 47 49 51 52 53 54 58 59 60 62 64 65 66];
% a(b) = 0;
% m = find(a ==1);
% data=double(data(:,m));
% 
% data = data';

%% Ԥ��������ͨ�˲�
channelNum=24;
lpass=8;
hpass=30;
fs=300;
filterorder = 3;                   
filtercutoff = [2*lpass/fs 2*hpass/fs];  
[f_b, f_a] = butter(filterorder,filtercutoff);
for i=1:channelNum
    data2(i,:) = filtfilt(f_b,f_a,data(i,:));
end

% data2_mean=mean(data2,1);
% for i=1:24
%   data2(i,:)=data2(i,:)-data2_mean;
% end

data=data2;
data = data(:,0.5*fs+1:3.5*fs);
clear data2;
data_test=[];
%% ��ȡ����
% ����ѵ�����ݵõ����˲������Բ������ݽ���ת������ȡ����
for i=1:2 % i ���������
    for p=24:-1:(24-Max_line+1)% P���˲���������� 
        Z(25-p,:)=result(p,:,i)*data(:,:); %Z���˲������
        V(i,25-p)=var(Z(25-p,:)); %V���������
    end
end
[m,n]=size(V);
Vsum=sum(sum(V),2); 
for i=1:2
    for l=1:n
        f(1,l)=log(V(i,l)/Vsum); 
    end
    f1(1,[1:n]+n*(i-1))=f; 
end
feature = f1;
%% ������һ��
d=size(feature,2);
new_data=zeros(size(feature));

for i=1:d
    temp=feature(:,i);
    new_temp=(temp-mean_temp(i))/std_temp(i);
    new_data(:,i)=new_temp;
end
data_test=new_data;
%% ����
labelpre = svmpredict(trigger, data_test,model); %����

flabel = labelpre; %% ������
