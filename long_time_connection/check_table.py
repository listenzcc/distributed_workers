class CheckTable():
    def __init__(self):
        self.define_issues()
        pass

    def define_issues(self):
        self.issues = {
            'lixian-kaishicaiji':
            dict(timestamp=float,
                 xiangxiangcishu=int,
                 shiyanzuci=int,
                 dongzuoleixing=int),
            'lixian-jieshucaiji':
            dict(timestamp=float),
            'lixian-jieshuciji':
            dict(timestamp=float),
            'lixian-jianmo':
            dict(shujulujing=str, timestamp=float),
            'zaixian-kaishicaiji':
            dict(timestamp=float,
                 xiangxiangcishu=int,
                 zantingshijian=int,
                 dongzuoleixing=int,
                 moxinglujing=str),
            'zaixian-jieshucaiji':
            dict(timestamp=float),
            'zaixian-jieshuciji':
            dict(timestamp=float)
        }

    def add(self, query):
        if not isinstance(query, dict):
            return 1

        if not all(['mode' in query, 'cmd' in query]):
            return 1

        # Regular query and get iss based on cmd
        cmd = '{mode}-{cmd}'.format(**query)
        [query.pop(e) for e in ['mode', 'cmd']]
        try:
            iss = self.issues[cmd].copy()
        except KeyError:
            return 1

        # Cross check on iss and query
        try:
            assert (len(iss) == len(query))
            assert (all(e in iss for e in query))
        except AssertionError:
            return 1

        # Format query to iss
        for k in iss:
            T = iss[k]
            try:
                iss[k] = T(query[k])
            except:
                print(k)
                return 1

        # Correctly add
        self.issues[cmd] = iss
        return 0

    def pprint(self):
        print('-' * 80)
        for k in self.issues:
            for p in self.issues[k]:
                if isinstance(self.issues[k][p], type(int)):
                    box = '[----]'
                else:
                    box = '[PASS]'
                print(f'{box} {k}: {p}={self.issues[k][p]}')


if __name__ == '__main__':
    ct = CheckTable()
    ct.pprint()

    ct.add(dict(mode='lixian', cmd='jianmo', timestamp=3, shujulujing='aa'))
    ct.pprint()
