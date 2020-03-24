""" Profiles """

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(asctime)s - %(message)s')

IP = 'localhost'
PORT = 63356
BUF_SIZE = 1024

Responses = dict(
    OKResponse=dict(
        # OK
        type='Resp',
        state='OK',
        repeat='',
        timestamp=0,
    ),
    FailResponse=dict(
        # Fail
        type='Resp',
        state='FAIL',
        repeat='',
        timestamp=0,
    ))

RuntimeErrors = dict(
    FileNotFoundError=dict(
        # File not found on given path
        type='RuntimeError',
        name='FileNotFoundError',
        detail='',
        timestamp=0,
    ),
    ValueError=dict(
        # Incoming value can not be correctly parsed
        type='RuntimeError',
        name='ValueError',
        detail='',
        timestamp=0,
    ),
    InterruptedError=dict(
        # Operation being interrupted
        # It normally means the operation stops unexpected.
        type='RuntimeError',
        name='InterruptedError',
        detail='',
        timestamp=0,
    ),
    BusyError=dict(
        # Operation failed because the resource is busy
        type='RuntimeError',
        name='BusyError',
        detail='',
        timestamp=0,
    ),
    UnknownError=dict(
        # For errors that are not defined
        type='RuntimeError',
        name='UnknownError',
        detail='',
        timestamp=0,
    ))
