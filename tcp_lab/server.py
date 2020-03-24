import time
import socket
import threading
import traceback
from profile import IP, PORT, BUF_SIZE
from logger import default_logger as logger

num_clients = 1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(num_clients)


def accept_client():
    """ Start server by accepting new client connection """
    logger.info('Server starts listening.')
    client, address = server.accept()
    logger.info(f'Connection established: {client}')
    return client


class Client():
    def __init__(self, client):
        self.client = client

    def pprint(self):
        print(self.client.__str__(), self.client._closed)

    def starts(self):
        t = threading.Thread(target=self.listen)
        t.start()

    def listen(self):
        while True:
            try:
                data = self.client.recv(BUF_SIZE)
                logger.info(f'Server received {data}, from {self.client}')
                if data == b'':
                    raise Exception('Empty received.')
            except:
                self.client.close()
                traceback.print_exc()
                break
                # self.client = accept_client()


clients = []
while True:  # len(clients) < num_clients:
    client = Client(accept_client())
    client.starts()
    clients.append(client)
    print('-' * 80)
    clients = [c for c in clients if not c.client._closed]
    [c.pprint() for c in clients]

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
    input('Enter to escape.')
