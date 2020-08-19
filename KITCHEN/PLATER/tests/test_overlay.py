import asyncio
import pytest
from PLATER.services.util.overlay import Overlay


@pytest.fixture()
def graph_interface_apoc_supported():
    class MockGI:
        def supports_apoc(self):
            return True

        async def run_apoc_cover(self, idlist):
            return [{
                'result': [
                    {
                        'source_id': 'NODE:0',
                        'target_id': 'NODE:2',
                        'edge': {
                            'type': 'biolink:related_to',
                            'id': 'SUPPORT_EDGE_KG_ID_1'
                        }
                    }, {
                        'source_id': 'NODE:00',
                        'target_id': 'NODE:22',
                        'edge': {
                            'type': 'biolink:related_to',
                            'id': 'SUPPORT_EDGE_KG_ID_2'
                        }
                    }, {  # Edge relating two nodes from different answers
                        # we should expect this NOT to be in response.
                        'source_id': 'NODE:0',
                        'target_id': 'NODE:22',
                        'edge': {
                            'type': 'biolink:related_to',
                            'id': 'SUPPORT_EDGE_KG_ID_3'
                        }
                    }
                ]
            }]

    return MockGI()


@pytest.fixture()
def graph_interface_apoc_unsupported():
    class MockGI:
        def supports_apoc(self):
            return True

    return MockGI()


@pytest.fixture()
def reasoner_json():
    return {
        # Although this is not particularly useful in testing...
        'query_graph': {
            'nodes': [
                {'id': 'n0', 'type': 'type'},
                {'id': 'n1', 'type': 'type'},
                {'id': 'n2', 'type': 'type'}
            ],
            'edges': [
                {'id': 'e0', 'source_id': 'n0', 'target_id': 'n1'},
                {'id': 'e1', 'source_id': 'n1', 'target_id': 'n2'},
            ]
        },
        # Knowledge_graph Here also we don't really care about what was in
        # kg
        'knowledge_graph':
            {
                'nodes': [],
                'edges': []
            },
        'results': [
            {
                'node_bindings': [
                    {'qg_id': 'n0', 'kg_id': 'NODE:0'},
                    {'qg_id': 'n1', 'kg_id': 'NODE:1'},
                    {'qg_id': 'n2', 'kg_id': 'NODE:2'},
                ],
                'edge_bindings': [
                    {'qg_id': 'e0', 'kg_id': 'EDGE:0'},
                    {'qg_id': 'e1', 'kg_id': 'EDGE:1'},
                    {'qg_id': 'e2', 'kg_id': 'EDGE:2'},
                ]
            },
            {
                'node_bindings': [
                    {'qg_id': 'n0', 'kg_id': 'NODE:00'},
                    {'qg_id': 'n1', 'kg_id': 'NODE:11'},
                    {'qg_id': 'n2', 'kg_id': 'NODE:22'},
                ],
                'edge_bindings': [
                    {'qg_id': 'e0', 'kg_id': 'EDGE:00'},
                    {'qg_id': 'e1', 'kg_id': 'EDGE:11'},
                    {'qg_id': 'e2', 'kg_id': 'EDGE:22'},
                ]
            },
            {
                'node_bindings': [
                    {'qg_id': 'n0', 'kg_id': 'NODE:000'},
                    {'qg_id': 'n1', 'kg_id': 'NODE:111'},
                    {'qg_id': 'n2', 'kg_id': 'NODE:222'},
                ],
                'edge_bindings': [
                    {'qg_id': 'e0', 'kg_id': 'EDGE:000'},
                    {'qg_id': 'e1', 'kg_id': 'EDGE:111'},
                    {'qg_id': 'e2', 'kg_id': 'EDGE:222'},
                ]
                ,
            }
        ]
    }


def test_overlay_adds_support_bindings(graph_interface_apoc_supported, reasoner_json):
    ov = Overlay(graph_interface=graph_interface_apoc_supported)
    event_loop = asyncio.get_event_loop()
    response = event_loop.run_until_complete(ov.overlay_support_edges(reasoner_json))
    edges = response['knowledge_graph']['edges']
    edge_ids = list(map(lambda edge: edge['id'], edges))
    assert len(edge_ids) == 2
    assert 'SUPPORT_EDGE_KG_ID_1' in edge_ids
    assert 'SUPPORT_EDGE_KG_ID_2' in edge_ids
    checked = False
    for answer in response['results']:
        all_node_ids = list(map(lambda x: x['kg_id'], answer['node_bindings']))
        all_edge_kg_ids = list(map(lambda x: x['kg_id'], answer['edge_bindings']))
        if ('NODE:0' in all_node_ids and 'NODE:2' in all_node_ids) \
                or ('NODE:00' in all_node_ids and 'NODE:22' in all_node_ids):
            assert 'SUPPORT_EDGE_KG_ID_1' in all_edge_kg_ids or 'SUPPORT_EDGE_KG_ID_2' in all_edge_kg_ids
            checked = True
    assert checked
