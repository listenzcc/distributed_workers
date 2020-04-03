""" TCP client for test. """
import os
import time
import json
import threading

from client import new_client, listen, shutdown, logger

client = new_client()
t = threading.Thread(target=listen)
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

    # Correct package, start online
    send(dict(mode='Online',
              cmd='kaishicaiji',
              moxinglujing=os.path.join('DataShop', 'Subject01', 'Model', 'whatevermodel')))
    time.sleep(0.5)

    # Correct package, query

    input('Enter to escape.')
