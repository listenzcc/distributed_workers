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
    logger.info(f'Client connection established at ({IP}: {PORT}).')
    return client


def listen():
    logger.info('Client starts listening.')
    while True:
        try:
            data = client.recv(BUF_SIZE)
            logger.info(f'Client received {data}')
            if data == b'':
                raise Exception('Empty received.')
        except:
            logger.info(f'Client connection lost.')
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


client = new_client()
t = threading.Thread(target=listen)
t.start()

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
            shutdown()
            try:
                client = new_client()
                t = threading.Thread(target=listen)
                t.start()
            except Exception:
                traceback.print_exc()
            continue

        # Send msg[2:] to server,
        # if there is a valid connection
        if msg.startswith('s '):
            msg = msg[2:]
            try:
                client.sendall(msg.encode())
                logger.info(f'Client send {msg}')
                time.sleep(0.5)
            except Exception:
                traceback.print_exc()
            continue

        # Shutdown current connection
        if msg == 'k':
            shutdown()
            continue

        # Quit
        if msg == 'q':
            shutdown()
            break

    input('Enter to escape.')
