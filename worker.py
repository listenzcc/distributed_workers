""" I am a worker,
I maintain a TCP server to listen. """

import tqdm
import time
import json
import socket
import socketserver
import threading
from profiles import HOST, HOST_PORT, PORT_RANGE, logger
from toolbox import get_local_ip


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

    def workload(self, n=5):
        """ Start a thread for self._workload_. """
        assert(isinstance(n, int))
        assert(n > 0)
        if not self.remaining == -1:
            logger.warning('Workload can not be set, since I am busy')
            return 1
        t = threading.Thread(target=self._workload_, args=(n,))
        t.start()
        return 0

    def send(self, msg=time.ctime(), host=HOST, port=HOST_PORT):
        """ Send [msg] to [host]:[port] """
        if not isinstance(msg, type(b'hello')):
            msg = str(msg).encode()
        assert(all([isinstance(host, type('127.0.0.1')),
                    isinstance(port, type(65536)),
                    isinstance(msg, type(b'hello'))]))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, port))
            client.sendall(msg)
            received = client.recv(1024)
            print(received)
        finally:
            client.close()

    def start_serve(self, handler, port_range=PORT_RANGE):
        host = self.local_ip
        for port in port_range:
            try:
                server = socketserver.TCPServer(
                    (host, port), handler)
                t = threading.Thread(target=server.serve_forever)
                t.start()
                logger.info(f'TCPServer started at {host}:{port}.')
                t.join()
            except Exception as e:
                logger.warning(f'TCPServer starts failed on {host}:{port}, {repr(e)}.')
                continue
        logger.error(f'TCPServer can not start.')


worker = Worker()


class Handler_TCPServer(socketserver.BaseRequestHandler):
    """ The TCP Server class for demonstration.
    Note: We need to implement the Handle method to exchange data
    with TCP client. """

    def response(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        self.request.sendall(msg)

    def parse(self, data):
        receive = json.loads(data)
        if not worker.idle:
            self.response('I am busy, Ignoring the request.')
            return
        if receive.get('cmd', None) == 'work':
            if receive.get('n', None) is not None:
                worker.workload(receive['n'])
                self.response('Doing work as required.')
                return
        self.response('Unrecognized request, Ignoring it.')

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.info('Receive {} from {}'.format(self.data, self.client_address[0]))
        print(self.client_address)
        self.parse(self.data)


if __name__ == '__main__':
    worker.start_serve(Handler_TCPServer)