import pytest
import json
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.endpoint_factory import EndpointFactory
from starlette.testclient import TestClient

class MockGraphInterface(GraphInterface):
    def get_schema(self):
        with open('./data/graph_schema.json') as j_file:
            return json.load(j_file)

    def get_node(self, node_type, curie):
        with open('./data/node_list.json') as j_file:
            return json.load(j_file)[0]

    def get_single_hops(self, source_type, target_type, curie):
        with open('./data/single_hop_triplets.json') as j_file:
            return json.load(j_file)

    def run_cypher(self, cypher):

        return {
            'cypher': cypher
        }

@pytest.fixture()
def graph_interface():
    return MockGraphInterface('host', 'port', ('neo4j', 'pass'))

@pytest.fixture()
def endpoint_factory(graph_interface):
    return EndpointFactory(graph_interface)

@pytest.fixture()
def client(endpoint_factory):
    return TestClient(endpoint_factory.create_app())

def test_node_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.NODE_ENDPOINT_TYPE, **{
        'node_type': 'chemical_substance'
    })
    assert route.path == '/chemical_substance/{curie}'

def test_one_hop_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.HOP_ENDPOINT_TYPE, **{
        'source_type': 'chemical_substance',
        'target_type': 'gene',
    })
    assert route.path == '/chemical_substance/gene/{curie}'

def test_open_api_schema_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.OPEN_API_ENDPOINT_TYPE, **{
    })
    assert  route.path == '/openapi'

def test_cypher_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE, **{
    })
    assert route.path == '/graph/schema'


def test_one_hop_response(client, graph_interface):
    response = client.get('/chemical_substance/gene/CHEBI:11492')
    assert response.status_code == 200
    assert response.json() == graph_interface.get_single_hops('chemical_substance', 'gene', 'CHEBI:11492')

def test_node_response(client, graph_interface):
    response = client.get('/chemical_substance/curie')
    assert response.status_code == 200
    assert response.json() == graph_interface.get_node('chemical_substance', 'curie')

def test_cypher_response(client, graph_interface):
    query = f'MATCH (n) return n limit 1'
    response = client.post('/cypher', headers={
        'Content-Type': 'application/json'
    }, json={
        'query': query
    })
    assert response.status_code == 200
    assert response.json() == graph_interface.run_cypher(query)

def test_graph_schema_response(client, graph_interface):
    response = client.get(
        '/graph/schema'
    )
    assert response.status_code == 200
    assert response.json() == graph_interface.get_schema()