#######################################################
# 
# DIInspect.py
# Python implementation of the Class DIInspect
# Generated by Enterprise Architect
# Created on:      15-Nov-2019 11:13:55 AM
# Original author: powen
# 
#######################################################
from DataIntrospection.DIWrite import DIWrite
from DataIntrospection.DIUtils import DIUtils
from DataProcessing.DPRead import DPRead


class DIInspect:
    """Class: DIInspect  By: Phil Owen Date: 15-Nov-2019 Description: A class that
    contains the main code to introspect a data source.
    """
    # The output data definition
    __data_def = None
    # Reference to the di utils class
    __di_utils = None
    # Reference to the di write class
    __di_write = None
    # Reference to the DPRead class
    __dp_read = None

    def introspect(self, data_def):
        """Entry point to launch data introspection
        """
        self.__data_def = data_def
        self.__di_write = DIWrite(data_def)
        self.__di_utils = DIUtils()
        self.__dp_read = DPRead(data_def)

        pass

    def process_file(self):
        """Processes a character delimited input file
        """
        pass

    def process_rdbms(self):
        """Processes a relational database
        """
        pass

    def scan_data(self, data_row):
        """Initiates a scanning rows of data to determine node types and edge predicates
        """
        pass
