import os
import time

os.system('start python server.py')

os.system('start python client_offline.py')
input('Press enter when Offline is finished')

os.system('start python client_online.py')
