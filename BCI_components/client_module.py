""" TCP client for test. """
import local_profile
import socket
import time
import json
import os
import sys
import threading
import traceback

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa

from local_profile import IP, PORT, BUF_SIZE  # , logger

from logger import Logger
logger = Logger(name='UI_GAME-{}',
                filepath=os.path.join('UI_GAME-{}.log'.format(time.ctime()
                                                              .replace(' ', '-')
                                                              .replace(':', '-')))).logger

CurrentDirectory = os.path.dirname(os.path.abspath(__file__))


def new_client(role='--'):
    """ Start a new connection to server. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    client.connect((IP, PORT))
    name = client.getsockname()
    logger.info(
        f'Client {name} ({role}) connected to server {IP}: {PORT}.')
    return client


def listen(client):
    name = client.getsockname()
    logger.info(f'Client {name} starts listening.')
    while True:
        try:
            data = client.recv(BUF_SIZE)
            name = client.getsockname()
            logger.info(f'Client {name} received {data}')
            if data == b'':
                raise Exception('Empty received.')
        except:
            traceback.print_exc()
            shutdown(client)
            break
    logger.info('Client stopped listening.')


def shutdown(client, silent=True):
    try:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except:
        if not silent:
            traceback.print_exc()
        logger.debug('Error occurred when client shutdown. {}'.format(
            traceback.format_exc()
        ))
    finally:
        logger.info(f'Client shutdown.')
