#######################################################
# 
# INAutils.py
# Created on:      15-Nov-2019 11:13:55 AM
# Original author: powen
# 
#######################################################
import shared.node_types as nt
from enum import Enum

import os
import logging
from Utils.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("Common.INAutils", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INAutils:
    """Class: INAutils  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of utility functions for the INAintrospect class.
    """
    # declare a data source type enum
    INAdata_source_type = Enum('data_source_type', 'FILE RDBMS')

    def __init__(self):
        pass

    def construct_data_def(self, input_def: dict, output_def: dict) -> dict:
        """ Constructs a data definition file """
        pass

    def validate_data_def(self, data_def: dict) -> bool:
        """ Validates the data definition """
        pass

    def construct_input_def(self, col_def: dict) -> dict:
        """ Creates the input data definition given the results of the introspection. """
        pass

    def construct_output_def(self, col_def: dict) -> dict:
        """ Creates the output data definition given the results of the introspection. """
        pass

    def inspect_for_node_types(self, element: str) -> int:
        """ Calls a web service to determine if this data value can be associated to a biomodel node type. """
        # init the return value
        rv = None

        # get the node types
        node_types = self.get_node_types_from_ws(element)

        # check the returned value
        if node_types is not None:
            for val in node_types:
                rv = val

        # return to caller
        return rv

    def inspect_for_edge_types(self, element: str) -> str:
        """ Calls a web service to determine if this data value can be associated to a biomodel edge type. """
        # init the return value
        rv = None

        # get the edge types
        edge_types = self.get_edge_types_from_ws(element)

        # check the returned value
        if edge_types is not None:
            for val in edge_types:
                rv = val

        # return to caller
        return rv

    def inspect_for_edge_predicates(self, element: str) -> str:
        """ Calls a web service to determine if this data value can be associated to a biomodel edge predicate. """
        # init the return
        rv = None

        # get the edge predicates
        edge_predicates = self.get_edge_predicates_from_ws(element)

        # check the returned value
        if edge_predicates is not None:
            for val in edge_predicates:
                rv = val

        # return to caller
        return rv

    @staticmethod
    def get_node_types_from_ws(el: str) -> set:
        """ Returns the node type from the web service """
        # init the return
        rv = {}

        # make the call to the web service
        rv = {el}

        # return to the caller
        return rv

    @staticmethod
    def get_edge_predicates_from_ws(el: str) -> set:
        """ Returns the edge predicate from the web service """
        # init the return
        rv = {}

        # make the call to the web service
        rv = {el}

        # return to the caller
        return rv

    @staticmethod
    def get_edge_types_from_ws(el: str) -> set:
        """ Returns the edge type from the web service """
        # init the return
        rv = {}

        # make the call to the web service
        rv = {el}

        # return to the caller
        return rv

    @staticmethod
    def get_data_source_type(data_source: dict) -> int:
        """ Returns the type of data source (file, rdbms, etc.) """
        # init the return
        rv = -1

        # index into the data def to get the data source

        # parse the data source to get the type

        # return to the caller
        return rv
