#######################################################
# 
# CHEFprocess.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
#
# Creator of Homogeneous Export Format (CHEF):
#
# Uses the RECIPE definition from INA to transform the incoming data set into a generalized node-edge-node format,
# focusing on the portions of the data that will eventually be exposed via the KP
#######################################################
from Common.CHEFutils import CHEFutils
from CHEF.CHEFwrite import CHEFwrite
from INA.INAread import INAread

import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("CHEF.CHEFprocess", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class CHEFprocess:
    """Class: CHEFProcess  By: Phil Owen Date: 15-Nov-2019 Description: A class that
    contains the main code to ingest and process a data source to convert it into a common format.
    """
    # The input data definition
    _data_def = None
    # The input RECIPE data definition
    _recipe_def = None
    # Reference to the CHEF utils class
    _utils = None
    # Reference to the CHEF write class
    _write = None
    # Reference to the INA read class
    _read = None

    def __init__(self, recipe_def, data_def):
        """ Class constructor. """
        self._data_def = data_def
        self._recipe_def = recipe_def

        self._utils = CHEFutils()
        self._write = CHEFwrite(recipe_def)
        self._read = INAread(data_def)

        pass

    def process(self):
        """ Main entry point to initiate the processing of the data. """
        pass

    def process_file(self):
        """ Processes a data file. """
        pass

    def process_rdbms(self):
        """ Processes records in a relational database. """
        pass

    def apply_output_rules(self, data_row):
        """ Applies the output rules to a data row. """
        pass

    def generate_output_record(self, data_row):
        """ Generates a output record from a row of data (Node -> Edge -> Node) and persists it. """
        pass
