
import numpy as np
import time
import struct
import socket
from local_profile import IP, PORT, BUF_SIZE, NUM_CHANNEL, SFREQ, logger

logger.info('---- New Session ----')


def make_up_package(floats):
    # 0-1-2-3, 4, 4
    _token = b'@ABCD'

    # 4, 1, 5
    _type = chr(1).encode()

    # 7-8-9-10, 4, 11
    _package_number = b''.join(chr(e).encode() for e in [1, 2, 3, 4])

    # 11-12-13-14, 4, 15
    _time_stamp = b''.join(chr(e).encode() for e in [0, 0, 0, 0])

    # 15, 1, 16
    _data_counter = chr(0).encode()

    # 16-17-18-19-20-21, 6, 22
    _adc_status = b''.join(chr(e).encode() for e in [0, 0, 4, 3, 2, 1])

    # 22--
    _bytes_floats = b''
    for f in floats:
        _bytes_floats += struct.pack('!f', f)

    # print(len(_bytes_floats))

    bits = b''

    _sub_length = 40000

    while _bytes_floats:
        _sub_bytes = _bytes_floats[:_sub_length]
        _bytes_floats = _bytes_floats[_sub_length:]

        # 5-6, 2, 7
        _length = len(_sub_bytes) + 11
        # _package_length = chr(_length // 256).encode() + \
        #     chr(_length % 256).encode()

        # _package_length = (chr(_length // 256) +
        #                    chr(_length % 256)).encode('utf-8')
        _package_length = int.to_bytes(_length // 256, 1, 'little') +\
            int.to_bytes(_length % 256, 1, 'little')
        # print(_package_length)

        bits += _token \
            + _type \
            + _package_length \
            + _package_number \
            + _time_stamp \
            + _data_counter \
            + _adc_status \
            + _sub_bytes

    # print(bits)

    return bits


class Server():
    def __init__(self, ip=IP, port=PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        logger.info(f'TCP Server is ready to listen on {ip}:{port}')

    def make_signal(self, state, interval):
        num = int(SFREQ * interval)

        if state == 'rest':
            onepiece = np.zeros((NUM_CHANNEL)).astype(np.float)
            return np.concatenate([onepiece for _ in range(num)])

        if state == 'fake':
            onepiece = np.array(range(NUM_CHANNEL)).astype(np.float)
            onepiece[NUM_CHANNEL - 1] = 1
            return np.concatenate([onepiece for _ in range(num)])

        if state == 'real':
            onepiece = np.array(range(NUM_CHANNEL, 0, -1)).astype(np.float)
            onepiece[NUM_CHANNEL - 1] = 2
            return np.concatenate([onepiece for _ in range(num)])

    def start(self):
        self.server.listen(1)
        logger.info(f'TCP Server starts listening.')

        client, address = self.server.accept()
        logger.info(f'New connection is established: {address}:{client}')

        client.sendall(b'hello')
        # for j in range(10):

        interval = 0.1
        passed_time = 0
        states = ['rest', 'fake', 'rest', 'real']
        idx = 0
        while True:
            time.sleep(interval)
            passed_time += interval
            if passed_time > 4:
                passed_time = 0
                idx += 1
                idx %= len(states)
                print(states[idx])

            bits = make_up_package(self.make_signal(state=states[idx],
                                                    interval=interval))
            client.sendall(bits)

        client.close()


if __name__ == '__main__':
    server = Server()
    server.start()
    print('Done.')
