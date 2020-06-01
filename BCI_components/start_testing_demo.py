# Start a testing demo,
# It contains three powershell windows,
# 1. In the current folder, run server.py;
# 2. In ../EEG_Device_Simulator folder, run tcp_server.py, an EEG simulator;
# 3. In the current folder, run client_offline.py or client_online.py.

import os

os.system('start powershell')
os.system('start powershell')

os.chdir(os.path.join('..', 'EEG_Device_Simulator'))
os.system('start powershell')
