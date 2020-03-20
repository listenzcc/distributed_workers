""" Listen on TCP port,
and check the check_table. """

import json
import time
import threading
import socketserver
import trace

from check_table import CheckTable
from profile import IP, PORT, logging

ct = CheckTable()

ct.pprint()


class Handler_TCPServer(socketserver.BaseRequestHandler):
    """ TCP Server class. """

    def sendback(self, msg):
        """ Send back [msg]. """
        if isinstance(msg, str):
            msg = msg.encode()
        self.request.sendall(msg)

    def do_GET(self):
        """ do on GET something. """
        received = json.loads(self.data)
        ct.add(received)
        ct.pprint()
        print('Press ENTER to escape.')
        self.sendback('OK')

    def handle(self):
        """ Handle TCP socket request. """
        self.data = self.request.recv(1024).strip()
        logging.debug('Receive {} from {}'.format(
            self.data, self.client_address))
        self.do_GET()


class Server():
    def __init__(self):
        pass

    def serve_forever(self):
        try:
            server = socketserver.TCPServer((IP, PORT), Handler_TCPServer)
            t = threading.Thread(target=server.serve_forever)
            t.start()
            self.server = server
            logging.info(f'TCPServer started at {IP}:{PORT}.')
        except Exception as err:
            logging.warning(f'TCPServer failed on starting. {err}')

    def shutdown(self):
        try:
            self.server.server_close()
            self.server.shutdown()
        finally:
            print('ByeBye.')


server = Server()
if __name__ == "__main__":
    server.serve_forever()
    input('Press ENTER to escape.')
    server.shutdown()
