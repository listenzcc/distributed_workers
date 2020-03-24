import time
import json
import socket
import threading
from check_table import CheckTable
from profile import IP, PORT, BUF_SIZE, RuntimeErrors, Responses, logging

ct = CheckTable()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(1)
client, address = server.accept()
logging.debug(f'Connection established at {address}')


def send(msg, client=client, delay=1):
    if isinstance(msg, dict):
        msg = json.dumps(msg).encode()
    client.send(msg)
    logging.debug(f'Server send {msg}')
    time.sleep(delay)


def listen(client=client):
    while True:
        data = client.recv(BUF_SIZE)
        logging.debug(f'Server received {data}')
        if ct.add(json.loads(data)) == 0:
            # Response 'OK' if received data is legal.
            resp = Responses['OKResponse']
            resp['repeat'] = data.decode()
            send(resp, delay=0)
        else:
            # Response 'Fail' if received data is illegal.
            resp = Responses['FailResponse']
            resp['repeat'] = data.decode()
            send(resp, delay=0)
        ct.pprint()


t = threading.Thread(target=listen)
t.start()

time.sleep(10)

send(
    dict(mode='lixian',
         cmd='jianmo',
         zhunquelv=0.9,
         moxinglujing='[path-to-module]',
         timestamp=time.time()))

for err in RuntimeErrors.values():
    send(err)

while True:
    s = input('>> ')
    if not s:
        continue
    client.sendall(f'{s}'.encode())
    logging.debug(f'Server sent {s}')
    time.sleep(1)
