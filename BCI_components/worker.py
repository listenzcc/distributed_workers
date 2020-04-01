""" BCI worker. """

import os
from logger import Logger

logger = Logger(name='worker').logger


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


def checkfile(path):
    """ Check [path] is a file. """
    assert(os.path.isfile(path))


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

    def offline_kaishicaiji(self, shujumulu, timestamp, client=None):
        mkdir(shujumulu)
        pass

    def offline_jieshucaiji(self, timestamp, client=None):
        pass

    def offline_jianmo(self, shujumulu, moxingmulu, timestamp, client=None):
        mkdir(shujumulu)
        mkdir(moxingmulu)
        pass
        return 'zhunquelv'

    def online_kaishicaiji(self, moxinglujing, timestamp, client=None):
        checkfile(moxinglujing)
        pass

    def online_jieshucaiji(self, timestamp, client=None):
        pass

    def query(self, chixushijian, zhenshibiaoqian, timestamp, client=None):
        pass


if __name__ == '__main__':
    w = Worker()
    w.state = 'Idle'

    pass
