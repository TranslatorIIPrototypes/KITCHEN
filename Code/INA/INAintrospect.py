#######################################################
# 
# INAintrospect.py
# Created on:      15-Nov-2019 11:43:36 AM
# Original author: powen
# 
#######################################################
from INA.INAutils import INAutils
from INA.INAwrite import INAwrite
from CHEF.CHEFread import CHEFread

class INAintrospect:
    """Class: INA_introspect  By: Phil Owen Date: 10/23/2019 Description: A class that
    contains the main code to introspect a chemical structure data source.
    """
    # The output data definition
    _data_def = None
    # Reference to the di write class
    _write = None
    # Reference to the ina utils class
    _utils = INAutils()


    def __init__(self, data_def):
        """Class constructor
        """
        self._data_def = data_def
        self._write = INAwrite(data_def)

        pass

    def introspect(self):
        """Entry point to launch data introspection
        """
        # get the data source type from the data definition
        self._utils.get_data_source_type(self._data_def)

        # if type is a data file
            # data_records = self.process_file()
        # else if type is a rdbms
            # data_records = self.process_rdbms()

        # for each data record
            # if first record, grab the header column record
                # scan the header for key words
                # self.scan_data(header_row)

                # scan the data record
                # self.scan_data(data_row)

       pass

    def process_file(self) -> dict:
        """Processes a character delimited input file
        """
        rv = {}

        # load the data file reader
        ch_rd = CHEFread(self._data_def)

        # get the file list
        #in_files = get_file_list()

        # for each file declared
            # set the file details
            #ch_rd.set_file(in_file_path, in_file_name)

            # get a subset of records that returns a dict for that file
                #data_records = ch_rd.get_data_record_subset()

        # return to caller
        return rv

    def process_rdbms(self) -> dict:
        """Processes a relational database
        """
        # init the return
        rv = {}

        # create a data rdbms reader
        ch_rd = CHEFread(self._data_def)

        # set connection to the data source
        #ch_rd.set_data_conn()

        # get the table (sql statement) list
        # self.get_rdbms_list()

        # for each data table (sql statement) declared
            # get a subset of records that return a dict for that table
            #ch_rd.get_file_rdbms_record_subset()

        # return to the caller
        return rv

    def get_file_list(self) -> dict:
        """Gets a list of input files from the data definition"""

        pass

    def get_rdbms_list(self) -> dict:
        """Gets a list of rdbms tables (sql statements) from the data definition"""

        pass

    def scan_data(self, data_row) -> dict:
        """Initiates a scanning of a data row to determine node types and edge predicates
        """
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
