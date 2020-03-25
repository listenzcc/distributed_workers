import time
import socket
import threading
import traceback
from profile import IP, PORT, BUF_SIZE
from logger import default_logger as logger


class Server():
    def __init__(self):
        # Init server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen(1)
        # Init clients pool
        self.clients = []
        # self.starts()

    def refresh(self, silent=False):
        """ Refresh clients pool """
        self.clients = [c for c in self.clients if not c.client._closed]
        if not silent:
            print('-' * 80)
            [c.pprint() for c in self.clients]

    def starts(self):
        """ Start serving """
        t = threading.Thread(target=self.maintain_clients)
        t.start()

    def accept_client(self):
        """ Start server by accepting new client connection """
        logger.info('Server starts listening.')
        client, address = self.server.accept()
        logger.info(f'Connection established: {client}')
        return client

    def maintain_clients(self):
        """ Maintain clients pool """
        while True:
            # When new connection established,
            # make new client
            client = Client(self.accept_client(), self.refresh)
            client.starts()
            # append into clients pool
            self.clients.append(client)
            # Refresh
            self.refresh()


class Client():
    def __init__(self, client, foo):
        """ Init,
        client: client connection,
        foo: refresh function of 3rd party """
        self.client = client
        self.foo = foo

    def pprint(self):
        """ Print client str. """
        print(self.client.__str__(), self.client._closed)

    def starts(self):
        """ Start listening. """
        t = threading.Thread(target=self.listen)
        t.start()

    def listen(self):
        """ Listening server. """
        while True:
            try:
                data = self.client.recv(BUF_SIZE)
                logger.info(f'Server received {data}, from {self.client}')
                self.client.sendall(f'Server received {data}'.encode())
                if data == b'':
                    raise Exception('Empty received.')
            except:
                self.client.close()
                self.foo()
                # traceback.print_exc()
                break
                # self.client = accept_client()


server = Server()
server.starts()

# while True:
#     try:
#         data = client.recv(BUF_SIZE)
#         # If receive empty data, raise an exception
#         if data == b'':
#             raise Exception('Empty received.')
#         logger.info(f'Server received {data}, from {client}')
#     except Exception:
#         traceback.print_exc()
#         # Re-server if current client fails
#         client = accept_client()

if __name__ == '__main__':
    while True:
        # Wait input
        msg = input('>> ')

        # Empty msg
        if msg == '':
            server.refresh()
            continue

        # Send message
        if not msg == '':
            for c in server.clients:
                c.client.sendall(msg.encode())
