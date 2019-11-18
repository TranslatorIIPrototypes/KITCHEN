#######################################################
# 
# CHEFprocess.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
from Utils.CHEFutils import CHEFutils
from CHEF.CHEFwrite import CHEFwrite
from INA.INAread import INAread

import os
import logging
from Utils.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("CHEFprocess", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class CHEFProcess:
    """Class: CHEFProcess  By: Phil Owen Date: 15-Nov-2019 Description: A class that
    contains the main code to ingest and process a data source.
    """
    # The input data definition
    _data_def = None
    # Reference to the dp utils class
    _utils = None
    # Reference to the dp write class
    _write = None
    # Reference to the dp read class
    _read = None

    def __init__(self, data_def):
        """Class constructor.
        """
        self._data_def = data_def
        self._utils = CHEFutils()
        self._write = CHEFwrite(data_def)
        self._read = INAread(data_def)

        pass

    def process(self):
        """Main entry point to initiate the processing of the data.
        """
        pass

    def process_file(self):
        """Processes a data file.
        """
        pass

    def process_rdbms(self):
        """Processes records in a relational database.
        """
        pass

    def apply_output_rules(self, data_row):
        """Applies the output rules to a data row.
        """
        pass

    def generate_output_record(self, data_row):
        """Generates a output record from a row of data (Node -> Edge -> Node).
        """
        pass
