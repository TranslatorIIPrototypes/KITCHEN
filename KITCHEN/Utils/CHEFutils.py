#######################################################
# 
# CHEFutils.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Utils.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("CHEFutils", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class CHEFutils:
    """ Class: CHEFutils  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of shared utility functions for the CHEFprocess class.
    """
    def __init__(self):
        """Class constructor.
        """
        pass

    def convert_to_type(self, data_value, new_type):
        """ Converts a string to the desired data type
        """
        pass

    def make_hyper_edge(self, elements):
        """ Creates a unique hyper edge ID from the data passed in.
        """
        pass

    def merge_elements(self, elements, delimiter):
        """ Merges a list of data elements using the separator provided.
        """
        pass

    def filter_by(self, data_row, criteria, criteria_type, filter_operation):
        """ Filters a data element by some criteria
        """
        pass

    def set_data_row(self, data_row):
        """ Sets the data row to be operated on
        """
        pass
