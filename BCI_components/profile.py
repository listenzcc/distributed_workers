""" BCI profiles """
import time

IP = 'localhost'
PORT = 63365
BUF_SIZE = 1024


class RealtimeReply():
    def __init__(self):
        pass

    def OK(self):
        return dict(mode='Reply',
                    state='OK',
                    timestamp=time.time())

    def ParseError(self):
        return dict(mode='Reply',
                    state='ParseError',
                    timestamp=time.time())

    def KeepAlive(self):
        return dict(mode='Reply',
                    state='KeepAlive',
                    timestamp=time.time())
