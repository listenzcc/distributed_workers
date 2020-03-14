""" Start a TCP server. """

import socketserver
import threading
from profiles import HOST, PORT_RANGE, logger


class Handler_TCPServer(socketserver.BaseRequestHandler):
    """ The TCP Server class for demonstration.
    Note: We need to implement the Handle method to exchange data
    with TCP client. """
    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        # just send back ACK for data arrival confirmation
        self.request.sendall("ACK from TCP Server".encode())


def new_TCPServer():
    """ Find a useable PORT,
    and start a TCP server. """
    for PORT in PORT_RANGE:
        try:
            tcp_server = socketserver.TCPServer((HOST, PORT),
                                                Handler_TCPServer)
            t = threading.Thread(target=tcp_server.serve_forever)
            t.start()
            logger.info(f'TCPServer started at {HOST}: {PORT}.')
            # todo: report to caller, a server started.
            t.join()
        except Exception as e:
            logger.warning(f'TCPServer starts failed on {HOST}: {PORT}, {repr(e)}')
            continue
    logger.error(f'TCPServer can not start.')
    return None


if __name__ == '__main__':
    new_TCPServer()