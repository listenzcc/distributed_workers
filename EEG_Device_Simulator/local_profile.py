""" BCI profiles """
import os
import time
from logger import Logger

IP = '127.0.0.1'
PORT = 8844  # 63333
BUF_SIZE = 1024

logger = Logger(name='EEGTCP', filepath=os.path.join('EEGTCP.log')).logger

NUM_CHANNEL = 25
SFREQ = 300
