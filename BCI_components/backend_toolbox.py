import os
import time
from ctypes import windll, create_string_buffer, WINFUNCTYPE
from ctypes.wintypes import BOOL, HWND, LPARAM

from logger import Logger
logger = Logger(name='BACKEND', filepath=os.path.join('BACKEND.log')).logger


class OpenHide():
    def __init__(self, working_directory, commands=[]):
        # self.cmd = 'matlab -nodesktop -nosplash -r main_gui'
        self.cmd = 'matlab -nodesktop -nosplash -sd {} -r "{}"'.format(
            working_directory,
            ';'.join(commands))
        self.hwnd_title = b'MATLAB Command Window'
        self.has_minimized = False

    def run(self):
        @WINFUNCTYPE(BOOL, HWND, LPARAM)
        def hide(hwnd, extra):
            title = create_string_buffer(1024)
            windll.user32.GetWindowTextA(hwnd, title, 255)
            title = title.value
            if title == self.hwnd_title:
                windll.user32.ShowWindow(hwnd, 1)
                windll.user32.ShowWindow(hwnd, 2)
                print('Minimizing.')
                self.has_minimized = True
            return 1

        os.system(self.cmd)
        for _ in range(100):
            windll.user32.EnumWindows(hide, 0)
            if self.has_minimized:
                print('--')
                break
            time.sleep(0.1)


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

    openhide = OpenHide(working_directory, commands)
    openhide.run()
    # start_matlab(working_directory, commands)
