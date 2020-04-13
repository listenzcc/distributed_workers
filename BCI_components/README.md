# BCI software V0.1

## Profile

The IP and PORT of TCP server has to be set properly in advance.

The settings is in [profile.py](./profile.py)

Default values are:

```python
IP = 'localhost'
PORT = 63365
```

## Start server

Run BCI.py will starts a TCP server.

```shell
python BCI.py
```

The TCP server will work as BCI hub for UI and GAME.
The log will be stored in [BCI.log](./BCI.log)

**Make sure it starts before UI and GAME try to connect with it.**

## Debug

Run debug.py will starts a DEBUG session.

```shell
python debug.py
```

The debug session will automatically do the following

1. The TCP server will start.
2. The UI simulator will start and perform OFFLINE experiment simulation.
3. When UI simulator is done, **press Enter**.
4. The UI and GAME simulators will start and perform OFFLINE experiment simulation.
5. The running detail can be found in [UI_GAME.log](UI_GAME.log).
