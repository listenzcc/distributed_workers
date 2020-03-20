# Protocol of Interface between UI and Controller

E-mail: listenzcc@mail.bnu.edu.cn

- [Protocol of Interface between UI and Controller](#protocol-of-interface-between-ui-and-controller)
  - [Definition](#definition)
  - [Communication](#communication)
  - [Socket Format](#socket-format)
  - [Runtime Errors](#runtime-errors)
  - [Example code](#example-code)
    - [Run demo test](#run-demo-test)
    - [Run UI test](#run-ui-test)

## Definition

UI: The User Interface software, who send TCP socket to TCP Server.

Controller: The backend workload controller, who maintain TCP Server.

IP and PORT: The IP address and PORT number of TCP Server.

## Communication

UI and Controller communicate through TCP socket.
The process is:

- Controller starts a TCP Server, listening at *IP:PORT*.
- The UI send TCP socket to TCP Server as [*Socket Format*](#socket-format).
- The TCP Server will reply b'OK' if the command is successfully operated.

## Socket Format

Socket content should be in bytes (UTF-8 encoding), using JSON format.

A legal socket content is something like

b'{mode="lixian", cmd="kaishicaiji", xiangxiangcishu=3, shiyanzuci=5, timestamp=1584664654.5274417}'

```python
# Setup dict
content = dict(
        mode="lixian",
        cmd="kaishicaiji",
        xiangxiangcishu=3,
        shiyanzuci=5,
        timestamp=time.time()
    )

# Dump dict into JSON and encode
bytes = json.dumps(content).encode()

# Send bytes
# See client.py for detail
```

All required socket content are in following table:

From client to server

| Mode | Command | Description | Parameters
| ---- | ------- | ----------- | ----------
| lixian | kaishicaiji | 离线-开始采集 | timestamp: 时间戳; xiangxiangcishu: 想象次数; shiyanzuci: 实验组次
| lixian | jieshucaiji | 离线-结束采集 | timestamp: 时间戳
| lixian | jieshuciji  | 离线-结束刺激 | timestamp: 时间戳
| lixian | jianmo      | 离线-建模     | timestamp: 时间戳; shujulujing: 数据路径
| zaixian | kaishicaiji | 在线-开始采集 | timestamp: 时间戳; xiangxiangcishu: 想象次数; zantingshijian: 暂停时间
| zaixian | jieshucaiji | 在线-结束采集 | timestamp: 时间戳
| zaixian | jieshuciji  | 在线-结束刺激 | timestamp: 时间戳

From server to client

| Mode | Command | Description | Parameters
| ---- | ------- | ----------- | ----------
| lixian | jianmo | 离线-建模 | timestamp: 时间戳; zhunquelv: 准确率

A legal socket content should contain mode as Mode, cmd as Command and para as Parameters as required.
No more, No less.

## Runtime Errors

We defined Runtime Errors as following

| Name | Comments |
| ---- | -------- |
| FileNotFoundError | File not found on given path
| ValueError | Incoming value can not be correctly parsed
| InterruptedError | Operation being interrupted
| BusyError | Operation failed because the resource is busy
| UnknownError | For errors that are not defined

The details of Runtime Errors can be found in [profile](./profile.py)

## Example code

The example codes in python are provided: [TCP Server](./server.py), [UI Sender](./client.py).

IP and PORT are set up in [Profile](./profile.py).

### Run demo test

Run python scripts as following:

- Setup IP and PORT in [Profile file](./profile.py)
- Start TCP Server by run *TCP Server*
- Run *UI Sender* to simulate socket communication
- You may see output of *TCP Server* like following, means Server has received all the information it will need in the project.
- The server will send accuracy to client for test.
- The server will send Runtime Errors for test.

    ```ruby
    [PASS] lixian-kaishicaiji: xiangxiangcishu=3  
    [PASS] lixian-kaishicaiji: shiyanzuci=5  
    [PASS] lixian-kaishicaiji: timestamp=1584663654.5134408  
    [PASS] lixian-jieshucaiji: timestamp=1584663654.5274417  
    [PASS] lixian-jieshuciji: timestamp=1584663654.5384455  
    [PASS] lixian-jianmo: shujulujing=[Path-to-Data]  
    [PASS] lixian-jianmo: timestamp=1584663654.5464418  
    [PASS] zaixian-kaishicaiji: xiangxiangcishu=10  
    [PASS] zaixian-kaishicaiji: zantingshijian=5  
    [PASS] zaixian-kaishicaiji: moxinglujing=[模型目录]  
    [PASS] zaixian-kaishicaiji: timestamp=1584663654.5604415  
    [PASS] zaixian-jieshucaiji: timestamp=1584663654.5754406  
    [PASS] zaixian-jieshuciji: timestamp=1584663654.591445
    ```

![Example figure](sample.png)

### Run UI test

If you want to test your UI for TCP communication, you have to start *TCP Server* first.

- Setup IP and PORT in [Profile file](./profile.py)
- Start TCP Server by run *TCP Server*
- Let UI send TCP socket
- The output of *TCP Server* should report if the received sockets are correct.
