""" BCI worker. """

import os
import time
from logger import Logger
from profile import RealtimeReply, RuntimeError

logger = Logger(name='worker').logger
rtreply = RealtimeReply()
rerror = RuntimeError()


def mkdir(path):
    """ Safety mkdir as [path] """
    # Mkdir if not exists
    if not os.path.exists(path):
        s = os.path.split(path)
        # Recursive create parent
        if s[0]:
            mkdir(s[0])
        # Mkdir child
        os.mkdir(path)
        logger.debug(f'Created {path}')
    # Make sure path is a folder
    assert(os.path.isdir(path))


def send(msg):
    """ Virtual sending method,
    used when sending method is not provided."""
    logger.debug(f'Virtual send {msg}')


def onerror(error, detail, send=send):
    """ Handle runtime errors,
    logging and send RuntimeError."""
    logger.debug(detail)
    errormsg = error(detail)
    send(errormsg)
    logger.debug(f'Sent RuntimeError: {errormsg}')


class Worker():
    def __init__(self):
        self._state = 'Busy'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, s):
        assert(s in ['Idle', 'Busy', 'Online', 'Offline'])
        if not s == self._state:
            self._state = s
            logger.info(f'State switched to {s}.')

    def check_state(self, states, workload, send=send):
        if isinstance(states, str):
            states = [states]
        if not self.state in states:
            onerror(rerror.StateError,
                    f'Wrong state {self.state} for {workload}',
                    send=send)
            return 1
        return 0

    def offline_kaishicaiji(self, shujumulu, timestamp=0, send=send):
        # Send OK means I has got everything in need,
        # but not guartee that all the things are correct,
        # if incorrect, I will reply Error in further
        send(rtreply.OK())

        # The state should be 'Idle'
        if self.check_state('Idle', 'offline_kaishicaiji', send=send) == 1:
            return 1

        # Try to mkdir and check of {shujumulu}
        try:
            mkdir(shujumulu)
        except:
            onerror(rerror.FileError, shujumulu, send=send)
            return 1

        # Workload
        self.state = 'Offline'

        return 0

    def offline_jieshucaiji(self, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Offline'
        if self.check_state('Offline', 'offline_jieshucaiji', send=send) == 1:
            return 1

        # workload
        self.state = 'Idle'

        return 0

    def offline_jianmo(self, shujumulu, moxingmulu, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Idle'
        if self.check_state('Idle', 'offline_jianmo', send=send) == 1:
            return 1

        # todo: check shujumulu

        try:
            mkdir(moxingmulu)
        except:
            onerror(rerror.FileError, moxingmulu, send=send)
            return 1

        # Workload
        self.state = 'Busy'
        moxinglujing = os.path.join(moxingmulu, 'model.txt')
        with open(moxinglujing, 'w') as f:
            f.writelines(['Hello, I am a model.\n',
                          f'shujumulu',
                          time.ctime()])
        send(dict(mode='Offline',
                  cmd='zhunquelv',
                  moxinglujing=moxinglujing,
                  shujulujing=shujumulu,
                  zhunquelv='0.95',
                  timestamp=time.time()))
        self.state = 'Idle'

        return 0

    def online_kaishicaiji(self, moxinglujing, timestamp=0, send=send):
        send(rtreply.OK())

        # todo: check moxinglujing

        if self.check_state('Idle', 'online_kaishicaiji', send=send) == 1:
            return 1

        # Workload
        self.state = 'Online'

        return 0

    def online_jieshucaiji(self, timestamp=0, send=send):
        send(rtreply.OK())

        if self.check_state('Online', 'online_jieshucaiji', send=send) == 1:
            return 1

        # workload
        self.state = 'Idle'

        return 0

    def query(self, chixushijian, zhenshibiaoqian, timestamp=0, send=send):
        send(rtreply.OK())

        if self.check_state('Online', 'query', send=send) == 1:
            return 1

        # Workload
        self.state = 'Busy'
        # todo: guess label
        gujibiaoqian = "1"
        send(dict(mode='QueryReply',
                  gujibiaoqian=gujibiaoqian,
                  timestamp=time.time()))
        self.state = 'Online'

        return 0

    def keepalive(self, timestamp=0, send=send):
        send(rtreply.KeepAlive())
        return 0


if __name__ == '__main__':
    w = Worker()
    w.state = 'Idle'

    pass
