""" TCP server of BCI. """
import time
import json
import socket
import threading
import traceback
from logger import Logger
from worker import Worker
from profile import IP, PORT, BUF_SIZE, RealtimeReply

logger = Logger(name='server').logger
worker = Worker()
rtreply = RealtimeReply()


def delay(timestamp):
    """ Calculate delay based on [timestamp] """
    return time.time() - float(timestamp)


class Server():
    def __init__(self):
        # Init server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen(1)
        # Init clients pool
        self._clientpool = []
        # self.starts()

    @property
    def clientpool(self):
        return self._clientpool

    @clientpool.getter
    def clientpool(self):
        self._clientpool = [c for c in self._clientpool
                            if not c.client._closed]
        return self._clientpool

    def pprint(self):
        print('-' * 80)
        [c.pprint() for c in self.clientpool]

    def starts(self):
        """ Start serving. """
        self.server.listen(1)
        t = threading.Thread(target=self.maintain_clients, name='TCP server')
        t.setDaemon(True)
        t.start()
        logger.info(f'Server started.')

    def maintain_clients(self):
        """ Maintain clients pool. """
        while True:
            client = Client(client=self.new_client())
            self.clientpool.append(client)
            logger.info(f'New client accepted {client}')

    def new_client(self):
        """ Accept new incoming client. """
        client, address = self.server.accept()
        return client


class Client():
    def __init__(self, client, onclose=None):
        """ Start [client] for listening,
        [onclose] is a function that will be called when client is closed."""
        # Setup client and onclose handler
        self.client = client
        if onclose is None:
            self.onclose = self.default_onclose
        else:
            self.onclose = onclose
        # Start listening
        t = threading.Thread(target=self.listening)
        t.setDaemon(True)
        t.start()
        logger.info(f'New client started {self.client}')

    def default_onclose(self):
        """ Default onclose handler. """
        pass

    def pprint(self):
        """ Report the client. """
        print(self.client.__str__(), self.client._closed)

    def send(self, msg):
        """ Send [msg] to self.client. """
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        self.client.sendall(msg)
        logger.debug(f'Sent {msg} to {self.client}')

    def listening(self):
        """ Listening. """
        while True:
            try:
                data = self.client.recv(BUF_SIZE)
                logger.info(f'Received {data}, from {self.client}')
                # If empty package received, it means the client to be closed.
                assert(not data == b'')
                # todo: Handle data received event.
                # Parse data using JSON format
                try:
                    D = json.loads(data.decode())
                except:
                    self.send(rtreply.ParseError())
                    logger.debug(f'{data} can not be loaded by JSON')
                    continue
                print(D)
                # Make sure D is legal
                # D is dict
                if not isinstance(D, dict):
                    self.send(rtreply.ParseError())
                    logger.debug(f'{D} is not dict')
                    continue
                # D contains timestamp
                if 'timestamp' not in D:
                    self.send(rtreply.ParseError())
                    logger.debug(f'{D} contains no timestamp')
                    continue
                logger.debug('Delay is {}'.format(delay(D['timestamp'])))
                # D contains mode, [cmd], and worker can deal with them
                if 'mode' not in D:
                    self.send(rtreply.ParseError())
                    logger.debug(f'{D} contains no mode')
                    continue

                if 'cmd' in D:
                    workload = '{mode}_{cmd}'.format(**D).lower()
                else:
                    workload = '{mode}'.format(**D).lower()
                if not hasattr(worker, workload):
                    self.send(rtreply.ParseError())
                    logger.debug(f'{D} triggers no workload')
                    continue

                self.send(rtreply.OK())

            except:
                traceback.print_exc()
                # Close the client
                self.client.close()
                self.onclose()
                # Stop listening
                break
        logger.info(f'Connection closed {self.client}.')


if __name__ == '__main__':
    server = Server()
    server.starts()
    while True:
        msg = input('>> ')

        if msg == 'q':
            break

        if not msg == '':
            for c in server.clientpool:
                c.client.sendall(msg.encode())
            continue

        server.pprint()
    print('ByeBye.')
