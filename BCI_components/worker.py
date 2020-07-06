""" BCI worker. """

import os
import sys
import time
import threading
import traceback

print(__file__)  # noqa
sys.path.append(os.path.dirname(__file__))  # noqa
from local_profile import RealtimeReply, RuntimeError, USE_BACKEND, logger

# Real-time reply instance
real_time_reply = RealtimeReply()
# runtime error instance
runtime_error = RuntimeError()


def mkdir(path):
    """Recursive (safe) mkdir function,
    use 1: Create [path],
    use 2: Check [path] is an already existing dir

    Arguments:
        path {str} -- Path to be created, it should be a legal dir path.
    """
    # Mkdir if not exists
    if not os.path.exists(path):
        s = os.path.split(path)
        # Recursive create parent
        if s[0]:
            mkdir(s[0])
        # Mkdir child
        os.mkdir(path)
        logger.debug(f'Created {path}')
    # Make sure path is a folder
    assert(os.path.isdir(path))


def send(msg):
    """ Virtual sending method,
    used when sending method is not provided.

    Arguments:
        msg {object} -- Message to be recorded.
    """
    logger.debug(f'Virtual send {msg}')


def onerror(error, detail, send=send):
    """ Handle runtime errors,
    logging and send RuntimeError,
    normally THIS should be followed by return 1.

    Arguments:
        error {RuntimeError func} -- Method for RuntimeError instance
        detail {object} -- Detail of the error.
        send {func} -- Send function to be used for Error report. (default: {send})
    """
    logger.error(detail)
    # Load [detail] into [error]
    errormsg = error(detail)
    # Send [errormsg]
    send(errormsg)
    logger.debug(f'Sent RuntimeError: {errormsg}')


class Worker():
    """Worker for operations. """

    def __init__(self):
        # The current STATE
        self._state = 'Busy'
        # The labels of estimated and true labels
        self._labels = []
        # Setup default send_backend as send
        if not USE_BACKEND:
            self.send_backend = send

    def get_ready(self, state='Idle', moxinglujing=None, shujulujing=None, send_UI=send):
        """Get ready for comming operation,
        switch STATE into 'Idle',
        empty LABELS,
        when STATE is switch into 'Online', make sure it has a valid send_UI.

        Keyword Arguments:
            state {str} -- Witch STATE will be set. (default: {'Idle'})
            moxinglujing {str} -- The path of model. (default: {None})
            shujulujing {str} -- The path of data. (default: {None})
            send_UI {func} -- Method of send_ui, means send to UI TCP client, to tell UI something when income TCP client may not be UI. (default: {send})
        """

        self.state = state
        self._labels = []
        self.moxinglujing = moxinglujing
        self.shujulujing = shujulujing
        self.send_UI = send_UI
        logger.info(f'Worker is ready to go, {state}.')

    def accuracy(self):
        """Calculate accuracy based on LABEL

        Returns:
            {float} -- accuracy
        """
        total = len(self.labels)
        correct = len([e for e in self.labels if e[0] == e[1]])
        return correct / total

    @property
    def labels(self):
        return self._labels

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, s):
        """Safe switch STATE into [s]

        Arguments:
            s {str} -- The name of new state, one from ['Idle', 'Busy', 'Online', 'Offline']
        """
        assert(s in ['Idle', 'Busy', 'Online', 'Offline'])
        if not s == self._state:
            self._state = s
            logger.info(f'State switched to {s}.')
            logger.debug(f'State switched to {s}.')

    def check_state(self, states, workload, send=send):
        """Check wether current state is in [states]

        Arguments:
            states {str} or {list} -- Legal states
            workload {str} -- Name of workload, used for potential onerror message

        Keyword Arguments:
            send {func} -- Send function to be used for onerror (default: {send})

        Returns:
            {int} -- 0 for correct, 1 for error
        """
        # Make sure states is iterable
        if isinstance(states, str):
            states = [states]
        # If current state is not in states,
        # means incorrect,
        # send error message.
        if self.state in states:
            return 0
        else:
            onerror(runtime_error.StateError,
                    f'Wrong state {self.state} for {workload}',
                    send=send)
            return 1

    def accept_backend(self, timestamp=0, send=send):
        self.send_backend = send
        logger.info('Backend connection established.')
        pass

    def response_query(self, gujibiaoqian, timestamp=0, send=send):
        self.latest_query_send(dict(mode='QueryReply',
                                    gujibiaoqian=gujibiaoqian,
                                    timestamp=time.time()))

        zhenshibiaoqian = self.latest_zhenshibiaoqian
        if all([gujibiaoqian == '1',
                zhenshibiaoqian == '1']):
            self.send_UI(dict(mode='Online',
                              cmd='kaishiyundong',
                              timestamp=time.time()))

        self.labels.append((gujibiaoqian, zhenshibiaoqian))
        logger.info(
            f'Estimated label: {gujibiaoqian}, True label: {zhenshibiaoqian}')
        logger.debug(
            f'Estimated label: {gujibiaoqian}, True label: {zhenshibiaoqian}')
        logger.debug(f'Labels is {self.labels}')

        pass

    def response_jianmo(self, zhunquelv, timestamp=0, send=send):
        moxinglujing = self.latest_moxinglujing
        shujulujing = self.latest_shujulujing

        self.latest_jianmo_send(dict(mode='Offline',
                                     cmd='zhunquelv',
                                     moxinglujing=moxinglujing,
                                     zhunquelv=zhunquelv,
                                     timestamp=time.time()))

        if not USE_BACKEND:
            print('-' * 80)
            print(moxinglujing)
            with open(moxinglujing, 'w') as f:
                f.writelines(['Fake model.'])

        logger.debug(
            f'Built model based on {shujulujing}, model has been saved in {moxinglujing}.')
        logger.info(
            f'Built model based on {shujulujing}, model has been saved in {moxinglujing}.')

        pass

    def force_Idle(self):
        """Force State to Idle, used for kaishicaiji by-force.
        """
        if self.state == 'Idle':
            return 0

        msg = f'Current state is {self.state}, setting it to Idle by-force.'
        logger.info(msg)
        logger.debug(msg)

        # Stop backend
        logger.debug('Send jieshucaiji to backend.')
        try:
            self.send_backend(dict(cmd='jieshucaiji'))
        except:
            logger.info('Fail to stop offline recording in backend.')
            traceback.print_exc()

        # workload
        self.state = 'Idle'

    def offline_kaishicaiji(self, shujulujingqianzhui, timestamp=0, send=send):
        """Start offline collection

        Arguments:
            shujulujingqianzhui {str} -- The prefix of data path, '.cnt' will be added for real data path

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 for success, 1 for fail
        """
        # Send OK means I has got everything in need,
        # but not guartee that all the things are correct,
        # if incorrect, I will reply Error in further
        send(real_time_reply.OK())

        # The state should be 'Idle'
        self.force_Idle()
        if self.check_state('Idle', 'offline_kaishicaiji', send=send) == 1:
            return 1

        # Try to mkdir and check of [shujulujingqianzhui] dir
        try:
            mkdir(os.path.dirname(shujulujingqianzhui))
        except:
            onerror(runtime_error.FileError, shujulujingqianzhui, send=send)
            return 1

        # Workload
        self.get_ready(state='Offline')
        path = f'{shujulujingqianzhui}.mat'

        if not USE_BACKEND:
            self._shujulujing = path

        try:
            self.send_backend(dict(cmd='kaishicaiji',
                                   mat_path=path,
                                   model_path='[empty]'))
        except:
            logger.info('Fail to start offline recording in backend.')
            traceback.print_exc()

        # Start self.record function as separate daemon threading
        # t = threading.Thread(target=self.record, args=(path,))
        # t.setDaemon(True)
        # t.start()

        logger.debug('Started offline collection.')
        return 0

    def offline_jieshucaiji(self, timestamp=0, send=send):
        """Stop offline collection

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 means success, 1 means fail
        """
        send(real_time_reply.OK())

        # The state should be 'Offline'
        if self.check_state('Offline', 'offline_jieshucaiji', send=send) == 1:
            return 1

        # workload
        self.state = 'Idle'

        # Stop backend
        try:
            self.send_backend(dict(cmd='jieshucaiji'))
        except:
            logger.info('Fail to stop offline recording in backend.')
            traceback.print_exc()

        if not USE_BACKEND:
            with open(self._shujulujing, 'w') as f:
                f.writelines(['Fake data.'])

        logger.debug('Stopped offline collection.')
        return 0

    def offline_jianmo(self, shujulujing, moxinglujingqianzhui, timestamp=0, send=send):
        """Start building model for offline data

        Arguments:
            shujulujing {str} -- The offline data
            moxinglujingqianzhui {str} -- The prefix of model path, '.mat' will be added for real mpdel path

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 means success, 1 means fail
        """
        send(real_time_reply.OK())

        # The state should be 'Idle'
        if self.check_state('Idle', 'offline_jianmo', send=send) == 1:
            return 1

        # Check {shujulujing}
        if not os.path.exists(shujulujing):
            onerror(runtime_error.FileError, shujulujing, send=send)
            return 1

        # Try to mkdir and check of [moxinglujingqianzhui]
        try:
            mkdir(os.path.dirname(moxinglujingqianzhui))
        except:
            onerror(runtime_error.FileError, moxinglujingqianzhui, send=send)
            return 1

        # Workload
        moxinglujing = f'{moxinglujingqianzhui}.mat'

        # todo: Building a model
        self.latest_jianmo_send = send
        self.latest_shujulujing = shujulujing
        self.latest_moxinglujing = moxinglujing
        try:
            self.send_backend(dict(cmd='jianmo',
                                   moxinglujing=moxinglujing,
                                   shujulujing=shujulujing))
        except:
            logger.info('Fail on sending jianmo request to backend.')

        # If not USE_BACKEND,****************************************
        # use response_jianmo
        if not USE_BACKEND:
            self.response_jianmo(zhunquelv="1.0", timestamp=0, send=send)

        logger.debug('Building model.')
        logger.info('Building model.')

        return 0

    def online_kaishicaiji(self, moxinglujing, shujulujingqianzhui, timestamp=0, send=send):
        """Start Online collection

        Arguments:
            moxinglujing {str} -- The path of model, it should be an existing path
            shujulujingqianzhui {str} -- The prefix of data path, '.cnt' will be added in real data path

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 for success, 1 for fail
        """
        send(real_time_reply.OK())

        # Check moxinglujing
        if not os.path.exists(os.path.dirname(moxinglujing)):
            onerror(runtime_error.FileError, moxinglujing, send=send)
            return 1

        # Try to mkdir and check of {shujulujingqianzhui}
        try:
            mkdir(os.path.dirname(shujulujingqianzhui))
        except:
            onerror(runtime_error.FileError, shujulujingqianzhui, send=send)
            return 1

        # The state should be 'Idle'
        self.force_Idle()
        if self.check_state('Idle', 'online_kaishicaiji', send=send) == 1:
            return 1

        # Workload
        path = f'{shujulujingqianzhui}.mat'

        if not USE_BACKEND:
            self._shujulujing = path

        # Remember Send-to-UI method,
        # as Start online collection can only be triggered by UI.
        self.get_ready(state='Online',
                       moxinglujing=moxinglujing,
                       shujulujing=path,
                       send_UI=send)

        try:
            self.send_backend(dict(cmd='kaishicaiji',
                                   mat_path=path,
                                   model_path=moxinglujing))
        except:
            logger.info('Fail to start online recording in backend.')
            traceback.print_exc()

        # Start daemon thread for data collection and start it
        # t = threading.Thread(target=self.record, args=(path, moxinglujing))
        # t.setDaemon(True)
        # t.start()

        logger.debug('Started online collection.')
        return 0

    def online_jieshucaiji(self, timestamp=0, send=send):
        """Stop online collection

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method. (default: {send})

        Returns:
            {int} -- 0 for success, 1 for fail
        """
        send(real_time_reply.OK())

        # The state should be 'Online'
        if self.check_state('Online', 'online_jieshucaiji', send=send) == 1:
            return 1

        # Workload

        # Stop backend
        try:
            self.send_backend(dict(cmd='jieshucaiji'))
        except:
            logger.info('Fail to stop offline recording in backend.')
            traceback.print_exc()

        if not USE_BACKEND:
            with open(self._shujulujing, 'w') as f:
                f.writelines(['Fake online data.'])

        # Calculate accuracy
        try:
            zhunquelv = self.accuracy()
            logger.debug(f'Accuracy is {zhunquelv}, labels are {self.labels}.')
        except:
            logger.debug(
                f'Accuracy can not be calculated, labels are {self.labels}')
            raise ValueError(
                f'Accuracy can not be calculated, labels are {self.labels}')

        # Send accuracy back to UI as remembered
        send(dict(mode='Online',
                  cmd='zhunquelv',
                  zhunquelv=str(zhunquelv),  # Covert accuracy into {str}
                  moxinglujing=self.moxinglujing,
                  shujulujing=self.shujulujing,
                  timestamp=time.time()))
        self.state = 'Idle'

        logger.debug('Stopped online collection.')
        return 0

    def query(self, chixushijian, zhenshibiaoqian, timestamp=0, send=send):
        """Answer for query package during ONLINE collection

        Arguments:
            chixushijian {float} -- Duration of the latest motion
            zhenshibiaoqian {str} -- True label of motion (image or actural motion)

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 for success, 1 for fail
        """
        send(real_time_reply.OK())

        # The state should be 'Online'
        if self.check_state('Online', 'query', send=send) == 1:
            return 1

        # Workload
        # Save the [send] as [latest_query_send],
        # the query result will be send through it
        self.latest_query_send = send
        self.latest_zhenshibiaoqian = zhenshibiaoqian
        try:
            self.send_backend(dict(cmd='query'))
        except:
            logger.info(f'Fail to send query request to backend.')

        # If not USE_BACKEND,****************************************
        # simulation response_query
        if not USE_BACKEND:
            self.response_query(zhenshibiaoqian, timestamp=0, send=send)

        # # Guess label, always return '2' for now
        # # todo: Estimate label from real data
        # logger.debug('Estimating label.')
        # gujibiaoqian = '2'
        # # Send back Query result
        # send(dict(mode='QueryReply',
        #           gujibiaoqian=gujibiaoqian,
        #           timestamp=time.time()))

        # # Send UI a motion order,
        # # if estimated and real label are both '2'
        # if all([gujibiaoqian == '2',
        #         zhenshibiaoqian == '2']):
        #     self.send_UI(dict(mode='Online',
        #                       cmd='kaishiyundong',
        #                       timestamp=time.time()))

        # logger.debug('Responded to query package')
        return 0

    def keepalive(self, timestamp=0, send=send):
        """Answer keep-alive package

        Keyword Arguments:
            timestamp {int} -- [description] (default: {0})
            send {func} -- Sending method (default: {send})

        Returns:
            {int} -- 0 means success, 1 means fail
        """
        # Reply keep alive package
        send(real_time_reply.KeepAlive())

        logger.debug(f'Responded to KeepAlive package.')
        return 0


if __name__ == '__main__':
    w = Worker()
    w.state = 'Idle'

    pass
