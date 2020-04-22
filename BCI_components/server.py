""" TCP server of BCI. """
import time
import json
import socket
import threading
import traceback
from worker import Worker
from profile import IP, PORT, BUF_SIZE, logger, RealtimeReply, RuntimeError

logger.info('---- New Session ----')

# Worker instance
worker = Worker()
# Real-time reply instance
real_time_reply = RealtimeReply()
# runtime error instance
runtime_error = RuntimeError()


def reg_timestamp(timestamp, tmp=time.time()):
    """Regularize time stamp and rescale it into time.time()

    Arguments:
        timestamp {object} -- Input time stamp.

    Keyword Arguments:
        tmp {float} -- Default correct time stamp (default: {time.time()})

    Returns:
        {float} -- Regularized timestamp
    """
    ts = float(timestamp)
    # Length of input
    a = len(str(ts).split('.')[0])
    # Length of template
    b = len(str(tmp).split('.')[0])
    # Re-scale
    return ts * (10 ** (b-a))


def delay(timestamp):
    """Calculate delay based on [timestamp]

    Arguments:
        timestamp {str} -- timestamp

    Returns:
        {float} -- Calculated delay
    """

    now = time.time()
    try:
        t = reg_timestamp(timestamp, now)
    except Exception as err:
        logger.error(f'Computing delay met error: {err}')
        t = now
    finally:
        return now - t


class Server():
    """TCP Server """

    def __init__(self, ip=IP, port=PORT):
        """Default init

        Keyword Arguments:
            ip {str} -- Legal IP address, like 'localhost' or '127.0.0.1' (default: {IP})
            port {int} -- Legal port, like 65535 (default: {PORT})
        """
        # Init server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        logger.info(f'TCP Server is parepared listening on {ip}:{port}')
        # self.server.listen(1)
        # Init clients pool
        self._clientpool = []
        # self.starts()

    @property
    def clientpool(self):
        return self._clientpool

    @clientpool.getter
    def clientpool(self):
        """Get clientpool

        Returns:
            {list} -- List of active client threads
        """
        self._clientpool = [c for c in self._clientpool
                            if not c.client._closed]
        return self._clientpool

    def pprint(self):
        """Report active client threads
        """
        print('-' * 80)
        [c.pprint() for c in self.clientpool]

    def starts(self):
        """ Start serving """
        self.server.listen(1)
        t = threading.Thread(target=self.maintain_clients, name='TCP server')
        t.setDaemon(True)
        t.start()
        logger.info(f'TCP Server started.')

    def maintain_clients(self):
        """ Maintain clients pool. """
        while True:
            # Wait for new client
            c, a = self.new_client()
            # New client instance
            client = Client(client=c, address=a)
            # Add new client into client pool
            self.clientpool.append(client)
            logger.info(f'New client accepted {a}')

    def new_client(self):
        """ Accept new incoming client. """
        client, address = self.server.accept()
        return client, address


class Client():
    """Connected TCP Client """

    def __init__(self, client, address, onclose=None):
        """Start [client] for listening at [address],
        [onclose] is a function that will be called when client is closed.

        Arguments:
            client {Client instance} -- The connected TCP Client
            address {str} -- Address str

        Keyword Arguments:
            onclose {func} -- Method will be called when client is closed (default: {None})
        """
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
        logger.info(f'New client started {address}')

    def default_onclose(self):
        """ Default onclose handler. """
        # Do nothing
        pass

    def pprint(self):
        """ Report the client. """
        print(self.client.__str__(), self.client._closed)

    def send(self, msg):
        """Send [msg] to connected TCP Client

        Arguments:
            msg {str} -- [description]
        """
        # Dumps dict
        if isinstance(msg, dict):
            msg = json.dumps(msg)

        # Encode str
        if isinstance(msg, str):
            msg = msg.encode('utf-8')

        # Send
        self.client.sendall(msg)
        logger.info(f'Sent {msg} to {self.address}')
        logger.debug(f'Sent {msg} to {self.address}')

    def listening(self):
        """ Listen and handling incoming message """
        while True:
            try:
                # Get data
                data = self.client.recv(BUF_SIZE)
                logger.info(f'Received {data}, from {self.address}')
                logger.debug('{dash} New data received {dash}'.format(
                    dash='-' * 8))
                logger.debug(f'Received {data}, from {self.address}')

                # If empty package received, it means the client to be closed.
                assert(not data == b'')

                # Parse data using JSON format,
                # send ParseError if parsing is failed
                try:
                    D = json.loads(data.decode())
                except:
                    self.send(real_time_reply.ParseError())
                    logger.error(f'{data} can not be loaded by JSON')
                    continue
                # print(D)

                # Make sure D is legal,
                # send ParseError if illegal
                # D is dict
                if not isinstance(D, dict):
                    self.send(real_time_reply.ParseError())
                    logger.error(f'{D} is not dict')
                    continue

                # D contains timestamp
                if 'timestamp' not in D:
                    self.send(real_time_reply.ParseError())
                    logger.error(f'{D} contains no timestamp')
                    continue

                # Record Delay
                logger.debug('Delay is {}'.format(delay(D['timestamp'])))

                # D contains 'mode', ['cmd'], and worker can deal with them
                # D contains 'mode'
                if 'mode' not in D:
                    self.send(real_time_reply.ParseError())
                    logger.error(f'{D} contains no mode')
                    continue

                # Deal with 'cmd' if it exists
                if 'cmd' in D:
                    workload = '{mode}_{cmd}'.format(**D).lower()
                else:
                    workload = '{mode}'.format(**D).lower()

                # Worker can deal with them
                if not hasattr(worker, workload):
                    self.send(real_time_reply.ParseError())
                    logger.error(f'{D} triggers no workload')
                    continue

                # Get ride of 'mode' and ['cmd']
                D.pop('mode')
                D.pop('cmd', None)

                # Operate
                logger.debug(f'Workload starts {workload}')
                try:
                    eval(f'worker.{workload}(**D, send=self.send)')
                except Exception as e:
                    logger.error(
                        f'Something went wrong in workload {workload}')
                    logger.debug(traceback.format_exc())
                    self.send(runtime_error.UnknownError(detail=e.__str__()))

            except Exception as e:
                traceback.print_exc()
                logger.debug(traceback.format_exc())
                # Close the client
                self.client.close()
                # Stop listening
                break

        # Run onclose function
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
