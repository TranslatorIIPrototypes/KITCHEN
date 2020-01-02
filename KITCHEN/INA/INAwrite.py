#######################################################
# 
# INAwrite.py
# Created on:      15-Nov-2019 11:13:55 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("INA.INAwrite", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INAwrite:
    """Class: INAwrite  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on creating a RECIPE definition for the INAintrospect class.
    """
    # The RECIPE data definition
    _data_def = None

    def __init__(self, data_def):
        """ Class constructor. """

        self._data_def = data_def
        pass

    def write_recipe_def(self):
        """ Writes out the RECIPE data definition """
        pass
