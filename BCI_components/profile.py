""" BCI profiles """
import os
import time
from logger import Logger

IP = 'localhost'
PORT = 63365
BUF_SIZE = 1024

logger = Logger(name='BCI', filepath=os.path.join('BCI.log')).logger


def stamp(d):
    """Add time stamp in [d]

    Arguments:
        d {dict} -- Where to add

    Returns:
        {dict} -- New dict with timestamp added
    """
    assert(isinstance(d, dict))
    d['timestamp'] = time.time()
    return d


class RealtimeReply():
    """Real time reply instance,
    legal types are limited. """

    def __init__(self):
        pass

    def OK(self):
        """OK response means TCP package is received and understandable.

        Returns:
            {dict} -- OK response
        """
        return stamp(dict(mode='Reply',
                          state='OK'))

    def ParseError(self):
        """ParseError response means TCP packages is received but can not be understand.

        Returns:
            {dict} -- ParseError response
        """
        return stamp(dict(mode='Reply',
                          state='ParseError'))

    def KeepAlive(self):
        """Response to KeepAlive package, used only for KeepAlive package being received.

        Returns:
            {dict} -- KeepAlive response
        """
        return stamp(dict(mode='Reply',
                          state='KeepAlive'))


class RuntimeError():
    """Runtime Error means something is wrong during operation. """

    def __init__(self):
        pass

    def FileError(self, detail=''):
        """File not found or can not be operated.

        Keyword Arguments:
            detail {str} -- Brief description of the error (default: {''})

        Returns:
            {dict} -- File Error
        """
        return stamp(dict(mode='RuntimeError',
                          type='FileError',
                          detail=detail))

    def BusyError(self, detail=''):
        """Resource busy error means required operation can not be operated because device or cpu is too busy.

        Keyword Arguments:
            detail {str} -- Brief description of the error (default: {''})

        Returns:
            {dict} -- Busy Error
        """
        return stamp(dict(mode='RuntimeError',
                          type='BusyError',
                          detail=detail))

    def StateError(self, detail=''):
        """State error means package require an operation under wrong state,
        like asking for START COLLECTION during ONLINE or OFFLINE state,
        since I can only do one collection process only;
        like asking for STOP COLLECTION before START COLLECTION.

        Keyword Arguments:
            detail {str} -- Brief description of the error (default: {''})

        Returns:
            {dict} -- State Error
        """
        return stamp(dict(mode='RuntimeError',
                          type='StateError',
                          detail=detail))

    def UnknownError(self, detail=''):
        """Unknown error

        Keyword Arguments:
            detail {str} -- Brief description of the error (default: {''})

        Returns:
            {dict} -- Unknown Error
        """
        return stamp(dict(mode='RuntimeError',
                          type='UnknownError',
                          detail=detail))
