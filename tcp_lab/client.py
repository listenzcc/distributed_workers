import socket
import time
import threading
import traceback
from profile import IP, PORT, BUF_SIZE
from logger import default_logger as logger


def new_client():
    """ Start a new connection to server. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    client.connect((IP, PORT))
    return client


client = new_client()

if __name__ == '__main__':
    """ Control interface. """
    while True:
        # Wait input
        msg = input('>> ')

        # If empty input received, continue
        if not msg:
            continue

        # Start connection to server
        if msg == 'c':
            try:
                client = new_client()
            except Exception:
                traceback.print_exc()
            continue

        # Send msg[2:] to server,
        # if there is a valid connection
        if msg.startswith('s '):
            msg = msg[2:]
            try:
                client.send(msg.encode())
                logger.info(f'Client send {msg}')
                time.sleep(0.5)
            except Exception:
                traceback.print_exc()
            continue

        # Shutdown current connection
        if msg == 'k':
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except Exception:
                traceback.print_exc()
            continue

        # Quit
        if msg == 'q':
            break

    input('Enter to escape.')
