import os
from logger import Logger
logger = Logger(name='BACKEND', filepath=os.path.join('BACKEND.log')).logger


def start_matlab(working_directory, commands=[]):
    """Start matlab instance

    Arguments:
        working_directory {str} -- Path of working directory

    Keyword Arguments:
        commands {list} -- Commands for matlab instance (default: {[]})

    Returns:
        flag {int} -- Flag of success or failure
    """
    logger.debug('Starting matlab at %s, with %s',
                 working_directory, commands)

    command = 'matlab -sd {} -r "{}"'.format(
        working_directory,
        ';'.join(commands)
    )

    print(command)

    os.system(command)

    return 0


def new_backend(working_directory, IP, PORT, IP_EEG_DEVICE, PORT_EEG_DEVICE):
    """Start a new backend

    Arguments:
        working_directory {str} -- Path of working directory
        IP {str} -- IP address of backend
        PORT {int} -- PORT of backend
        IP_EEG_DEVICE {str} -- IP address of EEG device
        PORT_EEG_DEVICE {int} -- PORT of EEG device
    """

    logger.debug('Starting new backend at %s, (%s: %s)',
                 working_directory, IP, PORT)
    commands = [f'IP = [\'{IP}\']',
                f'PORT = {PORT}',
                f'IP_EEG_DEVICE = [\'{IP_EEG_DEVICE}\']',
                f'PORT_EEG_DEVICE = {PORT_EEG_DEVICE}',
                'diary_start',
                'matlab_client_start']

    start_matlab(working_directory, commands)
