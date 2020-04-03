import os

for cmd in [
    'server.py',
    'client_offline.py',
    # 'client.py'
]:
    os.system(f'start python {cmd}')
