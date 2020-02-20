import copy
from functools import reduce
from PLATER.services.util.graph_adapter import GraphInterface


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

    def __init__(self, question_json):
        self._question_json = copy.deepcopy(question_json)
        self.__validate()

    def compile_cypher(self):
        question_graph = self._question_json[Question.QUERY_GRAPH_KEY]
        edges = question_graph[Question.EDGES_LIST_KEY]
        nodes = question_graph[Question.NODES_LIST_KEY]
        paths = []
        # Used to construct things guery graph returns
        returns = []

        # Create (a:type)->[e:type]->(b:type)  strings
        # append e in returned list
        for edge in edges:
            edge_type = edge.get(Question.TYPE_KEY)
            edge_type = ':' + edge_type if edge_type else ''
            source_id = edge[Question.SOURCE_KEY]
            target_id = edge[Question.TARGET_KEY]
            edge_id = edge[Question.QG_ID_KEY]
            path = f"({source_id})-[{edge_id}{edge_type}]->({target_id})"

            #append path
            paths += [path]

            #add returns
            returns += [edge_id]
            returns += [f'type({edge_id}) as type_{edge_id}']

        # make where clause for restricting node types
        # a:type{id:'curie'}
        # append a in returned list
        node_type_statements = []
        for node in nodes:
            node_id = node[Question.QG_ID_KEY]
            node_type = node[Question.TYPE_KEY]
            node_type_statements += [f"{node_id}:{node_type}"]
            if Question.KG_ID_KEY in node:
                node_type_statements += [f"{node_id}.id = \"{node[Question.KG_ID_KEY]}\""]
            returns += [node_id]
            returns += [f'labels({node_id}) as type_{node_id}']

        # join (a)-[e]->(b)
        # join where
        # join returns
        match_clause = ' , '.join(paths)
        where_clause = ' AND '.join(node_type_statements)
        return_clause = ', '.join(returns)

        cypher = f"""MATCH {match_clause}  WHERE {where_clause} RETURN {return_clause} """
        return cypher

    async def answer(self, graph_interface: GraphInterface):
        cypher = self.compile_cypher()
        results = await graph_interface.run_cypher(cypher)
        results_dict = graph_interface.convert_to_dict(results)
        node_keys = list(map(
            lambda node: node[Question.QG_ID_KEY],
            self._question_json[Question.QUERY_GRAPH_KEY][Question.NODES_LIST_KEY]))
        edge_map = {
            edge[Question.QG_ID_KEY]: edge
            for edge in self._question_json[Question.QUERY_GRAPH_KEY][Question.EDGES_LIST_KEY]
        }
        edge_keys = set(edge_map.keys())
        answer_bindings = []
        knowledge_graph = {
            Question.NODES_LIST_KEY: [],
            Question.EDGES_LIST_KEY: []
        }
        for result in results_dict:
            answer = {
                Question.EDGE_BINDINGS_KEY: {},
                Question.NODE_BINDINGS_KEY: {}
            }

            for query_graph_id in result:
                # Query should return type_<QG_ID> for all the nodes and edges where QG_ID is the nodes / edges
                # query graph id
                if query_graph_id in node_keys:
                    ### bind query_graph id with the knowledge graph id
                    types = result[f'type_{query_graph_id}']
                    result[query_graph_id]['type'] = types
                    answer[Question.NODE_BINDINGS_KEY].update({query_graph_id: result[query_graph_id]['id']})
                    knowledge_graph[Question.NODES_LIST_KEY].append(result[query_graph_id])
                    continue
                if query_graph_id in edge_keys:
                    ### bind query_graph edge with the kg id
                    # like the nodes add type to edges
                    types = result[f'type_{query_graph_id}']
                    result[query_graph_id]['type'] = types
                    answer[Question.EDGE_BINDINGS_KEY].update({query_graph_id: result[query_graph_id]['id']})
                    # Use question graph id to resolve actual result id
                    source_key = edge_map[query_graph_id][Question.SOURCE_KEY]
                    target_key = edge_map[query_graph_id][Question.TARGET_KEY]
                    result[query_graph_id][Question.SOURCE_KEY] = result[source_key]['id']
                    result[query_graph_id][Question.TARGET_KEY] = result[target_key]['id']
                    knowledge_graph[Question.EDGES_LIST_KEY].append(result[query_graph_id])
                    continue
            answer_bindings.append(answer)
        self._question_json[Question.ANSWERS_KEY] = answer_bindings
        self._question_json[Question.KNOWLEDGE_GRAPH_KEY] = knowledge_graph
        return self._question_json

    def __validate(self):
        assert Question.QUERY_GRAPH_KEY in self._question_json, "No question graph in json."
        question_graph = self._question_json[Question.QUERY_GRAPH_KEY]
        assert Question.NODES_LIST_KEY in question_graph, "No nodes in query graph"
        assert isinstance(question_graph[Question.NODES_LIST_KEY], list), "Expected nodes to be list"
        assert Question.EDGES_LIST_KEY in question_graph, "No edges in query graph"
        assert isinstance(question_graph[Question.EDGES_LIST_KEY], list), "Expected edges to be list"
        for node in question_graph[Question.NODES_LIST_KEY]:
            assert Question.TYPE_KEY in node , f"Expected {Question.TYPE_KEY} in {node}"
            assert Question.QG_ID_KEY in node, f"Expected {Question.QG_ID_KEY} in {node}"
        for edge in question_graph[Question.EDGES_LIST_KEY]:
            assert Question.QG_ID_KEY in edge, f"Expected {Question.QG_ID_KEY} in {edge}"
            assert Question.SOURCE_KEY in edge, f"Expected {Question.SOURCE_KEY} in {edge}"
            assert Question.TARGET_KEY in edge, f"Expected {Question.TARGET_KEY} in {edge}"
        # make sure everything mentioned in edges is actually refering something in the node list.
        node_ids = list(map(lambda node: node[Question.QG_ID_KEY], question_graph[Question.NODES_LIST_KEY]))
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
                            Question.QG_ID_KEY: "n1",
                            Question.TYPE_KEY: source_type,
                        },
                        {
                            Question.QG_ID_KEY: "n2",
                            Question.TYPE_KEY: target_type,
                        }
                    ],
                    Question.EDGES_LIST_KEY: []
                }
                edge_set = target_set[target_type]
                for index, edge_type in enumerate(set(edge_set)):
                    edge_dict = {
                        Question.QG_ID_KEY: f"e{index}",
                        Question.SOURCE_KEY: "n1",
                        Question.TARGET_KEY: "n2",
                        Question.TYPE_KEY: edge_type
                    }
                    question_graph[Question.EDGES_LIST_KEY].append(edge_dict)
            question_templates.append({Question.QUERY_GRAPH_KEY: question_graph})
        return question_templates


if __name__ == '__main__':
    schema  = {
      "chemical_substance": {
        "chemical_substance": [
          "similar_to"
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
    print(question.compile_cypher())
    questions[0]['query_graph']['nodes'][0]['kg_id'] = 'PUBCHEM:6302'
    del questions[0]['query_graph']['edges'][0]['type']
    q2 = Question(questions[0])
    ans = q2.answer(graph_interface=GraphInterface('localhost','7474', ('neo4j', 'ncatsgamma')))
    import asyncio
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(ans)
    print(result)
