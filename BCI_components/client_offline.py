""" TCP client for test. """
import os
import time
import json
import threading
from profile import logger

from client import new_client, listen, shutdown


client = new_client()
t = threading.Thread(target=listen, args=(client,))
t.setDaemon(True)
t.start()


def send(msg, client=client):
    if isinstance(msg, dict):
        msg = json.dumps(msg)
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
    client.sendall(msg)
    logger.info(f'Client sent {msg}')


if __name__ == '__main__':
    for _ in range(3):
        send(dict(mode='keepalive',
                  timestamp=time.time()))
        time.sleep(0.2)

    # Wrong package, stop offline before start
    send(dict(mode='Offline',
              cmd='jieshucaiji',
              timestamp=time.time()))
    time.sleep(0.5)

    # Correct package, start offline
    send(dict(mode='Offline',
              cmd='kaishicaiji',
              shujulujingqianzhui=os.path.join(
                  'DataShop', 'Subject01', 'Data', str(time.time())),
              timestamp=time.time()))
    time.sleep(0.5)

    # Wrong package, repeat start offline
    send(dict(mode='Offline',
              cmd='kaishicaiji',
              shujulujingqianzhui=os.path.join(
                  'DataShop', 'Subject01', 'Data', str(time.time())),
              timestamp=time.time()))
    time.sleep(0.5)

    # Correct package, stop offline
    send(dict(mode='Offline',
              cmd='jieshucaiji',
              timestamp=time.time()))
    time.sleep(0.5)

    # Correct package, build model
    send(dict(mode='Offline',
              cmd='jianmo',
              shujulujing=os.path.join('DataShop', 'Subject01', 'Data'),
              moxinglujingqianzhui=os.path.join(
                  'DataShop', 'Subject01', 'Model', str(time.time())),
              timestamp=time.time()))
    time.sleep(0.5)

    input('Enter to escape.')
