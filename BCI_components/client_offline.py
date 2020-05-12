""" TCP client for test. """
import os
import sys
import time
import json
import threading

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa

from client_module import new_client, listen, logger, CurrentDirectory

client = new_client()
t = threading.Thread(target=listen, args=(client,))
t.setDaemon(True)
t.start()


def send(msg, client=client):
    """Safe sending message use client

    Arguments:
        msg {object} -- Message to be send

    Keyword Arguments:
        client {client} -- TCP client (default: {client})
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
                  timestamp=time.time()))
        time.sleep(0.2)

    # # Wrong package, stop offline before start
    # send(dict(mode='Offline',
    #           cmd='jieshucaiji',
    #           timestamp=time.time()))
    # time.sleep(0.5)

    # Correct package, start offline
    send(dict(mode='Offline',
              cmd='kaishicaiji',
              shujulujingqianzhui=os.path.join(
                  CurrentDirectory, 'DataShop', subjectID, 'Data', sessionID),
              timestamp=time.time()))
    time.sleep(200)

    # # Wrong package, repeat start offline
    # send(dict(mode='Offline',
    #           cmd='kaishicaiji',
    #           shujulujingqianzhui=os.path.join(
    #               'DataShop', subjectID, 'Data', sessionID),
    #           timestamp=time.time()))
    # time.sleep(0.5)

    # Correct package, stop offline
    send(dict(mode='Offline',
              cmd='jieshucaiji',
              timestamp=time.time()))
    time.sleep(0.5)

    # Correct package, build model
    send(dict(mode='Offline',
              cmd='jianmo',
              shujulujing=os.path.join(
                  CurrentDirectory, 'DataShop', subjectID, 'Data', f'{sessionID}.mat'),
              moxinglujingqianzhui=os.path.join(
                  CurrentDirectory, 'DataShop', subjectID, 'Model', sessionID),
              timestamp=time.time()))
    time.sleep(1)

    input('Enter to escape.')
