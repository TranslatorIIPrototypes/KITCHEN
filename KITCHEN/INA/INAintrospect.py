#######################################################
# 
# INAintrospect.py
# Created on:      15-Nov-2019 11:43:36 AM
# Original author: powen
# 
#######################################################
from Utils.INAutils import INAutils
from INA.INAwrite import INAwrite
from INA.INAread import INAread

import os
import logging
from Utils.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("INA.INAintrospect", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INAintrospect:
    """ Class: INA_introspect  By: Phil Owen Date: 10/23/2019 Description: A class that
    contains the main code to introspect a chemical structure data source.
    """
    # The output data definition
    _data_def = None
    # Reference to the di write class
    _write = None
    # Reference to the ina utils class
    _utils = INAutils()

    def __init__(self, data_def):
        """ Class constructor """
        self._data_def = data_def
        self._write = INAwrite(data_def)

        pass

    def process(self) -> object:
        """ Entry point to launch data introspection """
        # init the return
        #rv = None

        try:
            # get the defined data sources
            data_sources = self.get_data_sources()

            # did we get any data sources
            if data_sources is not None:
                # for each data source
                for data_source in data_sources:
                    # get the data source type from the data definition
                    data_type = self._utils.get_data_source_type(data_source)

                    # if type is a data file
                    if data_type == self._utils.INAdata_source_type.FILE:
                        data_records = self.process_file(data_source)
                    # is it an rdbms
                    elif data_type == self._utils.INAdata_source_type.RDBMS:
                        data_records = self.process_rdbms(data_source)
                    else:
                        raise Exception('Invalid or missing data source type.')

                    # scan the header for key words
                    header_analysis = self.scan_data(data_records[0])
                    record_analysis = {}

                    # for each subsequent data record
                    for data_record in data_records[1:]:
                        # scan the data record for keywords
                        record_analysis = self.scan_data(data_record)

                    # parse the analysis and produce a group of node-edge-node introspection
                    rv: dict = self.introspect(header_analysis, record_analysis)
            else:
                raise Exception('Missing data source.')

        except Exception as e:
            logger.error(f'Exception caught. Exception: {e}')
            rv: Exception = e

        # return to the caller
        return rv

    def introspect(self, header_analysis, record_analysis):
        """ Looks over the data elements that were captured and assemble into a input data definition """
        # init the return
        rv = {}

        # get a reference to the writer
        self._write = INAwrite(self._data_def)

        # return to the caller
        return rv

    def scan_data(self, data_row) -> dict:
        """ Initiates a scanning of a data row to determine node types and edge predicates """
        # init the return
        rv = {}

        # lookup the value to see if a node type can be detected
        self._utils.inspect_for_node_types('')

        # if node type was found
            # is this a chemical substance node
                # save the node information as the source
            # else it must be some sort of target node
                # save the node information as the target

        # if edge type was found
            # lookup the value to see if it is a edge predicate
            # if an edge predicate was found
                # save the edge information

        # return to the caller
        return rv

    def process_file(self, data_source) -> dict:
        """ Processes a character delimited input file """
        rv = {}

        # load the data file reader
        chef_rd = INAread(data_source)

        # get a subset of records that returns a dict for that file
        rv = chef_rd.get_file_data_record_subset()

        # return to caller
        return rv

    def process_rdbms(self, data_source) -> dict:
        """ Processes a relational database """
        # init the return
        rv = {}

        # create a data rdbms reader
        chef_rd = INAread(data_source)

        # get a subset of records that return a dict for that table
        rv = chef_rd.get_rdbms_data_record_subset()

        # return to the caller
        return rv

    def get_data_sources(self) -> dict:
        """ Gets the data sources from the data definition """
        # init the return value
        rv = {}

        # return to the caller
        return rv
