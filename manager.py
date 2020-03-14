""" Manager of servers """

import socketserver
import threading
from profiles import HOST, HOST_PORT, logger


class Manager():
    def __init__(self):
        self.start_worker_server()

    def start_worker_server(self):
        pass



class Handler_Worker_TCPServer(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        # just send back ACK for data arrival confirmation
        self.request.sendall("ACK from TCP Server".encode())