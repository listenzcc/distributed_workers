import warnings
import logging
import sys
import os

profilename = 'USERPROFILE'
if sys.platform == 'linux':
    profilename = 'HOME'
filepath = os.path.join(os.environ.get(profilename, os.curdir), 'root.log')


class Logger():
    def __init__(self, name='root', stream_level=logging.INFO,
                 filepath=filepath,
                 encoding='utf-8',
                 pattern='%(created)f - %(name)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'):
        """ Init logger, and add stream and file handler,
        name: logger name,
        stream_level: level of stream handler,
        filedir: dir of log file,
        encoding: encoding of log file,
        pattern: pattern of logging entries. """
        # Make logger
        self.logger = logging.getLogger(name=name)
        # Set logger level as very low value
        self.logger.setLevel(logging.DEBUG)
        # Add stream handler
        self.add_stream_handler(level=stream_level, pattern=pattern)
        # Add file handler
        self.add_file_handler(level=logging.DEBUG, pattern=pattern,
                              filepath=filepath, encoding=encoding,
                              delay=True)

    def add_stream_handler(self, level, pattern):
        """ Print logging on stdout immediately. """
        # Settings
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setFormatter(logging.Formatter(pattern))
        self.stream_handler.setLevel(level)
        # Add
        self.logger.addHandler(self.stream_handler)

    def add_file_handler(self, level, pattern, filepath, encoding, delay, mode='a'):
        """ Print logging on [filepath] in [encoding] with [delay] as [mode]. """
        # Be careful with mode other than 'a'
        if not mode == 'a':
            warnings.warn(
                f'Mode is set as {mode}, it may erase existing file {filepath}.')
        # Settings
        self.file_handler = logging.FileHandler(
            filepath, mode='a', encoding=encoding, delay=delay)
        self.file_handler.setFormatter(logging.Formatter(pattern))
        self.file_handler.setLevel(level)
        # Add
        self.logger.addHandler(self.file_handler)
        self.logger.filehandler = open(filepath, 'a')


default_logger = Logger().logger

# Test
if __name__ == '__main__':
    default_logger.info('info信息')
    # logger.setLevel(logging.INFO)
    default_logger.debug('debug')
    logger = Logger(name='name').logger
    logger.info('Hi')
