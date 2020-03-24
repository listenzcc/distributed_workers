import socket
import json
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


def send(msg, client=client):
    if isinstance(msg, dict):
        msg = json.dumps(msg).encode()
    client.send(msg)
    logging.debug(f'Client send {msg}')
    time.sleep(1)


# Legal request
send(
    dict(mode='lixian',
         cmd='kaishicaiji',
         xiangxiangcishu=3,
         shiyanzuci=5,
         dongzuoleixing=2,
         timestamp=time.time()))

send(dict(mode='lixian', cmd='jieshucaiji', timestamp=time.time()))

send(dict(mode='lixian', cmd='jieshuciji', timestamp=time.time()))

send(
    dict(mode='lixian',
         cmd='jianmo',
         shujulujing='[Path-to-Data]',
         timestamp=time.time()))

send(
    dict(mode='zaixian',
         cmd='kaishicaiji',
         moxinglujing='[模型目录]',
         xiangxiangcishu=10,
         zantingshijian=5,
         dongzuoleixing=4,
         timestamp=time.time()))

send(dict(mode='zaixian', cmd='jieshucaiji', timestamp=time.time()))

send(dict(mode='zaixian', cmd='jieshuciji', timestamp=time.time()))

# Illegal request
send(dict(mode='wrongmode', timestamp=time.time()))
