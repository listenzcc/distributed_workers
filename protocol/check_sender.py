""" Send message through TCP socket. """
import socket
import json
import time

from profile import IP, PORT, logging

logging.info('Starting...')

def send(msg):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, PORT))
        assert(isinstance(msg, dict))
        msg = json.dumps(msg).encode()
        client.sendall(msg)
        received = client.recv(1024)
        client.close()
        logging.info(f'Send success, receive {received}.')
        return received
    except Exception as err:
        logging.error(f'Send failed, {err}.')
        return None


print(send(dict(mode='lixian',
                cmd='kaishicaiji',
                xiangxiangcishu=3,
                shiyanzuci=5,
                timestamp=time.time())))

print(send(dict(mode='lixian',
                cmd='jieshucaiji',
                timestamp=time.time())))

print(send(dict(mode='lixian',
                cmd='jieshuciji',
                timestamp=time.time())))

print(send(dict(mode='lixian',
                cmd='jianmo',
                shujulujing='[Path-to-Data]',
                timestamp=time.time())))

print(send(dict(mode='zaixian',
                cmd='kaishicaiji',
                moxinglujing='[模型目录]',
                xiangxiangcishu=10,
                zantingshijian=5,
                timestamp=time.time())))

print(send(dict(mode='zaixian',
                cmd='jieshucaiji',
                timestamp=time.time())))

print(send(dict(mode='zaixian',
                cmd='jieshuciji',
                timestamp=time.time())))

