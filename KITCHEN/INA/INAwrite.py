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
    # The RECIPE object definition
    _data_def: dict = None
    _parent_recipe: dict = None

    def __init__(self, data_def):
        """ Class constructor. """
        self._data_def = data_def

        pass

    def create_parent_recipe(self) -> bool:
        """ creates a default (empty) parent RECIPE object. children nodes will be RECIPE definitions for each data source """
        # init the parent
        _parent_recipe: dict = {}

        # grab a baseline RECIPE definition

        # populate the parent definition with details from the data definition

        # return to the caller
        return True

    def append_header_introspection(self, header_analysis) -> bool:
        """ appends a header record introspection to the RECIPE """

        # init the return
        rv: bool = True

        # populate the RECIPE definition

        # return to the caller
        return rv

    def append_data_record_introspection(self, data_record_analysis) -> bool:
        """ appends a data record introspection to the RECIPE """

        # init the return
        rv: bool = True

        # populate the RECIPE definition

        # return to the caller
        return rv

    def validate_recipe(self) -> bool:
        """ validates the RECIPE definition """

        # init the return
        rv: bool = True

        return rv

    def get_final_recipe(self) -> dict:
        """ creates a RECIPE transformation file """

        # init the return
        rv: dict = {}

        # check to make sure that the RECIPEs are valid
        if self.validate_recipe():
            rv = self._parent_recipe

        # return to the caller
        return rv
