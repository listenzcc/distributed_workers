""" TCP server of BCI. """
import os
import sys
import time
import json
import socket
import threading
import traceback

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa

from worker import Worker
from local_profile import IP, PORT, BUF_SIZE
from local_profile import logger, RealtimeReply, RuntimeError
from local_profile import USE_BACKEND, IP_EEG_DEVICE, PORT_EEG_DEVICE
from backend_toolbox import new_backend
import local_profile
CurrentDirectory = os.path.dirname(local_profile.__file__)

logger.info('---- New Session ----')
logger.info('---- Version 2020-05-29 ----')


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

    def send(self, msg, encoding='utf-8'):
        """Send [msg] to connected TCP Client

        Arguments:
            msg {str} -- [description]
        """
        # Dumps dict
        if isinstance(msg, dict):
            msg = json.dumps(msg, ensure_ascii=False).encode(encoding)

        # Encode str
        if isinstance(msg, str):
            msg = msg.encode(encoding)

        # Send
        self.client.sendall(msg)
        logger.info(f'Sent {msg} to {self.address}')
        logger.debug(f'Sent {msg} to {self.address}')

    def deal(self, D):
        """Deal with incoming message

        Arguments:
            D {dict} -- Parsed message dictionary
        """
        # Make sure D is legal,
        # send ParseError if illegal
        # D is dict
        if not isinstance(D, dict):
            self.send(real_time_reply.ParseError())
            logger.error(f'{D} is not dict')
            return 1

        logger.debug(f'Dealing with {D}')

        # D contains timestamp
        if 'timestamp' not in D:
            self.send(real_time_reply.ParseError())
            logger.error(f'{D} contains no timestamp')
            return 1

        # Record Delay
        logger.debug('Delay is {}'.format(delay(D['timestamp'])))

        # D contains 'mode', ['cmd'], and worker can deal with them
        # D contains 'mode'
        if 'mode' not in D:
            self.send(real_time_reply.ParseError())
            logger.error(f'{D} contains no mode')
            return 1

        # Deal with 'cmd' if it exists
        if 'cmd' in D:
            workload = '{mode}_{cmd}'.format(**D).lower()
        else:
            workload = '{mode}'.format(**D).lower()

        # Worker can deal with them
        if not hasattr(worker, workload):
            self.send(real_time_reply.ParseError())
            logger.error(f'{D} triggers no workload')
            return 1

        # Get ride of 'mode' and ['cmd']
        D.pop('mode')
        D.pop('cmd', None)

        # Operate
        logger.debug(f'Workload starts {workload}')
        try:
            eval(f'worker.{workload}(**D, send=self.send)')
            return 0
        except Exception as e:
            logger.error(
                f'Something went wrong in workload {workload}')
            logger.debug(traceback.format_exc())
            self.send(runtime_error.UnknownError(detail=e.__str__()))
            return 1

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
                # Decode data
                try:
                    decoded_data = data.decode('utf-8')
                except:
                    logger.info(f'{data} can not be decoded.')
                    logger.debug(f'{data} can not be decoded.')
                    continue

                # send ParseError if parsing is failed
                try:
                    D = json.loads(decoded_data)
                except:
                    logger.debug(
                        f'{decoded_data} can not be loaded by JSON, try linked expection.')
                    try:
                        split = decoded_data.split('}{')

                        D = list()
                        for s in split:
                            if not s.startswith('{'):
                                s = '{' + s
                            if not s.endswith('}'):
                                s = s + '}'
                            D.append(json.loads(s))
                        logger.debug(f'Link exception success: {D}.')
                    except:
                        logger.error(
                            f'{decoded_data} can not be loaded by JSON')
                        logger.error('{}'.format(traceback.format_exc()))
                        self.send(real_time_reply.ParseError(
                            detail=decoded_data))
                        continue
                # print(D)

                # Deal with D
                if isinstance(D, list):
                    for d in D:
                        self.deal(d)
                else:
                    self.deal(D)

            except Exception:
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

    if USE_BACKEND:
        print(CurrentDirectory)
        new_backend(working_directory=os.path.join(CurrentDirectory, 'local_backend'),
                    IP=IP,
                    PORT=PORT,
                    IP_EEG_DEVICE=IP_EEG_DEVICE,
                    PORT_EEG_DEVICE=PORT_EEG_DEVICE)

    while True:
        msg = input('>> ')

        if msg == 'q':
            break

        if not msg == '':
            for c in server.clientpool:
                c.send(f'- | {msg} |', )  # encoding='ansi')
            continue

        server.pprint()
    print('ByeBye.')
