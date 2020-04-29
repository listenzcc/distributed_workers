function [Output_acc, Max_line, filter,model_final, mean_temp_final, std_temp_final] = model_dry(offlineData)
% circBuff = load('C:\Users\NICA_BCI1\Desktop\test2\1_1_1_1\Data_MI1_20_Session1.txt');

%%% 输入circBuff Numtrial
circBuff = offlineData.data;

% circBuff = load('C:\Users\NICA_BCI1\Desktop\test3\20190412_XuelinMa_1_26\Data_MI1_10_Session6.txt');
data=circBuff(1:end-1,:);
label =circBuff(end,:);
% label_loc=find(label>0);
m1=find(diff(label)==1)+1;
m2=find(diff(label)==2)+1;
% label(m2)
% m1 = double(find(fix(label) ==1));%%%%找标签 left 位置
% m2 = double(find(fix(label) ==2));%%%%找标签 rest 位置
Numtrial = min(length(m1), length(m2));

% %% 去掉多余的导联，剩下32导
% a = ones(1,66);
% b= [1 2 3 4 5 6 7 9 11 13 14 15 23 24 32 33 34 42 43 44 45 47 49 51 52 53 54 58 59 60 62 64 65 66];
% a(b) = 0;
% m = find(a ==1);
% data=double(data(:,m));

%% lv bo
%CAR
% data_mean=mean(data,1);
% for i=1:24
%   data(i,:)=data(i,:)-data_mean;
% end

channelNum=24;
lpass=8;
hpass=30;
fs=300;
filterorder = 3;
%%
for i=1:Numtrial  %%%%这里要填trail的个数
    data1(:,:,i)=data(:,m1(i)+1:m1(i)+4*fs);  %% latency之后0-4s
    data2(:,:,i)=data(:,m2(i)+1:m2(i)+4*fs);  %% latency之后0-4s

    filtercutoff = [2*lpass/fs 2*hpass/fs];
    [f_b, f_a] = butter(filterorder,filtercutoff);
    
    for w=1:channelNum
        data1(w,:,i) = filtfilt(f_b,f_a,data1(w,:,i));
        data2(w,:,i) = filtfilt(f_b,f_a,data2(w,:,i));
    end
end

% car
% for tri=1:Numtrial 
% data1_mean=mean(data1(:,:,tri),1);
% for cha=1:24
%   data1(cha,:,tri)=data1(cha,:,tri)-data1_mean;
% end
% data2_mean=mean(data2(:,:,tri),1);
% for cha=1:24
%   data2(cha,:,tri)=data2(cha,:,tri)-data2_mean;
% end
% end

data1 = data1(:,0.5*fs+1:3.5*fs,:);
data2 = data2(:,0.5*fs+1:3.5*fs,:);
% 
% data1 = data1(:,1:5:end,:);
% data2 = data2(:,1:5:end,:);

% index1=find(label==1);
% index2=find(label==2);

data11(:,:,1:Numtrial)=data1;  % 每一类trials数目
data11(:,:,Numtrial +1:Numtrial *2)=data2;

label1(1:Numtrial,:)=1;
label1(Numtrial+1:Numtrial *2,:)=2;
index11=find(label1==1);
index21=find(label1==2);

Indices1 = crossvalind('Kfold',Numtrial ,5);   %十折交叉验证

for r=1:5
    
    test1=(Indices1==r);
    train1=~test1;
    test=[index11(test1,:);index21(test1,:)];
    train=[index11(train1,:);index21(train1,:)];
    label_train=label1(train,:);   %训练标签
    label_test=label1(test,:);     %测试标签
    
    MI_index{1}=index11(train1);
    MI_index{2}=index21(train1);       %训练样本
    
    for j=1:2
        index=MI_index{j};%选取1类
        x=length(index);
        for k=1:x               %k: 样本个数
            temp_data=data11(:,:,index(k));  %选取某一试次样本
            R(:,:,k)=(temp_data*temp_data')/trace(temp_data*temp_data');% 求协方差矩阵
        end
        R_m(:,:,j)=mean(R,3); %对某一类样本所有试次的协方差矩阵求平均
    end
    Rsum=sum(R_m,3);
    Rl_m=R_m(:,:,1); %代表第一类的平均协方差矩阵
    Rr_m=R_m(:,:,2); %代表第2类的平均协方差矩阵
    
    [EVecsum,EValsum] = eig(Rsum); %特征值分解
    %   W = sqrt(inv(EValsum)) * EVecsum';
    [EValsum,ind] = sort(diag(EValsum),'descend'); %按特征值降序排列
    EVecsum = EVecsum(:,ind);
    
    %   Find Whitening Transformation Matrix - Ramoser Equation (3)
    W = sqrt(inv(diag(EValsum))) * EVecsum'; %求解白化矩阵
    % W = sqrt(inv(EValsum)) * EVecsum';
    Yl = W * Rl_m * W'; %矩阵重构
    Yr = W * Rr_m * W';
    
    [Bl,Dl]=eig(Yl); %特征值分解
    [Br,Dr]=eig(Yr);
    Dsum=Dl+Dr;
    
    %sort ascending by default
    [Dl,ind] = sort(diag(Dl)); Bl = Bl(:,ind); %第一类特征向量矩阵
    %     result=Bl'*W;
    resultl=Bl'*W;  %第一类滤波器矩阵
    [Dr,ind] = sort(diag(Dr)); Br = Br(:,ind);
    resultr=Br'*W;
    result(:,:,1)=resultl;
    result(:,:,2)=resultr;
    
    %% 取前几个特征向量作为滤波器求出每一个样本的特征，需要看求解特征的理论公式
    clear V feature f1 Z
    for k=24:-1:20  % k：滤波器矩阵64行到55行取值
        % k=60;
        for j=1:Numtrial *2   % j：样本序列
            for i=1:2 % i ：类别序列
                for p=24:-1:k % P：滤波后矩阵序列
                    Z(25-p,:)=result(p,:,i)*data11(:,:,j); %Z：滤波后矩阵
                    V(i,25-p)=var(Z(25-p,:)); %V：方差矩阵
                end
            end
            [m,n]=size(V);
            Vsum=sum(sum(V),2);
            clear f
            for i=1:2
                for l=1:n
                    f(1,l)=log(V(i,l)/Vsum);
                end
                f1(1,[1:n]+n*(i-1))=f;
            end
            feature(j,:)=f1;
        end
        %% svm
        %归一化
        data111=feature;
        d=size(data111,2);
        mean_temp = [];
        std_temp = [];
        new_data = [];
        
        for i=1:d
            temp=data111(:,i);
            mean_temp(i)=mean(temp);
            std_temp(i)=std(temp);
            new_temp=(temp-mean_temp(i))/std_temp(i);
            new_data(:,i)=new_temp;
        end
        %
        norm_sample=new_data;
        data_train=norm_sample(train,:);
        data_test=norm_sample(test,:);
        
        model = svmtrain(label_train,data_train, '-t 0 -c 1'); %建立SVM模型
        
        [labelpre,accuracy,dec]=svmpredict(label_test, data_test,model); %测试
        acc(r,25-k)=accuracy(1,1); %正确率
        Model{r,25-k}=model;
        Feature{r,25-k}=feature;
        M_temp{r,25-k}=mean_temp;
        S_temp{r,25-k}=std_temp;
        Result(:,:,:,r)=result;
        % acc(r)=accuracy(1,1);
        clear accuracy new_data feature v
    end
end
Acc_mean=mean(acc,1);
Acc_mean2=mean(acc,2);
Max_line=find(Acc_mean == max(Acc_mean));
qs=acc(:,Max_line(1));
Max_line=Max_line(1);
Output_acc=mean(qs);%%%%%
% Max_acc_pos=find(qs ==max(qs));
Max_acc_pos=find(Acc_mean2 ==max(Acc_mean2));
% Output_acc=max(qs);%%%%%
Output_acc=max(acc(Max_acc_pos(1),Max_line(1)));
% feature_final=Feature{Max_acc_pos(1),Max_line(1)};
model_final=Model{Max_acc_pos(1),Max_line(1)};
mean_temp_final=M_temp{Max_acc_pos(1),Max_line(1)};
std_temp_final=S_temp{Max_acc_pos(1),Max_line(1)};
filter=Result(:,:,:,Max_line(1));
% filter=result;

% save('mxl_model.mat', 'Max_line','result', 'model', 'mean_temp', 'std_temp')
