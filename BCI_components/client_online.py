""" TCP client for test. """
import os
import time
import json
import threading

from client import new_client, listen, shutdown, logger


client_UI = new_client()
client_GAME = new_client()
for c in [client_UI, client_GAME]:
    t = threading.Thread(target=listen, args=(c,))
    t.setDaemon(True)
    t.start()


def send(msg, client):
    if isinstance(msg, dict):
        msg = json.dumps(msg)
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
    client.sendall(msg)
    logger.info(f'Client sent {msg}')


if __name__ == '__main__':
    subjectID = 'Subject00'
    sessionID = f'motion00-{time.time()}'

    for _ in range(3):
        send(dict(mode='keepalive',
                  timestamp=time.time()),
             client_GAME)
        time.sleep(0.2)

    # Correct package, start online
    models = os.listdir(os.path.join('DataShop', subjectID, 'Model'))
    send(dict(mode='Online',
              cmd='kaishicaiji',
              shujulujingqianzhui=os.path.join(
                  'DataShop', subjectID, 'OnlineData', sessionID),
              moxinglujing=os.path.join(
                  'DataShop', subjectID, 'Model', models[0]),
              timestamp=time.time()),
         client_UI)
    time.sleep(0.5)

    # Correct package, query
    for j in range(5):
        send(dict(mode='Query',
                  chixushijian='3.0',
                  zhenshibiaoqian=f'{j % 2}',
                  timestamp=time.time()),
             client_GAME)
        time.sleep(0.5)

    # Correct package, stop online
    send(dict(mode='Online',
              cmd='jieshucaiji',
              timestamp=time.time()),
         client_UI)

    input('Enter to escape.')
