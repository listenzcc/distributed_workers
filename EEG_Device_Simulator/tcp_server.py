
import numpy as np
import time
import struct
import socket
from local_profile import IP, PORT, BUF_SIZE, NUM_CHANNEL, SFREQ, logger

logger.info('---- New Session ----')


def make_up_package(floats):
    # 22--
    _bytes_floats = b''
    for f in floats:
        _bytes_floats += struct.pack('!f', f)

    # 0-1-2-3, 4, 4
    _token = b'@ABCD'

    # 4, 1, 5
    _type = chr(1).encode()

    # 5-6, 2, 7
    _length = len(_bytes_floats) + 11
    _package_length = chr(_length // 256).encode() + \
        chr(_length % 256).encode()

    # 7-8-9-10, 4, 11
    _package_number = b''.join(chr(e).encode() for e in [0, 0, 0, 0])

    # 11-12-13-14, 4, 15
    _time_stamp = b''.join(chr(e).encode() for e in [0, 0, 0, 0])

    # 15, 1, 16
    _data_counter = chr(0).encode()

    # 16-17-18-19-20-21, 6, 22
    _adc_status = b''.join(chr(e).encode() for e in [0, 0, 0, 0, 0, 0])

    return _token \
        + _type \
        + _package_length \
        + _package_number \
        + _time_stamp \
        + _data_counter \
        + _adc_status \
        + _bytes_floats


class Server():
    def __init__(self, ip=IP, port=PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        logger.info(f'TCP Server is ready to listen on {ip}:{port}')

    def start(self):
        self.server.listen(1)
        logger.info(f'TCP Server starts listening.')

        client, address = self.server.accept()
        logger.info(f'New connection is established: {address}:{client}')

        client.sendall(b'hello')
        # for j in range(10):

        interval = 0.1
        passed_time = 0
        while True:
            time.sleep(interval)
            passed_time += interval
            print(passed_time)
            bits = make_up_package(np.linspace(
                1, 25 * SFREQ * interval, int(25 * SFREQ * interval)))
            # bits = b''
            # for e in [0.34, 0.83, -0.64]:
            #     bits += struct.pack('!f', e)
            # print(j, bits)
            client.sendall(bits)

        client.close()


if __name__ == '__main__':
    server = Server()
    server.start()
    print('Done.')
