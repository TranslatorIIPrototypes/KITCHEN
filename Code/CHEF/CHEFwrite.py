#######################################################
# 
# CHEFwrite.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Utils.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("CHEFwrite", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class CHEFwrite:
    """Class: CHEFwrite  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on persisting records for the CHEFprocess class.
    """
    # The data definition
    _data_def = None

    def __init__(self, data_def):
        """ Class constructor. """
        self._data_def = data_def

        pass

    def transform(self, data_row):
        """ Transforms the data row into the appropriate node-edge-node layout """
        pass

    def make_edge(self, edge_data):
        """ Makes a KEdge object from the data row passed in. """
        pass

    def make_node(self, node_data):
        """ Makes a KNode object from the data row passed in. """
        pass
