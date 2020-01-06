#######################################################
# 
# COOKERwrite.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.COOKER.COOKERwrite", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class COOKERwrite:
    """Class: COOKERwrite  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on persisting COOKER records.
    """
    def __init__(self):
        """ Class constructor. """
        pass

    def persist(self):
        """ Persists the data. This generalized data set will be used by the COOKER """
        pass
