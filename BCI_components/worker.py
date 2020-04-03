""" BCI worker. """

import os
import time
import threading
from logger import Logger
from profile import RealtimeReply, RuntimeError, logger

rtreply = RealtimeReply()
rterror = RuntimeError()


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
    logger.error(detail)
    errormsg = error(detail)
    send(errormsg)
    logger.debug(f'Sent RuntimeError: {errormsg}')


class Worker():
    def __init__(self):
        self._state = 'Busy'
        self._labels = []

    def get_ready(self, moxinglujing=None, shujulujing=None):
        self._state = 'Idle'
        self._labels = []
        self.moxinglujing = moxinglujing
        self.shujulujing = shujulujing
        logger.info('Worker is ready to go.')

    def accuracy(self):
        total = len(self.labels)
        correct = len([e for e in self.labels if e[0] == e[1]])
        return correct / total

    @property
    def labels(self):
        return self._labels

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
            onerror(rterror.StateError,
                    f'Wrong state {self.state} for {workload}',
                    send=send)
            return 1
        return 0

    def record(self, fpath, model_msg=''):
        """ Simulation of record method. """
        logger.info('Record starts.')
        logger.debug(f'Record fpath is {fpath}')
        with open(fpath, 'w') as f:
            f.write(f'{model_msg}\n')
            f.write('-' * 40 + 'starts.\n')
            while self.state not in ['Idle']:
                f.write(time.ctime() + '\n')
                time.sleep(0.2)
            f.write('-' * 40 + 'ends.\n')
        logger.info('Record finished.')

    def offline_kaishicaiji(self, shujulujingqianzhui, timestamp=0, send=send):
        # Send OK means I has got everything in need,
        # but not guartee that all the things are correct,
        # if incorrect, I will reply Error in further
        send(rtreply.OK())

        # The state should be 'Idle'
        if self.check_state('Idle', 'offline_kaishicaiji', send=send) == 1:
            return 1

        # Try to mkdir and check of {shujulujingqianzhui}
        try:
            mkdir(os.path.dirname(shujulujingqianzhui))
        except:
            onerror(rterror.FileError, shujulujingqianzhui, send=send)
            return 1

        # Workload
        self.get_ready()
        self.state = 'Offline'
        fpath = f'{shujulujingqianzhui}.cnt'
        t = threading.Thread(target=self.record, args=(fpath,))
        t.setDaemon(True)
        t.start()

        return 0

    def offline_jieshucaiji(self, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Offline'
        if self.check_state('Offline', 'offline_jieshucaiji', send=send) == 1:
            return 1

        # workload
        self.state = 'Idle'

        return 0

    def offline_jianmo(self, shujulujing, moxinglujingqianzhui, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Idle'
        if self.check_state('Idle', 'offline_jianmo', send=send) == 1:
            return 1

        # Check {shujulujing}
        if not os.path.exists(shujulujing):
            onerror(rterror.FileError, shujulujing, send=send)
            return 1

        # Try to mkdir and check of {moxinglujingqianzhui}
        try:
            mkdir(os.path.dirname(moxinglujingqianzhui))
        except:
            onerror(rterror.FileError, moxinglujingqianzhui, send=send)
            return 1

        # Workload
        self.state = 'Busy'
        moxinglujing = f'{moxinglujingqianzhui}.mat'
        with open(moxinglujing, 'w') as f:
            f.writelines(['Hello, I am a model.\n',
                          time.ctime(),
                          '\n------------------\n'])
            f.write(f'{shujulujing}\n')
            f.write('\n------------------------ends')
        send(dict(mode='Offline',
                  cmd='zhunquelv',
                  moxinglujing=moxinglujing,
                  zhunquelv='0.95',
                  timestamp=time.time()))
        self.state = 'Idle'

        return 0

    def online_kaishicaiji(self, moxinglujing, shujulujingqianzhui, timestamp=0, send=send):
        send(rtreply.OK())

        # Check moxinglujing
        if not os.path.exists(os.path.dirname(moxinglujing)):
            onerror(rterror.FileError, moxinglujing, send=send)

        # Try to mkdir and check of {shujulujingqianzhui}
        try:
            mkdir(os.path.dirname(shujulujingqianzhui))
        except:
            onerror(rterror.FileError, shujulujingqianzhui, send=send)
            return 1

        # The state should be 'Idle'
        if self.check_state('Idle', 'online_kaishicaiji', send=send) == 1:
            return 1

        # Workload
        fpath = f'{shujulujingqianzhui}.cnt'
        self.get_ready(moxinglujing=moxinglujing,
                       shujulujing=fpath)
        self.state = 'Online'
        t = threading.Thread(target=self.record, args=(fpath, moxinglujing))
        t.setDaemon(True)
        t.start()

        return 0

    def online_jieshucaiji(self, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Online'
        if self.check_state('Online', 'online_jieshucaiji', send=send) == 1:
            return 1

        # Workload
        zhunquelv = self.accuracy()
        logger.debug(f'Accuracy is {zhunquelv}')
        send(dict(mode='Online',
                  cmd='zhunquelv',
                  zhunquelv=zhunquelv,
                  moxinglujing=self.moxinglujing,
                  shujulujing=self.shujulujing,
                  timestamp=time.time()))
        self.state = 'Idle'

        return 0

    def query(self, chixushijian, zhenshibiaoqian, timestamp=0, send=send):
        send(rtreply.OK())

        # The state should be 'Online'
        if self.check_state('Online', 'query', send=send) == 1:
            return 1

        # Workload
        self.state = 'Busy'
        # Guess label
        gujibiaoqian = "1"
        self.labels.append((gujibiaoqian, zhenshibiaoqian))
        logger.debug(f'Labels is {self.labels}')
        send(dict(mode='QueryReply',
                  gujibiaoqian=gujibiaoqian,
                  timestamp=time.time()))
        self.state = 'Online'

        return 0

    def keepalive(self, timestamp=0, send=send):
        # Reply keep alive package
        send(rtreply.KeepAlive())
        return 0


if __name__ == '__main__':
    w = Worker()
    w.state = 'Idle'

    pass
