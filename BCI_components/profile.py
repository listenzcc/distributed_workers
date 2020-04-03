""" BCI profiles """
import os
import time
from logger import Logger

IP = 'localhost'
PORT = 63365
BUF_SIZE = 1024

logger = Logger(name='BCI', filepath=os.path.join('BCI.log')).logger


def stamp(d):
    """ Add time stamp in {d} """
    assert(isinstance(d, dict))
    d['timestamp'] = time.time()
    return d


class RealtimeReply():
    def __init__(self):
        pass

    def OK(self):
        return stamp(dict(mode='Reply',
                          state='OK'))

    def ParseError(self):
        return stamp(dict(mode='Reply',
                          state='ParseError'))

    def KeepAlive(self):
        return stamp(dict(mode='Reply',
                          state='KeepAlive'))


class RuntimeError():
    def __init__(self):
        pass

    def FileError(self, detail=''):
        return stamp(dict(mode='RuntimeError',
                          type='FileError',
                          detail=detail))

    def BusyError(self, detail=''):
        return stamp(dict(mode='RuntimeError',
                          type='BusyError',
                          detail=detail))

    def StateError(self, detail=''):
        return stamp(dict(mode='RuntimeError',
                          type='StateError',
                          detail=detail))

    def UnknownError(self, detail=''):
        return stamp(dict(mode='RuntimeError',
                          type='UnknownError',
                          detail=detail))
