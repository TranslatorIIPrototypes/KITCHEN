#######################################################
#
# COOKERprocess.py
# Created on:      3-Jan-2020 2:55:27 PM
# Original author: powen
#
# COmpliance-Observing Knowledge Extraction and Rectification (COOKER):
#
# Converts the data, now in a generalized format from CHEF processing, into fully compliant and
# standardized data object using synonymizers and property/predicate transformer services.
#######################################################
from COOKER.COOKERwrite import COOKERwrite

import os
import logging
from Common.logutil import LoggingUtil


# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.COOKER.COOKERprocess", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class COOKERprocess:
    """Class: COOKERconvert  By: Phil Owen Date: 3-Jan-2020 2:55:27 PM Description: A class that
    standardizes the data from CHEF generalized data conversion processes.
    """
    # The data definition
    _data_def = None
    # Reference to the CHEF write class
    _write = None

    def __init__(self, data_def):
        """ Class constructor. """
        self.data_def = data_def
        self._write = COOKERwrite(data_def)

        pass

    def process(self):
        pass