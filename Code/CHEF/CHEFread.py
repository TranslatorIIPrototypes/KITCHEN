#######################################################
# 
# CHEFread.py
# Created on:      15-Nov-2019 11:15:27 AM
# Original author: powen
# 
#######################################################


class CHEFread:
    """Class: CHEFread By: Phil Owen Date: 15-Nov-2019 Description: A class that has a
    number of functions focusing on reading data records for the CHEFprocess class.
    """
    _data_def = None

    def __init__(self, data_def):
        """Class constructor.
        """
        self._data_def = data_def
        pass

    def set_data_conn(self, connstr: str):
        """Creates and sets a connection to a RDBMS
        """
        pass

    def set_file(self, file_path: str, file_name: str):
        """Sets the data file details
        """
        pass

    def get_file_data_record_subset(self, record_limit: int = 5) -> dict:
        """Returns a dict of data records
        """
        pass

    def get_file_rdbms_record_subset(self, record_limit: int = 5) -> dict:
        """Returns a dict of data records
        """
        pass

    def get_data_record_iterator(self) -> dict:
        """Returns a data record iterator
        """
        pass
