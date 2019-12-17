import logging
from logging.handlers import RotatingFileHandler

def init_logger(name,level = logging.INFO, logFilePath = './', logFileLevel = logging.ERROR):
    logger = logging.getLogger(name)
    if not logger.parent.name == 'root':
        return logger

    # FORMAT = {
    #     "short" : '%(funcName)s: %(message)s',
    #     "medium" : '%(funcName)s: %(asctime)-15s %(message)s',
    #     "long"  : '%(asctime)-15s %(filename)s %(funcName)s %(levelname)s: %(message)s'
    # }[format]

    # create a stream handler (default to console)
    stream_handler = logging.StreamHandler()

    # create a formatter
    # formatter = logging.Formatter(FORMAT)

    # set the formatter on the console stream
    # stream_handler.setFormatter(formatter)

    # get the name of this logger
    logger = logging.getLogger(name)

    # set the logging level
    logger.setLevel(level)

    # if there was a file path passed in use it
    if logFilePath is not None:
        # create a rotating file handler, 100mb max per file with a max number of 10 files
        file_handler = RotatingFileHandler(filename=logFilePath + name + '.log', maxBytes=1000000, backupCount=10)

        # set the formatter
        # file_handler.setFormatter(formatter)

        # if a log level for the file was passed in use it
        if logFileLevel is not None:
            level = logFileLevel

        # set the log level
        file_handler.setLevel(level)

        # add the handler to the logger
        logger.addHandler(file_handler)

    # add the console handler to the logger
    logger.addHandler(stream_handler)

    # return to the caller
    return logger