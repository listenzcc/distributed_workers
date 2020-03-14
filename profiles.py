import logging
from toolbox import get_local_ip

""" Basic settings. """
HOST = 'localhost'
HOST_PORT = 60000
PORT_RANGE = [e for e in range(60001, 60010)]
LOGGER_NAME = 'logging.log'


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


logger = Logger()

if __name__ == '__main__':
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
