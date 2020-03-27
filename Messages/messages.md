# Message contract

## Roles

UI: User Interface or Main Controller.  
Controller: Controller of BCI backend.  
Display: Game display.

## Mode

Offline: Fixed time series process.  
Online: BCI process.

## General

所有通信参与者都可以定期互发心跳包。

心跳包

```json
{
  "mode": "keepalive",
  "timestamp": "1585297645.123"
}
```

## Offline

### From UI to Controller

开始采集

```json
{
  "mode": "offline",
  "cmd": "kaishicaiji",
  "subjectid": "name-001",
  "sessionid": "motion-001",
  "timestamp": "1585297645.123"
}
```

结束采集

```json
{
  "mode": "offline",
  "cmd": "jieshucaiji",
  "timestamp": "1585297645.123"
}
```

建模

```json
{
  "mode": "offline",
  "cmd": "jianmo",
  "shujulujing": "\\folder1\\folder2\\datafolder\\",
  "timestamp": "1585297645.123"
}
```

### From Controller to UI

模型准确率

```json
{
  "mode": "offline",
  "cmd": "zhunquelv",
  "moxinglujing": "\\folder1\\folder2\\modefile",
  "zhunquelv": "0.95",
  "timestamp": "1585297645.123"
}
```

## Online

### From UI to Controller

开始采集

```json
{
  "mode": "online",
  "cmd": "kaishicaiji",
  "moxinglujing": "\\folder1\\folder2\\modefile",
  "timestamp": "1585297645.123"
}
```

结束采集

```json
{
  "mode": "online",
  "cmd": "jieshucaiji",
  "timestamp": "1585297645.123"
}
```

## Reply

### Reply keep-alive package

```json
{
  "mode": "reply",
  "state": "keepalive",
  "timestamp": "1585297645.123"
}
```

### Reply other package

OK, means the package is received and parsed correctly.

```json
{
  "mode": "reply",
  "state": "OK",
  "timestamp": "1585297645.123"
}
```

ParseError, means the package is received but can not be parsed correctly.

```json
{
  "mode": "reply",
  "state": "ParseError",
  "timestamp": "1585297645.123"
}
```
