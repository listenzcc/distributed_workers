""" Check table of incoming messages. """
import time
from profile import logging

class CheckTable():
    def __init__(self):
        self.issues = dict()
        self.add_lixian()
        self.add_zaixian()

    def add_lixian(self):
        self.issues['lixian-kaishicaiji'] = dict(
            xiangxiangcishu=None,
            shiyanzuci=None,
            timestamp=None
        )
        self.issues['lixian-jieshucaiji'] = dict(
            timestamp=None
        )
        self.issues['lixian-jieshuciji'] = dict(
            timestamp=None
        )
        self.issues['lixian-jianmo'] = dict(
            shujulujing=None,
            timestamp=None
        )

    def add_zaixian(self):
        self.issues['zaixian-kaishicaiji'] = dict(
            xiangxiangcishu=None,
            zantingshijian=None,
            moxinglujing=None,
            timestamp=None
        )
        self.issues['zaixian-jieshucaiji'] = dict(
            timestamp=None
        )
        self.issues['zaixian-jieshuciji'] = dict(
            timestamp=None
        )

    def add(self, query):
        if all(['mode' in query,
                'cmd' in query]):
            cmd = '{mode}-{cmd}'.format(**query)
            if cmd in self.issues:
                for k in query:
                    if k in ['mode', 'cmd']:
                        continue
                    if k in self.issues[cmd]:
                        self.issues[cmd][k] = query[k]
                    logging.info(f'Add {k} of {query}.')
                return
        logging.warning(f'Invalid {query}.')

    def pprint(self):
        for k in self.issues:
            if isinstance(self.issues[k], dict):
                for p in self.issues[k]:
                    if self.issues[k][p] is None:
                        box = '[----]'
                    else:
                        box = '[PASS]'
                    print(f'{box} {k}: {p}={self.issues[k][p]}')
            else:
                if self.issues[k] is None:
                    box = '[----]'
                else:
                    box = '[PASS]'
                print(f'{box} {k}={self.issues[k]}')


if __name__ == '__main__':
    ct = CheckTable()
    ct.pprint()
