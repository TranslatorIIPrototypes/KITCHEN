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
from Common.INAutils import INAutils, INADataSourceType

import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.CHEF.CHEFprocess", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


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

    def __init__(self, data_def, recipe_def):
        """ Class constructor. """
        # The input data definition (type, input location, etc.)
        self._data_def = data_def
        self._recipe_def = recipe_def
        self._utils = CHEFutils()
        self._write = CHEFwrite(recipe_def)
        self._read = INAread(data_def)

    def process(self) -> object:
        """ Entry point to launch data introspection """
        # init the return
        rv = None

        try:
            # get the defined data sources from the data definition
            data_sources = self._read.get_data_sources()

            # did we get any data sources
            if data_sources is not None:
                # for each data source
                for data_source in data_sources:
                    # get a sampling of records from the data source
                    data_records = self._read.get_records(data_source)

                    # parse the data records and transform/persist it into a file
                    rv: dict = self._write.transform(data_records)
            else:
                raise Exception('Missing data source. Aborting.')

        except Exception as e:
            logger.error(f'Exception caught. Aborting. Exception: {e}')
            raise

        # return to the caller
        return rv

    def apply_output_rules(self, data_row):
        """ Applies the output rules to a data row. """
        # init the return
        rv = {}
        pass

    def generate_output_record(self, data_row):
        """ Generates a output record from a row of data (Node -> Edge -> Node) and persists it. """
        # init the return
        rv = {}

        pass
