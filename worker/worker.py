""" I am a worker,
I maintain a TCP server to listen. """

import tqdm
import time
import json
import socket
import socketserver
import threading

from toolbox import get_local_ip, PORT_RANGE, logger
from toolbox import MANAGER_IP, MANAGER_PORT


class Worker():
    def __init__(self):
        self.remaining = -1
        self.idle = True
        self.local_ip = get_local_ip()

    def _workload_(self, n):
        """ Simulation of time consuming work. """
        self.idle = False
        self.remaining = n
        for _ in tqdm.trange(n):
            self.remaining -= 1
            time.sleep(1)
        self.idle = True
        self.remaining = -1

    def workload(self, n):
        """ Start a thread for self._workload_. """
        if not self.idle:
            logger.warning('Workload can not be set, since I am busy.')
            return 1
        t = threading.Thread(target=self._workload_, args=(n,))
        t.start()
        return 0

    def send(self, msg=time.ctime(), ip=MANAGER_IP, port=MANAGER_PORT):
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
        # Test link with manager
        # Not listening if can not connect to the manager
        if not self.send(msg=dict(cmd='TestLink')) == b'OK':
            logger.error(f'Can not connect to the manager.')
            return

        # Try a useable port,
        # setup a TCP server,
        # Register on the manager.
        ip = self.local_ip
        for port in port_range:
            try:
                # Setup TCP server
                server = socketserver.TCPServer((ip, port), handler)
                t = threading.Thread(target=server.serve_forever)
                t.start()
                self.local_port = port
                self.server = server

                # Register on the manager
                if not self.send(msg=dict(cmd='NewWorker', ip=ip, port=port, name='worker')) == b'OK':
                    # If failed, shutdown the server.
                    server.shutdown()
                    logger.error(f'No available manager.')
                    raise ConnectionRefusedError

                logger.info(f'TCPServer started at {ip}:{port}.')
                return
            except Exception as err:
                logger.warning(
                    f'TCPServer starts failed on {ip}:{port}, {err}.')
                continue

        # PORT_RANGE is used up.
        logger.error(f'TCPServer can not start.')
        return


worker = Worker()


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

        # New workload request
        if receive.get('cmd', None) == 'work':
            # Ignore the request since busying
            if not worker.idle:
                self.sendback('Ignoring the request, since I am busy.')
                return

            # Start new job on workload of n seconds
            if receive.get('n', None) is not None:
                try:
                    n = int(receive['n'])
                    assert(n > 0)
                except Exception as err:
                    # If n is illegal, sendback error
                    self.sendback(f'Illegal request {err}.')
                    return
                # Setup workload
                worker.workload(n)
                self.sendback('OK')
                return

        # TestLink request
        if receive.get('cmd', None) == 'TestLink':
            self.sendback('OK')
            return

        # QueryState request
        if receive.get('cmd', None) == 'QueryState':
            if worker.idle:
                # Sendback IDLE
                self.sendback('IDLE')
            else:
                # Sendback BUSY with remaining
                self.sendback('BUSY, {}'.format(worker.remaining))
            return

        # Dismiss request
        if receive.get('cmd', None) == 'Dismiss':
            self.sendback('BYE')
            # Shutdown TCPServer server
            try:
                worker.server.server_close()
            finally:
                print ('TCPServer has closed.')
            return

        self.sendback(f'Unrecognized request: {self.data}.')

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.debug('Receive {} from {}'.format(
            self.data, self.client_address))
        self.response()


if __name__ == '__main__':
    worker.start_listening(Handler_TCPServer)
    print('This window will close in 5 seconds.')
    time.sleep(5)
