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
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("Common.INAutils", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')


class INADataSourceType(Enum):
    """ Class: INADataSourceType By: Phil Owen Date: 15-Nov-2019 Description: A data source type enum """
    FILE = 1
    RDBMS = 2
    WS = 3


class INAutils:
    """Class: INAutils  By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of utility functions for the INA classes.
    """

    def __init__(self):
        pass

    def validate_data_def(self, data_def: dict) -> bool:
        """ Validates the data definition """
        rv: bool = True

        # return to the caller
        return rv

    def inspect_for_node_type(self, element: str) -> int:
        """ Calls a web service to determine if this data value can be associated to a Translator biomodel node or type. """
        # init the return value
        rv = None

        # get the node types
        node_types = self.get_node_type_from_ws(element)

        # check the returned value
        if node_types is not None:
            for val in node_types:
                rv = val

        # return to caller
        return rv

    def inspect_for_edge_property(self, element: str) -> str:
        """ Calls a web service to determine if this data value can be associated to a biomodel edge property. """
        # init the return value
        rv = None

        # get the edge types
        edge_types = self.get_edge_property_from_ws(element)

        # check the returned value
        if edge_types is not None:
            for val in edge_types:
                rv = val

        # return to caller
        return rv

    def inspect_for_edge_predicate(self, element: str) -> str:
        """ Calls a web service to determine if this data value can be associated to a biomodel edge predicate. """
        # init the return
        rv = None

        # get the edge predicates
        edge_predicates = self.get_edge_predicate_from_ws(element)

        # check the returned value
        if edge_predicates is not None:
            for val in edge_predicates:
                rv = val

        # return to caller
        return rv

    @staticmethod
    def get_node_type_from_ws(element: str) -> dict:
        """ Returns the node type from the web service """
        # init the return
        rv = {}

        # make the call to the web service

        # return to the caller
        return rv

    @staticmethod
    def get_edge_predicate_from_ws(element: str) -> dict:
        """ Returns the edge predicate from the web service """
        # init the return
        rv = {}

        # make the call to the web service

        # return to the caller
        return rv

    @staticmethod
    def get_edge_property_from_ws(element: str) -> dict:
        """ Returns the edge property from the web service """
        # init the return
        rv = {}

        # make the call to the web service

        # return to the caller
        return rv
