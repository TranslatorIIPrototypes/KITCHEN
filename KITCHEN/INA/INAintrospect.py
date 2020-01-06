#######################################################
# 
# INAintrospect.py
# Created on:      15-Nov-2019 11:43:36 AM
# Original author: powen
#
# Implementation of the IntrospectioN Analyzer (INA):
#
# Introspects data sources to discover entities and predicates, creates a metadata object of Rules Ensuring
# Compliance of Information Producing Entities (RECIPE) defining how to transform the data
# into a translator-compliant source.
#######################################################
from Common.INAutils import INAutils
from INA.INAwrite import INAwrite
from INA.INAread import INAread

import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.INA.INAintrospect", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INA_introspect:
    """ Class: INA_introspect  By: Phil Owen Date: 10/23/2019 Description: A class that
    contains code to introspect a data source to determine node-edge-node relationships and properties.
    """
    # The input data definition (type, input location, etc.)
    _data_def: dict = None
    # Reference to the INA write class
    _write: INAwrite = None
    # Reference to the INA read class
    _read: INAread = None
    # Reference to the INA utils class
    _utils: INAutils = INAutils()
    # file system path for intermediate text file output of the RECIPE object for inspection
    _intermediate_out_path: str = None

    def __init__(self, data_def: dict, intermediate_out_path: str = None):
        """ Class constructor. populate all class members """
        self._data_def = data_def
        self._read = INAread(data_def)
        self._write = INAwrite(data_def)
        self._intermediate_out_path = intermediate_out_path

    def introspect(self) -> dict:
        """ Entry point to launch data introspection """
        # init the return
        rv: dict = {}

        try:
            # validate the data definition
            if self._utils.validate_data_def(self._data_def):
                # get the defined data sources from the data definition
                data_sources: dict = self._read.get_data_sources()

                # did we get any data sources
                if data_sources is not None and len(data_sources) > 0:
                    # create a baseline object to store the data RECIPEs
                    success: bool = self._write.create_parent_recipe()

                    # did it create ok
                    if success:
                        # for each data source
                        for data_source in data_sources:
                            # get a sampling of records from the data source, 1 row for the header names and a few of raw data
                            data_records: list = self._read.get_records(data_source, 5)

                            # check the return for errors
                            if data_records is None:
                                raise Exception('Error gathering data record(s). Aborting.')  # TODO: add data_source details to this return

                            # use Translator services to identify the nature of the header record elements
                            header_analysis: dict = self.scan_header_record(data_records[0])

                            # check the return for errors
                            if header_analysis is None:
                                raise Exception('Error analyzing header record. Aborting.') # TODO: add data_source details to this return
                            else:
                                # append the header introspection to the RECIPE
                                success: bool = self._write.append_header_introspection(header_analysis)

                                # check the return for errors
                                if not success:
                                    raise Exception('Error appending header record introspection. Aborting.') # TODO: add data_source details to this return

                            # init the data analysis results
                            data_analysis: list = []

                            # for each subsequent data record
                            for data_record in data_records[1:]:
                                # use Translator services to identify the nature of the data record elements
                                result: dict = self.scan_data_record(data_record)

                                # check the return for errors
                                if result is None:
                                    raise Exception('Error scanning data record. Aborting.') # TODO: add data_source details to this return
                                else:
                                    data_analysis.append(result)

                            # append the data record introspection to the RECIPE
                            success: bool = self._write.append_data_record_introspection(data_analysis)

                            # check the return for errors
                            if not success:
                                raise Exception('Error appending data record introspection. Aborting.') # TODO: add data_source and data record details to this return
                    else:
                        raise Exception('Error creating RECIPE object. Aborting.' ) # TODO: add data_sources details to this return
                else:
                   raise Exception('Error missing data source(s). Aborting.') # TODO: add details to this return

                # get the completed RECIPE
                rv = self._write.get_final_recipe()

                # check for errors
                if rv is None:
                    raise Exception('Error creating final RECIPE definition object. Aborting.')
            else:
                raise Exception('Error validating data definition. Aborting.')

            # are we to output the results to a file
            if self._intermediate_out_path is not None and rv is not None:
                success = self._utils.output_intermediate_results(rv, self._intermediate_out_path)

                # check the return for errors
                if not success:
                    raise Exception('Error outputting intermediate introspection results. Aborting.')

        except Exception as e:
            logger.exception(e)
            raise

        # return to the caller
        return rv

    def scan_header_record(self, header_record: dict) -> dict:
        """ Initiates a scanning of a data header to identify node types and edge properties and predicates based on the column name """
        # init the return
        rv: dict = {}

        # for each data element in the record
        for element in header_record:
            # lookup the value to see if a node type can be detected
            nt = self._utils.inspect_for_node_type(element)

            # if node type was found
                # is this a chemical substance node type
                # save the node information as the source
            # else it must be some sort of target node
                # save the node information as the target

            epred = self._utils.inspect_for_edge_predicate(element)

            # if an edge predicate type was found
                # save the edge predicate information

            eprop = self._utils.inspect_for_edge_property(element)

            # if an edge property type was found
                # save the edge property information

        # return to the caller
        return rv

    def scan_data_record(self, data_record: dict) -> dict:
        """ Initiates a scanning of a data row to determine node types and edge predicates """
        # init the return
        rv: dict = {}

        # for each data element in the record
        for element in data_record:
            # lookup the value to see if a node type can be detected
            nt: int = self._utils.inspect_for_node_type(element)

            # if node type was found
                # is this a chemical substance node type
                # save the node information as the source
            # else it must be some sort of target node
                # save the node information as the target

            epred: str = self._utils.inspect_for_edge_predicate(element)

            # if an edge predicate type was found
                # save the edge predicate information

            eprop: str = self._utils.inspect_for_edge_property(element)

            # if an edge property type was found
                # save the edge property information

        # return to the caller
        return rv
