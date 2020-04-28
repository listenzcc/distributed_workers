import os
from logger import Logger
logger = Logger(name='BACKEND', filepath=os.path.join('BACKEND.log')).logger


def start_matlab(working_directory, commands=[]):
    logger.debug('Starting matlab at %s, with %s',
                 working_directory, commands)

    command = 'matlab -sd {} -r "{}"'.format(
        working_directory,
        ';'.join(commands)
    )

    print(command)

    os.system(command)

    return 0


def new_backend(working_directory, IP, PORT):
    logger.debug('Starting new backend at %s, (%s: %s)',
                 working_directory, IP, PORT)
    commands = [f'IP = [\'{IP}\']',
                f'PORT = {PORT}',
                'diary_start',
                'matlab_client_start']

    start_matlab(working_directory, commands)
