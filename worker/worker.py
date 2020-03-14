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
        """ Send [msg] to [ip]:[port]. """
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
            logger.info(f'Send success, receive {received}.')
            r = 0
        except Exception as err:
            logger.error(f'Send failed, {err}.')
            r = -1
        finally:
            client.close()
        return r

    def start_listening(self, handler, port_range=PORT_RANGE):
        """ Start listening. """
        # Test link with manager
        if not self.send(msg=dict(cmd='TestLink')) == 0:
            logger.error(f'Can not connect to the manager.')
            return

        ip = self.local_ip
        for port in port_range:
            try:
                server = socketserver.TCPServer((ip, port), handler)
                t = threading.Thread(target=server.serve_forever)
                t.start()
                self.local_port = port

                if not self.send(msg=dict(cmd='NewWorker', ip=ip, port=port, name='worker')) == 0:
                    server.shutdown()
                    logger.error(f'No available manager.')
                    raise ConnectionRefusedError

                logger.info(f'TCPServer started at {ip}:{port}.')
                t.join()
            except Exception as err:
                logger.warning(
                    f'TCPServer starts failed on {ip}:{port}, {err}.')
                continue
        logger.error(f'TCPServer can not start.')
        return


worker = Worker()

class Handler_TCPServer(socketserver.BaseRequestHandler):
    """ The TCP Server class for demonstration.
    Note: We need to implement the Handle method to exchange data
    with TCP client. """

    def sendback(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        self.request.sendall(msg)

    def response(self):
        receive = json.loads(self.data)
        if not worker.idle:
            self.sendback('Ignoring the request, since I am busy.')
            return

        if receive.get('cmd', None) == 'work':
            if receive.get('n', None) is not None:
                try:
                    n = int(receive['n'])
                    assert(n > 0)
                except Exception as err:
                    self.sendback(f'Illegal request {err}.')
                    return
                worker.workload(n)
                self.sendback('Doing work as required.')
                return

        self.sendback('Unrecognized request, Ignoring it.')

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.info('Receive {} from {}'.format(
            self.data, self.client_address))
        self.response()


if __name__ == '__main__':
    worker.start_listening(Handler_TCPServer)
    print ('This window will close in 5 seconds.')
    time.sleep(5)