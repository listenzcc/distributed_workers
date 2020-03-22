import time
import socket
import threading
import traceback
from profile import IP, PORT, BUF_SIZE
from logger import default_logger as logger

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(1)


def accept_client():
    logger.info('Server starts listening.')
    client, address = server.accept()
    logger.info(f'Connection established at {address}')
    return client


client = accept_client()

while True:
    try:
        data = client.recv(BUF_SIZE)
        if data == b'':
            raise Exception('Empty received.')
        logger.info(f'Server received {data}')
    except Exception:
        traceback.print_exc()
        client = accept_client()

if __name__ == '__main__':
    input('Enter to escape.')
