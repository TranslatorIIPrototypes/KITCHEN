#######################################################
# 
# CHEFwrite.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("CHEF.CHEFwrite", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class CHEFwrite:
    """Class: CHEFwrite  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on transforming (standardizing) the input data based on the INA RECIPE.
    """
    # The data definition
    _recipe_def = None

    def __init__(self, recipe_def):
        """ Class constructor. """
        self._recipe_def = recipe_def

        pass

    def transform(self, data_records):
        """ Transforms the data records into a standardized node-edge-node layout """
        pass

    def make_edge(self, edge_data):
        """ Makes a KEdge like object from the data row passed in. """
        pass

    def make_node(self, node_data):
        """ Makes a KNode like object from the data row passed in. """
        pass

    def persist(self, node_data):
        """ Persists the data into the standardized intermediate format. This data set will be used by the COOKER """
        pass
