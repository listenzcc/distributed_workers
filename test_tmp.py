import time
import threading

class AClass():
    def __init__(self):
        self.a = 0
        print('__init__')

    def _workload_(self):
        self.a = 0
        for j in range(5):
            print(f'-{j}')
            self.a += 1
            time.sleep(1)

    def workload(self):
        t = threading.Thread(target=self._workload_)
        t.start()


if __name__ == '__main__':
    aclass = AClass()
    aclass.workload()
    for j in range(3):
        print(aclass.a)
        time.sleep(1)