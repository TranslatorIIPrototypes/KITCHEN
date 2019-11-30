#######################################################
# 
# INAread.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("INAread", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INAread:
    """Class: INAread By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on reading data records for the processor classes.
    """
    _data_def = None

    def __init__(self, data_def):
        """ Class constructor. """
        self._data_def = data_def
        pass

    def get_data_conn(self) -> object:
        """ Returns a connection to a RDBMS """
        # get connection string from the data source definition
        # init the return
        rv = {}

        # get the file path/name
        rv = self._data_def

        # return to the caller
        return rv

    def get_file(self) -> str:
        """ Returns the data file location """
        # init the return
        rv = ''

        # get the file path and name from the data source definition

        # assemble the file path/name
        rv = self._data_def

        # return to the caller
        return rv

    def get_file_data_record_subset(self, record_limit: int = 5) -> dict:
        """ Returns a dict of data records from a file """
        # init the return
        rv = {}

        # get the file path/name
        full_file_path = self.get_file()

        # parse the file and get the records

        # check for errors

        # return to the caller
        return rv

    def get_rdbms_data_record_subset(self, record_limit: int = 5) -> dict:
        """ Returns a dict of data records from a rdbms """
        # init the return
        rv = {}

        # execute the sql statement
        rv = self.execute()

        # check for errors

        # return to the caller
        return rv

    def execute(self) -> dict:
        """ Executes the sql statment """
        # init the return
        rv = {}

        # get the connection to the rdbms
        conn = self.get_data_conn()

        # get the sql statment
        sql = self.get_sql_statement()

        # limit the records

        # execute the sql

        # return to the caller
        return rv

    def get_sql_statement(self) -> str:
        """ Gets the sql statement from the data source definition"""
        # init the return
        rv = ''

        # read the data source def to get the sql

        # return to the caller
        return rv

    def get_data_record_iterator(self) -> dict:
        """ Returns a data record iterator """
        pass
