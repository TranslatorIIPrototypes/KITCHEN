import copy
from functools import reduce
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.qgraph_compiler import cypher_query_answer_map, flatten_semilist
import time
import asyncio

class Question:

    #SPEC VARS
    QUERY_GRAPH_KEY='query_graph'
    KG_ID_KEY='kg_id'
    QG_ID_KEY='qg_id'
    ANSWERS_KEY='results'
    KNOWLEDGE_GRAPH_KEY='knowledge_graph'
    NODES_LIST_KEY='nodes'
    EDGES_LIST_KEY='edges'
    TYPE_KEY='type'
    SOURCE_KEY='source_id'
    TARGET_KEY='target_id'
    NODE_BINDINGS_KEY='node_bindings'
    EDGE_BINDINGS_KEY='edge_bindings'
    CURIE_KEY = 'curie'

    def __init__(self, question_json):
        self._question_json = copy.deepcopy(question_json)
        self.__validate()

    def compile_cypher(self):
        return cypher_query_answer_map(self._question_json[Question.QUERY_GRAPH_KEY])

    async def answer(self, graph_interface: GraphInterface, yank=True):
        cypher = self.compile_cypher()
        print(cypher)
        s = time.time()
        results = await graph_interface.run_cypher(cypher)
        end = time.time()
        print(f'grabbing results took {end - s}')
        results_dict = graph_interface.convert_to_dict(results)
        answer_bindings = []
        for result in results_dict:
            edge_bindings = []
            for e in result.get('edges', []):
                edge_binding = {
                    Question.KG_ID_KEY: e.get('kg_id'),
                    Question.QG_ID_KEY: e.get('qg_id')
                }
                edge_bindings.append(edge_binding)

            node_bindings = []
            for n in result.get('nodes', []):
                node_bindings.append(
                    {
                        Question.KG_ID_KEY: n['kg_id'],
                        Question.QG_ID_KEY: n['qg_id']
                    }
                )
            answer = {
                Question.EDGE_BINDINGS_KEY: edge_bindings,
                Question.NODE_BINDINGS_KEY: node_bindings
            }

            answer_bindings.append(answer)
        self._question_json[Question.ANSWERS_KEY] = answer_bindings
        s = time.time()
        if yank == True:
            self._question_json[Question.KNOWLEDGE_GRAPH_KEY] = await self.yank(answer_bindings, graph_interface)
        e = time.time()
        print(f'pulling answers back took {e - s}')
        return self._question_json

    async def yank(self, answers, graph_interface: GraphInterface):
        """
        Pull neo4j data for all the mini ids
        :param answer_bindings:
        :return:
        """
        node_ids = []
        edge_ids = []
        for answer in answers:
            node_ids += list(map(lambda node_binding: node_binding[self.KG_ID_KEY], answer[self.NODE_BINDINGS_KEY]))
            edge_ids += list(map(lambda edge_binding: edge_binding[self.KG_ID_KEY], answer[self.EDGE_BINDINGS_KEY]))
        node_ids = list(set(flatten_semilist(node_ids)))
        edge_ids = list(set(flatten_semilist(edge_ids)))
        return await self.get_properties(graph_interface, edge_ids, node_ids)

    async def get_properties(self, graph_interface: GraphInterface, edge_ids, node_ids):
        """Get properties associated with edges and nodes."""
        cypher_get_nodes = f"""
        MATCH (node) where node.id in {node_ids} return collect({{node: node, type: labels(node)}}) as nodes 
        """
        s = time.time()
        nodes_full = await graph_interface.run_cypher(cypher_get_nodes)
        e = time.time()
        print(f'grabbing nodes toolk {e -s}')
        nodes_full = graph_interface.convert_to_dict(nodes_full)
        nodes_full = nodes_full[0]['nodes']
        nodes = []
        for node in nodes_full:
            node_properties = node['node']
            node_properties.update({
                'type': node['type']
            })
            nodes.append(
                node_properties
            )
        s = time.time()

        edges = await self.get_edge_properties(graph_interface, edge_ids)
        e = time.time()
        print(f'grabbing endges took {e-s}')
        return {
            self.NODES_LIST_KEY: nodes,
            self.EDGES_LIST_KEY: edges
        }

    async def get_edge_properties(self, graph_interface: GraphInterface, edge_ids, fields=None):
        if not edge_ids:
            return []
        functions = {
            'source_id': 'startNode(e).id',
            'target_id': 'endNode(e).id',
            'type': 'type(e)'
        }

        if fields is not None:
            prop_string = ', '.join(
                [f'{key}:{functions[key]}' if key in functions else f'{key}:e.{key}' for key in fields])
        else:
            prop_string = ', '.join([f'{key}:{functions[key]}' for key in functions] + ['.*'])
        chunk_size = 1024
        chunks = [edge_ids[start: start + chunk_size] for start in range(0, len(edge_ids), chunk_size)]
        tasks = []
        for ids in chunks:
            batch = ' '.join(ids)
            statement = f"" \
                f"CALL db.index.fulltext.queryRelationships('edge_id_index', '{batch}') YIELD relationship " \
                f"WITH relationship as e RETURN collect(e{{{prop_string}}}) as edges"
            print(f'grabbing enges{statement}')
            tasks.append(graph_interface.run_cypher(statement))

        answers = await asyncio.gather(*tasks)
        response = []
        for answer in answers:
            if answer.get('errors'):
                print(f'got neo4j error {answer.get("errors")}')
            answer = graph_interface.convert_to_dict(answer)
            if len(answer):
                response += answer[0]['edges']
        return response

    def __validate(self):
        assert Question.QUERY_GRAPH_KEY in self._question_json, "No question graph in json."
        question_graph = self._question_json[Question.QUERY_GRAPH_KEY]
        assert Question.NODES_LIST_KEY in question_graph, "No nodes in query graph"
        assert isinstance(question_graph[Question.NODES_LIST_KEY], list), "Expected nodes to be list"
        assert Question.EDGES_LIST_KEY in question_graph, "No edges in query graph"
        assert isinstance(question_graph[Question.EDGES_LIST_KEY], list), "Expected edges to be list"
        for node in question_graph[Question.NODES_LIST_KEY]:
            assert Question.TYPE_KEY in node , f"Expected {Question.TYPE_KEY} in {node}"
            assert 'id' in node, f"Expected `id` in {node}"
        for edge in question_graph[Question.EDGES_LIST_KEY]:
            assert 'id' in edge, f"Expected `id` in {edge}"
            assert Question.SOURCE_KEY in edge, f"Expected {Question.SOURCE_KEY} in {edge}"
            assert Question.TARGET_KEY in edge, f"Expected {Question.TARGET_KEY} in {edge}"
        # make sure everything mentioned in edges is actually refering something in the node list.
        node_ids = list(map(lambda node: node['id'], question_graph[Question.NODES_LIST_KEY]))
        mentions = reduce(lambda accu, value: accu + value,
                          list(map(lambda edge: [
                              edge[Question.SOURCE_KEY],
                              edge[Question.TARGET_KEY]
                          ], question_graph[Question.EDGES_LIST_KEY])), [])
        assert reduce(lambda x, y: x and (y in node_ids), mentions, True), "Some edge mentions don't have matching " \
                                                                           "nodes. Please check question graph."

    @staticmethod
    def transform_schema_to_question_template(graph_schema):
        """
        Returns array of Templates given a graph schema
        Eg: if schema looks like
           {
            "Type 1" : {
                "Type 2": [
                    "edge 1"
                ]
            }
           }
           We would get
           {
            "question_graph": {
                "nodes" : [
                    {
                        "qg_id": "n1",
                        "type": "Type 1",
                        "kg_id": "{{curie}}"
                    },
                    {
                        "qg_id" : "n2",
                        "type": "Type 2",
                        "kg_id": "{{curie}}"
                    }
                ],
                "edges":[
                    {
                        "qg_id": "e1",
                        "type": "edge 1",
                        "source_id": "n1",
                        "target_id": "n2"
                    }
                ]
            }
           }
        :param graph_schema:
        :return:
        """
        question_templates = []
        for source_type in graph_schema:
            target_set = graph_schema[source_type]
            for target_type in target_set:
                question_graph = {
                    Question.NODES_LIST_KEY: [
                        {
                            'id': "n1",
                            Question.TYPE_KEY: source_type,
                        },
                        {
                            'id': "n2",
                            Question.TYPE_KEY: target_type,
                        }
                    ],
                    Question.EDGES_LIST_KEY: []
                }
                edge_set = target_set[target_type]
                for index, edge_type in enumerate(set(edge_set)):
                    edge_dict = {
                        'id': f"e{index}",
                        Question.SOURCE_KEY: "n1",
                        Question.TARGET_KEY: "n2",
                        Question.TYPE_KEY: edge_type
                    }
                    question_graph[Question.EDGES_LIST_KEY].append(edge_dict)
            question_templates.append({Question.QUERY_GRAPH_KEY: question_graph})
        return question_templates


if __name__ == '__main__':
    schema  = {
      "gene": {
        "biological_process_or_activity": [
          "actively_involved_in"
        ],
        "named_thing": [
          "similar_to"
        ]
      },
      "named_thing": {
        "chemical_substance": [
          "similar_to"
        ],
        "named_thing": [
          "similar_to"
        ]
      }
    }
    import json
    questions = Question.transform_schema_to_question_template(schema)
    print(questions)
    question = Question(questions[0])
    questions[0]['query_graph']['nodes'][1]['curie'] = 'MONDO:0005148'
    questions[0]['query_graph']['nodes'][1]['type'] = 'disease'
    questions[0]['query_graph']['edges'][0]['type'] = 'treats'
    questions[0]['query_graph']['nodes'][0]['type'] = 'chemical_substance'
    q2 = Question(questions[0])
    ans = q2.answer(graph_interface=GraphInterface('localhost','7474', ('neo4j', 'ncatsgamma')))
    import asyncio
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(ans)
    print(json.dumps(result, indent=2))
