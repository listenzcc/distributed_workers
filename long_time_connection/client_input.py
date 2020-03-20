import socket
import time
import threading
from profile import IP, PORT, BUF_SIZE, logging

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
client.connect((IP, PORT))


def listen(client=client):
    while True:
        data = client.recv(BUF_SIZE)
        logging.debug(f'Client received {data}')


t = threading.Thread(target=listen)
t.start()

while True:
    s = input('>> ')
    if not s:
        continue
    client.send(f'{s}'.encode())
    logging.debug(f'Client sent {s}')
    time.sleep(1)

