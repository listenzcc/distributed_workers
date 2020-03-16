""" Manager of several workers,
it should be start advance of workers. """

import os
import time
import json
import socket
import socketserver
import threading
from pprint import pprint

from toolbox import get_local_ip, PORT_RANGE, logger


class Manager():
    """ Manager """

    def __init__(self):
        self.local_ip = get_local_ip()
        self.local_port = None
        self.known_workers = dict()

    def _add_worker_(self, ip, port, name=time.ctime()):
        """ Add worker from [id]:[port] as [name] into self.known_workers. """
        id = f'{ip}:{port}'
        if id in self.known_workers:
            logger.warning('Repeat worker. Something is wrong.')
        self.known_workers[id] = dict(ip=ip, port=port, name=name)

    def _remove_worker_(self, id):
        """ Remove [id] worker from self.known_workers. """
        if not id in self.known_workers:
            logger.warning('Removing unknown worker. Doing nothing.')
            return
        self.known_workers.pop(id)

    def list_workers(self):
        """ List self.known_workers. """
        unavaible_ids = []
        j = 0
        for id in self.known_workers:
            ip = self.known_workers[id]['ip']
            port = self.known_workers[id]['port']

            received = self.send(json.dumps(dict(cmd='QueryState')), ip, port)
            if received == -1:
                unavaible_ids.append(id)
                continue
            print(f'[{j}] {id} - {received}')
            j += 1

        for id in unavaible_ids:
            self._remove_worker_(id)

    def send(self, msg, ip, port):
        """ Send [msg] to [ip]:[port].
        Return received message if send success,
        return -1 if send fail."""

        if isinstance(msg, dict):
            msg = json.dumps(msg)

        if not isinstance(msg, type(b'hello')):
            msg = str(msg).encode()

        assert(all([isinstance(ip, type('127.0.0.1')),
                    isinstance(port, type(65536)),
                    isinstance(msg, type(b'hello'))]))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((ip, port))
            client.sendall(msg)
            received = client.recv(1024)
            logger.debug(f'Send success, receive {received}.')
            r = received
        except Exception as err:
            logger.error(f'Send failed, {err}.')
            r = -1
        finally:
            client.close()
        return r

    def start_listening(self, handler, port_range=PORT_RANGE):
        """ Start listening. """
        # Try a useable port,
        # setup a TCP server,
        # Register on the manager.
        ip = self.local_ip
        for port in port_range:
            try:
                # Setup TCP server
                server = socketserver.TCPServer((ip, port),
                                                handler)
                t = threading.Thread(target=server.serve_forever)
                t.start()
                self.local_port = port
                self.server = server
                logger.info(f'TCPServer started at {ip}:{port}.')
                return
            except Exception as err:
                logger.warning(
                    f'TCPServer starts failed on {ip}:{port}, {err}.')
                continue

        # PORT_RANGE is used up.
        logger.error(f'TCPServer can not start.')
        return


manager = Manager()


class Handler_TCPServer(socketserver.BaseRequestHandler):
    """ The TCP Server class for demonstration.
    Note: We need to implement the Handle method to exchange data
    with TCP client. """

    def sendback(self, msg):
        """ Send back [msg]. """
        if isinstance(msg, str):
            msg = msg.encode()
        self.request.sendall(msg)

    def response(self):
        """ Response self.data. """
        receive = json.loads(self.data)

        # NewWorker registered request
        if receive.get('cmd', None) == 'NewWorker':
            receive.pop('cmd')
            manager._add_worker_(**receive)
            self.sendback('OK')
            return

        # TestLink request
        if receive.get('cmd', None) == 'TestLink':
            self.sendback('OK')
            return

        # Not recognized request
        self.sendback(f'Illegal request: {self.data}.')

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.debug('Receive {} from {}'.format(
            self.data, self.client_address))
        self.response()


if __name__ == '__main__':
    manager.start_listening(Handler_TCPServer)

    # print (os.system('pwd'))

    d = ''
    while True:
        if d not in manager.known_workers:
            d = ''
        c = input(f'{d}\n>> ')

        # Quit
        if c == 'q':
            break

        # New local worker
        if c == 'n':
            os.system('start python ./worker/worker.py')
            continue

        # List known workers
        if c == 'l':
            manager.list_workers()
            continue

        # Select worker
        if c.startswith('s'):
            idx = int(c.split()[-1])
            lst = [k for k in manager.known_workers]
            try:
                d = lst[idx]
            except Exception as err:
                d = ''
            continue

        # Send message of workload
        if c.startswith('m'):
            try:
                ip = manager.known_workers[d]['ip']
                port = manager.known_workers[d]['port']
                _, cmd, n = c.split()
                manager.send(msg=dict(cmd=cmd, n=n),
                             ip=ip,
                             port=port)
            except Exception as err:
                logger.error(f'{err}')
            continue

        # Send message of dismiss
        if c == 'k':
            try:
                ip = manager.known_workers[d]['ip']
                port = manager.known_workers[d]['port']
                manager.send(msg=dict(cmd='Dismiss'),
                             ip=ip,
                             port=port)
                manager._remove_worker_(d)
                manager.list_workers()
            except Exception as err:
                logger.error(f'{err}')
            continue

        # [c] is invalid if it reaches here
        if c:
            print (f'Invalid input {c}, doing nothing.')

    try:
        manager.server.shutdown()
    finally:
        print('ByeBye.')
