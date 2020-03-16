import logging
import socket

MANAGER_IP = '10.0.2.74'
MANAGER_PORT = 60000

LOGGER_NAME = 'logging.log'
PORT_RANGE = [e for e in range(60000, 60010)]

def get_local_ip():
    """ Get IP of local machine. """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class Logger():
    """ Auto logging. """

    def __init__(self, fname=LOGGER_NAME):
        logging.basicConfig(filename=fname,
                            level=logging.DEBUG,
                            format='%(levelname)s, %(asctime)s, %(message)s')

    def info(self, msg):
        print(f'INFO: {msg}')
        logging.info(msg)

    def warning(self, msg):
        print(f'WARNING: {msg}')
        logging.warning(msg)

    def error(self, msg):
        print(f'!!!ERROR: {msg}')
        logging.error(msg)

    def debug(self, msg):
        print(f'DEBUG: {msg}')
        logging.debug(msg)


logger = Logger()
