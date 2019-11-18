import pytest
from DataIntrospection.DIIntrospect import DIIntrospect

def test_introspect():
    data_def = None

    di = DIIntrospect(data_def)

    di.introspect()

