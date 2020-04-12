""" TCP client for test. """
import socket
import time
import json
import os
import threading
import traceback
from profile import IP, PORT, BUF_SIZE
from logger import Logger

logger = Logger(name='UI_GAME', filepath=os.path.join('UI_GAME.log')).logger


def new_client():
    """ Start a new connection to server. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    client.connect((IP, PORT))
    logger.info(f'Client connection established at {IP}: {PORT}.')
    return client


def listen(client):
    logger.info('Client starts listening.')
    while True:
        try:
            data = client.recv(BUF_SIZE)
            logger.info(f'Client received {data}')
            if data == b'':
                raise Exception('Empty received.')
        except:
            traceback.print_exc()
            shutdown()
            break
    logger.info('Client stopped listening.')


def shutdown(silent=True):
    try:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except:
        if not silent:
            traceback.print_exc()
