import pytest
import json
from Code.Plater.services.validators.KGX_validator import  KGX_Validator
import requests

@pytest.fixture()
def kgx_validator() :
    return KGX_Validator()


@pytest.fixture()
def broken_kgx_graph():
    return requests.get('https://raw.githubusercontent.com/NCATS-Tangerine/kgx/master/examples/biogrid-fake.json').json()





def test_kgx_invalid(kgx_validator, broken_kgx_graph):
    assert kgx_validator.validate(broken_kgx_graph) == False