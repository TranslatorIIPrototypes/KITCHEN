import asyncio
import pytest
import json
from functools import reduce
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.endpoint_factory import EndpointFactory
from starlette.testclient import TestClient
import os


class MockGraphInterface(GraphInterface):
    def __init__(self, *args, **kwargs):
        pass

    def get_schema(self):
        graph_schema_file_path = os.path.join(os.path.dirname(__file__), 'data', 'graph_schema.json')
        with open(graph_schema_file_path) as j_file:
            return json.load(j_file)

    async def get_mini_schema(self, source_id, target_id):
        #this function is only used by simple_spec endpoint
        # we could assert that its being called appropriately
        if source_id:
            assert source_id == 'SOME:CURIE'
        if target_id:
            assert target_id == 'SOME:CURIE'

        schema = self.get_schema()
        # flatten the schema, to mimic
        # MATCH (a)-[e]->(b) return labels(a) as source_label, type(e) as predicate, labels(b) as target_label
        flat_schema = []
        for source_type in schema:
            for target_type in schema[source_type]:
                for edge_type in schema[source_type][target_type]:
                    flat_schema.append({
                        'source_label': [source_type],
                        'predicate': edge_type,
                        'target_label': [target_type]})
        return flat_schema

    async def get_node(self, node_type, curie):
        node_list_file_path = os.path.join(os.path.dirname(__file__), 'data', 'node_list.json')
        with open(node_list_file_path) as j_file:
            return json.load(j_file)[0]

    async def get_single_hops(self, source_type, target_type, curie):
        single_hop_triplets_file_path = os.path.join(os.path.dirname(__file__), 'data', 'single_hop_triplets.json')
        with open(single_hop_triplets_file_path) as j_file:
            return json.load(j_file)

    async def run_cypher(self, cypher):

        return {
            'cypher': cypher
        }

    async def get_examples(self, source, target=None):
        single_hop_triplets_file_path = os.path.join(os.path.dirname(__file__), 'data', 'single_hop_triplets.json')
        with open(single_hop_triplets_file_path) as j_file:
            triplets = json.load(j_file)
        return reduce(lambda x, y: x + [y[0]], triplets, [])


@pytest.fixture()
def graph_interface():
    return MockGraphInterface('host', 'port', ('neo4j', 'pass'))


@pytest.fixture()
def endpoint_factory(graph_interface):
    return EndpointFactory(graph_interface)


@pytest.fixture()
def client(endpoint_factory):
    return TestClient(endpoint_factory.create_app('test-app'))


def test_node_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.NODE_ENDPOINT_TYPE, **{
        'node_type': 'chemical_substance'
    })
    assert route.path == '/chemical_substance/{curie}'


def test_node_response(client, graph_interface):
    response = client.get('/chemical_substance/curie')
    assert response.status_code == 200
    event_loop = asyncio.get_event_loop()
    graph_response = event_loop.run_until_complete(graph_interface.get_node('chemical_substance', 'curie'))
    assert response.json() == graph_response


def test_one_hop_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.HOP_ENDPOINT_TYPE, **{
        'source_type': 'chemical_substance',
        'target_type': 'gene',
    })
    assert route.path == '/chemical_substance/gene/{curie}'


def test_one_hop_response(client, graph_interface):
    response = client.get('/chemical_substance/gene/CHEBI:11492')
    assert response.status_code == 200
    event_loop = asyncio.get_event_loop()
    graph_response = event_loop.run_until_complete(graph_interface.get_single_hops('chemical_substance', 'gene', 'CHEBI:11492'))
    assert response.json() == graph_response


def test_open_api_schema_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.OPEN_API_ENDPOINT_TYPE, **{
        'build_tag': 'test-tag'
    })
    assert route.path == '/openapi.json'


def test_open_api_schema_response(client, graph_interface):
    openapi_path = '/openapi.json'
    response = client.get(openapi_path)
    assert response.status_code == 200
    open_spec = response.json()
    schema = graph_interface.get_schema()
    # assert that the types have paths in the open api spec and also ch
    print(open_spec)
    for top_types, links in schema.items():
        assert f'/{top_types}/{{curie}}' in open_spec['paths']
        for link_types in links:
            assert f'/{top_types}/{link_types}/{{curie}}' in open_spec['paths']
    assert '/simple_spec' in open_spec['paths']
    assert '/reasonerapi' in open_spec['paths']
    assert '/cypher' in open_spec['paths']
    assert '/graph/schema' in open_spec['paths']


def test_cypher_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.CYPHER_ENDPOINT_TYPE, **{
        'build_tag': 'test-tag'
    })
    assert route.path == '/cypher'


def test_cypher_response(client, graph_interface):
    query = f'MATCH (n) return n limit 1'
    response = client.post('/cypher', headers={
        'Content-Type': 'application/json'
    }, json={
        'query': query
    })
    assert response.status_code == 200
    ev_loop = asyncio.get_event_loop()
    graph_resp = ev_loop.run_until_complete(graph_interface.run_cypher(query))
    assert response.json() == graph_resp


def test_graph_schema_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE, **{
        'build_tag': 'test-tag'
    })
    assert route.path == '/graph/schema'


def test_graph_schema_response(client, graph_interface):
    response = client.get(
        '/graph/schema'
    )
    assert response.status_code == 200
    assert response.json() == graph_interface.get_schema()


def test_swagger_ui_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.SWAGGER_UI_ENDPOINT, **{
        'build_tag': 'test-tag'
    })
    assert route.path == '/apidocs'


def test_swagger_ui_endpoint_response(client, graph_interface):
    response = client.get('/apidocs')
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'text/html; charset=utf-8'


def test_create_simple_one_hop_endpoint_creation(endpoint_factory):
    route = endpoint_factory.create_endpoint(EndpointFactory.SIMPLE_ONE_HOP_SPEC, **{})
    assert route.path == '/simple_spec'


def test_simple_one_hop_spec_response(client, graph_interface):
    # with out parameters it should return all the questions based on that
    # send source parameter, target parameter
    response = client.get('/simple_spec')
    assert response.status_code == 200
    specs = response.json()
    schema = graph_interface.get_schema()
    source_types = set(schema.keys())
    target_types = set(reduce(lambda acc, source: acc + list(schema[source].keys()), schema, []))
    spec_len = 0
    for source in schema:
        for target in schema[source]:
            spec_len += len(schema[source][target])
    assert len(specs) == spec_len

    for item in specs:
        assert item['source_type'] in source_types
        assert item['target_type'] in target_types

    # test source param
    source_type = list(schema.keys())[0]
    response = client.get(f'/simple_spec?source=SOME:CURIE')
    assert response.status_code == 200
    response = client.get(f'/simple_spec?target=SOME:CURIE')
    assert response.status_code == 200
