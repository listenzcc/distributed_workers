""" TCP client for test. """
import os
import sys
import time
import json
import threading

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa

from client_module import new_client, listen, logger, CurrentDirectory


client_UI = new_client(role='UI')
client_GAME = new_client(role='GAME')
for c in [client_UI, client_GAME]:
    t = threading.Thread(target=listen, args=(c,))
    t.setDaemon(True)
    t.start()


def send(msg, client):
    """Safe sending message using client

    Arguments:
        msg {object} -- Message to be send.
        client {object} -- Client to use.
    """
    if isinstance(msg, dict):
        msg = json.dumps(msg)
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
    client.sendall(msg)
    name = client.getsockname()
    logger.info(f'Client {name} sent {msg}')


if __name__ == '__main__':
    subjectID = 'Subject00'
    sessionID = f'motion00-{time.time()}'

    for _ in range(3):
        send(dict(mode='keepalive',
                  timestamp=time.time()),
             client_GAME)
        time.sleep(0.2)

    # Correct package, start online
    models = os.listdir(os.path.join(
        CurrentDirectory, 'DataShop', subjectID, 'Model'))
    send(dict(mode='Online',
              cmd='kaishicaiji',
              shujulujingqianzhui=os.path.join(
                  CurrentDirectory, 'DataShop', subjectID, 'OnlineData', sessionID),
              moxinglujing=os.path.join(
                  CurrentDirectory, 'DataShop', subjectID, 'Model', models[0]),
              timestamp=time.time()),
         client_UI)

    time.sleep(0.1)

    # Correct package, query
    # 2: Real motion
    # 1: Fake motion
    for j in range(10):
        send(dict(mode='Query',
                  chixushijian='3.0',
                  zhenshibiaoqian=f'{j % 2 + 1}',
                  timestamp=time.time()),
             client_GAME)
        time.sleep(5)

    # Correct package, stop online
    send(dict(mode='Online',
              cmd='jieshucaiji',
              timestamp=time.time()),
         client_UI)

    # # Wrong package, linked package
    # a = dict(mode='keepalive',
    #          timestamp=time.time())
    # bstr = json.dumps(a)
    # send(bstr+bstr,
    #      client_UI)

    input('Enter to escape.')
