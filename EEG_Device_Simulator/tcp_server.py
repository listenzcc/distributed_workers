
import numpy as np
import time
import os
import sys
import struct
import socket

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa

from local_profile import IP, PORT, BUF_SIZE, NUM_CHANNEL, SFREQ, logger

logger.info('---- New Session ----')


def make_up_package(floats):
    """Make up Dry EEG device package

    Arguments:
        floats {list} -- List of float values, the values will be sent as simulation of an EEG device

    Returns:
        bits {bytes} -- Well formulated bytes to simulate an EEG device
    """

    # Fixed stuffs
    # 0-1-2-3-4
    _token = b'@ABCD'

    # 5
    _type = chr(1).encode()

    # 8-9-10-11
    _package_number = b''.join(chr(e).encode() for e in [1, 2, 3, 4])

    # 12-13-14-15
    _time_stamp = b''.join(chr(e).encode() for e in [0, 0, 0, 0])

    # 16
    _data_counter = chr(0).encode()

    # 17-18-19-20-21-22
    _adc_status = b''.join(chr(e).encode() for e in [0, 0, 4, 3, 2, 1])

    # 23--
    _bytes_floats = b''
    for f in floats:
        _bytes_floats += struct.pack('!f', f)

    # print(len(_bytes_floats))

    # Variable stuffs
    bits = b''

    # Split the float bits in case it is too long,
    # even it will not happen in normal
    _sub_length = 40000

    while _bytes_floats:
        # Cut the float bits
        _sub_bytes = _bytes_floats[:_sub_length]
        _bytes_floats = _bytes_floats[_sub_length:]

        # Compute length
        # 6-7, 2, 7
        _length = len(_sub_bytes) + 11
        _package_length = int.to_bytes(_length // 256, 1, 'little') +\
            int.to_bytes(_length % 256, 1, 'little')
        # print(_package_length)

        # Concatenate parts into legal bits
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
    """TCP server performing as a EEG device
    """

    def __init__(self, ip=IP, port=PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        logger.info(f'TCP Server is ready to listen on {ip}:{port}')

    def make_signal(self, state, interval):
        """Simulate 2 kinds of signals

        Arguments:
            state {str} -- The name of the state
            interval {float} -- The length of the signal

        Returns:
            {array} -- The values of the signal
        """
        # The length of the signal in 'second'
        num = int(SFREQ * interval)

        if self.new_switch:
            num_trigger = int(SFREQ * 0.01)
            self.new_switch = False
        else:
            num_trigger = 0

        # Motion imaging signal
        if state == 'imag':
            # Make data
            onepiece = np.array(range(NUM_CHANNEL, 0, -1)).astype(np.float)
            onepiece[NUM_CHANNEL - 1] = 0
            output = np.concatenate([onepiece for _ in range(num)])

            # Add trigger
            for j in range(num_trigger):
                output[NUM_CHANNEL - 1 + j * NUM_CHANNEL] = 1

            return output

        # Rest state signal
        if state == 'rest':
            # Make data
            onepiece = np.array(range(NUM_CHANNEL)).astype(np.float)
            onepiece[NUM_CHANNEL - 1] = 0
            output = np.concatenate([onepiece for _ in range(num)])

            # Add trigger
            for j in range(num_trigger):
                output[NUM_CHANNEL - 1 + j * NUM_CHANNEL] = 2

            return output

    def start(self):
        """TCP server starts,
        now it serves forever,
        if it is disconnected, it will start a new listening immediately.
        """

        while True:
            try:
                self.server.listen(1)
                logger.info(f'TCP Server starts listening.')

                # Accept in comming connection
                client, address = self.server.accept()
                logger.info(
                    f'New connection is established: {address}:{client}')

                # Say hi...........
                # client.sendall(b'hello')

                # Intending I am a EEG device,
                # and I am serving.
                interval = 0.1
                passed_time = 0
                states = ['rest', 'imag', 'rest', 'imag']
                idx = 0
                t = time.time()
                print(states[idx])

                # Whether the data slice contains a trigger on head
                self.new_switch = True

                while True:
                    # Make up bits according to [state] and [interval]
                    bits = make_up_package(self.make_signal(state=states[idx],
                                                            interval=interval))

                    # Send bits
                    client.sendall(bits)

                    time.sleep(interval - (time.time()-t) % interval)
                    # Update passed_time
                    passed_time += interval

                    # The state will be updated every 5 seconds
                    if passed_time > 5:
                        # Every time we update idx,
                        # new_switch should be set
                        self.new_switch = True

                        # Update idx
                        idx += 1
                        idx %= len(states)
                        print(states[idx])

                        # Reset passed_time
                        passed_time = 0
            except ConnectionAbortedError:
                continue
            except KeyboardInterrupt:
                break

        client.close()


if __name__ == '__main__':
    server = Server()
    server.start()
    print('Done.')
