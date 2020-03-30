import logging
from logging.handlers import RotatingFileHandler
import os

class LoggingUtil(object):
    """ Logging utility controlling format and setting initial logging level """

    @staticmethod
    def init_logging(name, level=logging.INFO, format_sel='medium', log_file_level=None):
        log_file_path = os.path.join(os.path.dirname(__file__), '../../logs/plater.log')
        # get a logger
        logger = logging.getLogger(__name__)

        # returns a new logger if its not the root
        if not logger.parent.name == 'root':
            return logger

        # define the output types
        format_types = {
            "short": '[%(name)s.%(funcName)s] : %(message)s',
            "medium": '[%(name)s.%(funcName)s] - %(asctime)-15s: %(message)s',
            "long": '[%(name)s.%(funcName)s] - %(asctime)-15s %(filename)s %(levelname)s: %(message)s'
        }[format_sel]

        # create a stream handler (default to console)
        stream_handler = logging.StreamHandler()

        # create a formatter
        formatter = logging.Formatter(format_types)

        # set the formatter on the console stream
        stream_handler.setFormatter(formatter)

        # get the name of this logger
        logger = logging.getLogger(name)

        # set the logging level
        logger.setLevel(level)

        # if there was a file path passed in use it
        if log_file_path is not None:
            # create a rotating file handler, 100mb max per file with a max number of 10 files
            file_handler = RotatingFileHandler(filename=log_file_path, maxBytes=1000000, backupCount=10)

            # set the formatter
            file_handler.setFormatter(formatter)

            # if a log level for the file was passed in use it
            if log_file_level is not None:
                level = log_file_level

            # set the log level
            file_handler.setLevel(level)

            # add the handler to the logger
            logger.addHandler(file_handler)

        # add the console handler to the logger
        logger.addHandler(stream_handler)

        # return to the caller
        return logger
