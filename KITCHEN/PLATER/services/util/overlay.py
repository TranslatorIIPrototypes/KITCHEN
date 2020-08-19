from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.question import Question
from functools import reduce


class Overlay:
    def __init__(self, graph_interface: GraphInterface):
        self.graph_interface = graph_interface

    async def overlay_support_edges(self, reasoner_graph):
        """
        Grabs a set of answers and queries for connection among set of nodes
        :param reasoner_graph:
        :return:
        """
        final_response = {}
        # Set to keep track of edge_ids appended to knowledge_graph.edges
        # so as not to add dup edges
        added_edge_ids = set()
        edges_to_add = list()
        overlayed_answers = list()
        chunk_size = 1
        chunked_answers = [reasoner_graph[Question.ANSWERS_KEY][start: start + chunk_size]
                           for start in range(0, len(reasoner_graph[Question.ANSWERS_KEY]), chunk_size)]
        for answer in chunked_answers:
            # 3. filter out kg ids
            all_kg_nodes = set(map(lambda node_binding: node_binding[Question.KG_ID_KEY],
                                   # 2. merge them into single array
                                   reduce(lambda a, b: a + b,
                                          # 1. get node bindings from all answers
                                          map(lambda ans: ans[Question.NODE_BINDINGS_KEY], answer), [])))
            # fun part summon APOC
            if self.graph_interface.supports_apoc():
                all_kg_nodes = list(all_kg_nodes)
                apoc_result = (await self.graph_interface.run_apoc_cover(all_kg_nodes))[0]['result']
                apoc_result = self.structure_for_easy_lookup(apoc_result)
                # now go back to the answers and add the edges
                for ans in answer:
                    support_id_suffix = 0
                    node_bindings = ans[Question.NODE_BINDINGS_KEY]
                    ans_all_node_ids = set(map(lambda x: x[Question.KG_ID_KEY], node_bindings))
                    for node_id in ans_all_node_ids:
                        other_nodes = ans_all_node_ids.difference(set(node_id))
                        # lookup current node in apoc_result
                        current_node_relations = apoc_result.get(node_id, {})
                        for other_node_id in other_nodes:
                            # lookup for relations in apoc_result graph
                            support_edges = current_node_relations.get(other_node_id, [])
                            for support_edge in support_edges:
                                q_graph_id = f's_{support_id_suffix}'
                                support_id_suffix += 1
                                k_graph_id = support_edge['id']
                                ans['edge_bindings'].append(
                                    {
                                        Question.QG_ID_KEY: q_graph_id,
                                        Question.KG_ID_KEY: k_graph_id
                                    }
                                )
                                if k_graph_id not in added_edge_ids:
                                    added_edge_ids.add(k_graph_id)
                                    edges_to_add.append(support_edge)
                    overlayed_answers.append(ans)
                    # @TODO raise exception if apoc is not supported

        final_response[Question.QUERY_GRAPH_KEY] = reasoner_graph[Question.QUERY_GRAPH_KEY]
        final_response[Question.ANSWERS_KEY] = overlayed_answers
        final_response[Question.KNOWLEDGE_GRAPH_KEY] = reasoner_graph[Question.KNOWLEDGE_GRAPH_KEY]
        final_response[Question.KNOWLEDGE_GRAPH_KEY][Question.EDGES_LIST_KEY] += edges_to_add
        return final_response

    def structure_for_easy_lookup(self, result_set):
        """
        Converts apoc result into a mini graph
        :param result_set:
        :return:
        """
        result = {}
        for r in result_set:
            source_id = r['source_id']
            target_id = r['target_id']
            edge = r['edge']
            edge['source_id'] = source_id
            edge['target_id'] = target_id
            m = result.get(source_id, {})
            n = m.get(target_id, list())
            n.append(edge)
            m[target_id] = n
            result[source_id] = m
        return result


if __name__ == '__main__':
    gp = GraphInterface('localhost', '7474', ('neo4j', 'ncatsgamma'))
    overlay = Overlay(gp)
    resoner_jj = {
        "query_graph": {
            "nodes": [
                {
                    "id": "n1",
                    "type": "named_thing"
                },
                {
                    "id": "n2",
                    "type": "biological_process_or_activity"
                }
            ],
            "edges": [
                {
                    "id": "e0",
                    "source_id": "n1",
                    "target_id": "n2"
                }
            ]
        },
        "results": [
            {
                "edge_bindings": [
                    {
                        "kg_id": "1",
                        "qg_id": "e0"
                    }
                ],
                "node_bindings": [
                    {
                        "kg_id": "UBERON:0000463",
                        "qg_id": "n1"
                    },
                    {
                        "kg_id": "GO:0097099",
                        "qg_id": "n2"
                    }
                ]
            },
            {
                "edge_bindings": [
                    {
                        "kg_id": "2",
                        "qg_id": "e0"
                    }
                ],
                "node_bindings": [
                    {
                        "kg_id": "UBERON:0000465",
                        "qg_id": "n1"
                    },
                    {
                        "kg_id": "GO:0097099",
                        "qg_id": "n2"
                    }
                ]
            }
        ],
        "knowledge_graph": {
            "nodes": [
                {
                    "name": "structural constituent of albumen",
                    "id": "GO:0097099",
                    "equivalent_identifiers": [
                        "GO:0097099"
                    ],
                    "type": [
                        "named_thing",
                        "biological_entity",
                        "molecular_activity",
                        "biological_process_or_activity"
                    ]
                },
                {
                    "name": "organism substance",
                    "id": "UBERON:0000463",
                    "equivalent_identifiers": [
                        "NCIT:C13236",
                        "UBERON:0000463"
                    ],
                    "type": [
                        "named_thing",
                        "biological_entity",
                        "anatomical_entity",
                        "organismal_entity"
                    ]
                },
                {
                    "name": "material anatomical entity",
                    "id": "UBERON:0000465",
                    "equivalent_identifiers": [
                        "UBERON:0000465"
                    ],
                    "type": [
                        "named_thing",
                        "biological_entity",
                        "anatomical_entity",
                        "organismal_entity"
                    ]
                }
            ],
            "edges": [
                {
                    "predicate_id": "biolink:subclass_of",
                    "relation_label": [
                        "subclass of"
                    ],
                    "edge_source": [
                        "uberongraph.term_get_ancestors"
                    ],
                    "ctime": [
                        1595956911.393211
                    ],
                    "target_id": "UBERON:0000465",
                    "source_id": "GO:0097099",
                    "id": "1",
                    "type": "subclass_of",
                    "source_database": [
                        "uberongraph"
                    ],
                    "relation": [
                        "rdfs:subClassOf"
                    ],
                    "publications": []
                },
                {
                    "predicate_id": "biolink:subclass_of",
                    "relation_label": [
                        "subclass of"
                    ],
                    "edge_source": [
                        "uberongraph.term_get_ancestors"
                    ],
                    "ctime": [
                        1595956913.4062119
                    ],
                    "target_id": "UBERON:0000463",
                    "source_id": "GO:0097099",
                    "id": "2",
                    "type": "subclass_of",
                    "source_database": [
                        "uberongraph"
                    ],
                    "relation": [
                        "rdfs:subClassOf"
                    ],
                    "publications": []
                }
            ]
        }
    }

    overlay.overlay_support_edges(resoner_jj)
