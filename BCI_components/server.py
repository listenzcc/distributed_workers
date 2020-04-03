""" TCP server of BCI. """
import time
import json
import socket
import threading
import traceback
from worker import Worker
from profile import IP, PORT, BUF_SIZE, logger, RealtimeReply

logger.info('---- New Session ----')

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
            c, a = self.new_client()
            client = Client(client=c, address=a)
            self.clientpool.append(client)
            logger.info(f'New client accepted {a}')

    def new_client(self):
        """ Accept new incoming client. """
        client, address = self.server.accept()
        return client, address


class Client():
    def __init__(self, client, address, onclose=None):
        """ Start {client} for listening at {address},
        {onclose} is a function that will be called when client is closed."""
        # Setup client and onclose handler
        self.client = client
        self.address = address
        if onclose is None:
            self.onclose = self.default_onclose
        else:
            self.onclose = onclose
        # Start listening
        t = threading.Thread(target=self.listening)
        t.setDaemon(True)
        t.start()
        logger.info(f'New client started {self.address}')

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
        logger.info(f'Sent {msg} to {self.address}')

    def listening(self):
        """ Listening. """
        while True:
            try:
                data = self.client.recv(BUF_SIZE)
                logger.info(f'Received {data}, from {self.address}')
                # If empty package received, it means the client to be closed.
                assert(not data == b'')
                # todo: Handle data received event.
                # Parse data using JSON format
                try:
                    D = json.loads(data.decode())
                except:
                    self.send(rtreply.ParseError())
                    logger.error(f'{data} can not be loaded by JSON')
                    continue
                # print(D)
                # Make sure D is legal
                # D is dict
                if not isinstance(D, dict):
                    self.send(rtreply.ParseError())
                    logger.error(f'{D} is not dict')
                    continue
                # D contains timestamp
                if 'timestamp' not in D:
                    self.send(rtreply.ParseError())
                    logger.error(f'{D} contains no timestamp')
                    continue
                logger.debug('Delay is {}'.format(delay(D['timestamp'])))
                # D contains mode, [cmd], and worker can deal with them
                if 'mode' not in D:
                    self.send(rtreply.ParseError())
                    logger.error(f'{D} contains no mode')
                    continue

                if 'cmd' in D:
                    workload = '{mode}_{cmd}'.format(**D).lower()
                else:
                    workload = '{mode}'.format(**D).lower()
                if not hasattr(worker, workload):
                    self.send(rtreply.ParseError())
                    logger.error(f'{D} triggers no workload')
                    continue

                D.pop('mode')
                D.pop('cmd', None)

                logger.debug(f'Workload starts {workload}')
                try:
                    eval(f'worker.{workload}(**D, send=self.send)')
                except:
                    logger.error(
                        f'Something went wrong in workload {workload}')
                    logger.debug(traceback.format_exc())
                    self.send(rtreply.ParseError())

                # self.send(rtreply.OK())

            except:
                traceback.print_exc()
                # Close the client
                self.client.close()
                # Stop listening
                break
        self.onclose()
        logger.info(f'Connection closed {self.client}.')


if __name__ == '__main__':
    server = Server()
    worker.get_ready()
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
