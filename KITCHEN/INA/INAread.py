#######################################################
# 
# INAread.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################
from Common.INAutils import INADataSourceType

import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.INA.INAread", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INAread:
    """Class: INAread By: Phil Owen Date: 15-Nov-2019 Description: A class that has a number of functions focusing
    on reading data records from various sources for the INAintrospect and CHEFprocess classes.
    """
    # The input data definition (type, input location, etc.)
    _data_def: dict = None

    def __init__(self, data_def: dict):
        """ Class constructor. """
        self._data_def = data_def

        pass

    def get_records(self, data_source: dict, record_limit: int = -1) -> list:
        """ processes an input data source and returns a list of dict records. a record limit of -1 will return all records """

        # init the return
        rv: list = []

        # get the data source type from the data source definition
        data_type: INADataSourceType = self.get_data_source_type(data_source)

        # parse the data and get a sampling of name/value pairs for each record element.
        # record 0 will be the names of the elements, subsequent records will be the data elements
        # if type is a textual data file
        if data_type == INADataSourceType.FILE:
            rv = self.process_file(data_source, record_limit)
        # else is it an rdbms
        elif data_type == INADataSourceType.RDBMS:
            rv = self.process_rdbms(data_source, record_limit)
        # else is it an web service
        elif data_type == INADataSourceType.WS:
            rv = self.process_ws(data_source, record_limit)
        # capture unexpected data source type error
        else:
            raise Exception('Invalid or missing data source type. Aborting.')

        # return to the caller
        return rv

    def process_file(self, data_source: dict, record_limit) -> list:
        """ Processes a character delimited input file """
        rv: list = []

        # get a subset of records that returns a dict for that file
        rv = self.get_file_data_record_subset(record_limit)

        # return to caller
        return rv

    def process_rdbms(self, data_source: dict, record_limit: int) -> list:
        """ Processes a relational database """
        # init the return
        rv: list = []

        # get a subset of records that return a dict for that table
        rv = self.get_rdbms_data_record_subset(data_source, record_limit)

        # return to the caller
        return rv

    def process_ws(self, data_source: dict, record_limit: int) -> list:
        """ Processes a web service """
        # init the return
        rv: list = []

        # get a subset of records that return a dict for that table
        rv = self.get_ws_data_record_subset(record_limit)

        # return to the caller
        return rv

    def get_data_sources(self) -> dict:
        """ Gets the data sources from the data definition """
        # init the return value
        rv: dict = {}

        # use the data definition to locate the type and locations of the target input data sources

        # return to the caller
        return rv

    def get_data_source_type(self, data_source: dict) -> INADataSourceType:
        """ Returns the type of data source (file, rdbms, web service, etc.) """
        # init the return
        rv: int = -1

        # parse the data source to get the type

        # return to the caller
        return rv

    def get_rdbms_conn(self, data_source: dict) -> object:
        """ Returns a connection to a RDBMS """
        # get connection string from the data source definition
        # init the return
        rv: object = None

        # get the file path/name

        # return to the caller
        return rv

    def get_ws_conn(self, data_source: dict) -> object:
        """ Returns a connection to a web service """
        # get connection string from the data source definition
        # init the return
        rv: object = None

        # get the web service url

        # return to the caller
        return rv

    def get_file(self, data_source: dict) -> str:
        """ Returns the data file location """
        # init the return
        rv: str = ''

        # get the file path and name from the data source definition

        # assemble the file path/name

        # return to the caller
        return rv

    def get_file_data_record_subset(self, record_limit: int) -> list:
        """ Returns a dict of data records from a file """
        # init the return
        rv: list = []

        # get the file path/name
        full_file_path: str = self.get_file()

        # parse the file and get the records

        # check for errors

        # return to the caller
        return rv

    def get_ws_data_record_subset(self, record_limit: int) -> list:
        """ Returns a dict of data records from a web service """
        # init the return
        rv: list = []

        # access the ws and get some data bac
        conn = self.get_ws_conn()

        # check for errors

        # get the data from the web service

        # check for errors

        # return to the caller
        return rv

    def get_rdbms_data_record_subset(self, data_source: dict, record_limit: int) -> list:
        """ Returns a dict of data records from a rdbms """
        # init the return
        rv: list = []

        # execute the sql statement
        rv = self.execute(data_source, record_limit)

        # check for errors

        # return to the caller
        return rv

    def execute(self, data_source: dict, record_limit: int) -> list:
        """ Executes the sql statement """
        # init the return
        rv: list = []

        # get the connection to the rdbms
        conn = self.get_rdbms_conn(data_source)

        # get the sql statement
        sql = self.get_sql_statement()

        # limit the record count

        # execute the sql

        # return to the caller
        return rv

    def get_sql_statement(self) -> str:
        """ Gets the sql statement from the data source definition"""
        # init the return
        rv: str = ''

        # read the data source def to get the sql

        # return to the caller
        return rv
