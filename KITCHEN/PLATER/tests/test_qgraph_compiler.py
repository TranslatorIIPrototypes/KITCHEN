from PLATER.services.util.qgraph_compiler import cypher_query_answer_map
import pytest

@pytest.fixture()
def question_graph():
    return {
        'nodes': [
            {
                'id': 'n0',
                'type': ['type1'],
                'curie': 'SOME:CURIE'
            }, {
                'id': 'n1',
                'type': [
                    'type2'
                ]
            }
        ],
        'edges': [
            {
                'id': 'e0',
                'type': 'edge-type',
                'source_id': 'n0',
                'target_id': 'n1'
            }
        ]
    }

@pytest.fixture()
def question_graph_with_properties():
    return {
        'nodes': [
            {
                'id': 'n0',
                'type': ['type1'],
                'curie': 'SOME:CURIE',
                'name': 'name'
            }, {
                'id': 'n1',
                'type': [
                    'type2'
                ],
                'curie': ['SOME:OTHER_CURIE1']
            }
        ],
        'edges': [
            {
                'id': 'e0',
                'type': 'edge-type',
                'source_id': 'n0',
                'target_id': 'n1'
            }
        ]
    }


def test_cypher_generated_for_a_query_graph(question_graph, question_graph_with_properties):
    """ """
    cypher = cypher_query_answer_map(question_graph)
    cypher_expected = """MATCH (n0:`type1` {`id`: 'SOME:CURIE'})-[e0:edge-type]->(n1:`type2`) USING INDEX n0:type1(id) WITH [n0] AS n0, [n1] AS n1, collect(DISTINCT e0) AS e0 RETURN [ni IN n0 | {qg_id:'n0', kg_id:ni.id, node: ni, type: labels(ni) }] + [ni IN n1 | {qg_id:'n1', kg_id:ni.id, node: ni, type: labels(ni) }] AS nodes, [ei IN e0 | {qg_id:'e0', kg_id:ei.id, edge: ei, type: type(ei) }] AS edges"""
    assert cypher == cypher_expected
