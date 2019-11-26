import pytest
from INA.INAintrospect import INAintrospect

def test_introspect_FILE():
    # init the data definition
    data_def = None

    # create a new data daefintion for the test

    # create the introspection object
    di = INAintrospect(data_def)

    # perform the introspection
    di.introspect()

