import copy
from functools import reduce
from PLATER.services.util.graph_adapter import GraphInterface

class Question:

    def __init__(self, question_json):
        self._question_json = copy.deepcopy(question_json)
        self.__validate()

    def compile_cypher(self):
        question_graph = self._question_json['question_graph']
        edges = question_graph['edges']
        nodes = question_graph['nodes']
        paths = []
        returns = []
        for edge in edges:
            edge_type = edge.get('type')
            edge_type = ':' + edge_type if edge_type else ''
            path = f"({edge['source_id']})-[{edge['id']}{edge_type}]->({edge['target_id']}) "
            paths += [path]
            returns.append(edge['id'])

        node_type_statements = []
        for node in nodes:
            node_type_statements += [f"{node['id']}:{node['type']}"]
            if 'curie' in node:
                node_type_statements += [f"{node['id']}.id = \"{node['curie']}\""]
            returns.append(node['id'])

        match_clause = ' , '.join(paths)
        where_clause = ' AND '.join(node_type_statements)
        return_clause = ', '.join(returns)

        cypher = f"""MATCH {match_clause}  WHERE {where_clause} RETURN {return_clause} """
        return cypher

    async def answer(self, graph_interface: GraphInterface):
        cypher = self.compile_cypher()
        results = await graph_interface.run_cypher(cypher)
        results_dict = graph_interface.convert_to_dict(results)
        node_keys = list(map(lambda node: node['id'], self._question_json['question_graph']['nodes']))
        edge_map = { edge['id'] : edge for edge in self._question_json['question_graph']['edges']}
        edge_keys = set(edge_map.keys())
        answer_bindings = []
        knowledge_graph = {
            'nodes': [],
            'edges': []
        }
        for result in results_dict:
            answer = {
                'node_bindings': {},
                'edge_bindings': {}
            }
            for key in result:
                if key in node_keys:
                    answer['node_bindings'].update({key: result[key]['id']})
                    knowledge_graph['nodes'].append(result[key])
                    continue
                if key in edge_keys:
                    answer['edge_bindings'].update({key: result[key]['id']})
                    # Use question graph id to resolve actual result id
                    source_key = edge_map[key]['source_id']
                    target_key = edge_map[key]['target_id']
                    result[key]['source_id'] = result[source_key]['id']
                    result[key]['target_id'] = result[target_key]['id']
                    knowledge_graph['edges'].append(result[key])
                    continue
            answer_bindings.append(answer)
        self._question_json['answers'] = answer_bindings
        self._question_json['knowledge_graph'] = knowledge_graph
        return self._question_json

    def __validate(self):
        assert 'question_graph' in self._question_json, "No question graph in json."
        question_graph = self._question_json['question_graph']
        assert 'nodes' in question_graph, "No nodes in question graph"
        assert isinstance(question_graph['nodes'], list), "Expected nodes to be list"
        assert 'edges' in question_graph, "No edges in question graph"
        assert isinstance(question_graph['edges'], list), "Expected edges to be list"
        for node in question_graph['nodes']:
            assert 'type' in node
            assert 'id' in node
        for edge in question_graph['edges']:
            assert 'id' in edge
            assert 'source_id' in edge
            assert 'target_id' in edge
        # make sure everything mentioned in edges is actually refering something in the node list.
        node_ids = list(map(lambda node: node['id'], question_graph['nodes']))
        mentions = reduce(lambda accu, value: accu + value,
                          list(map(lambda edge: [
                              edge['source_id'],
                              edge['target_id']
                          ], question_graph['edges'])), [])
        assert reduce(lambda x, y: x and (y in node_ids), mentions, True), "Some edge metions don't have matching " \
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
                        "id": "n1",
                        "type": "Type 1",
                        "curie": "{{curie}}"
                    },
                    {
                        "id" : "n2",
                        "type": "Type 2",
                        "curie": "{{curie}}"
                    }
                ],
                "edges":[
                    {
                        "id": "e1",
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
                quesion_graph = {
                    "nodes": [
                        {
                            "id": "n1",
                            "type": source_type,
                        },
                        {
                            "id": "n2",
                            "type": target_type,
                        }
                    ],
                    "edges": []
                }
                edge_set = target_set[target_type]
                for index, edge_type in enumerate(set(edge_set)):
                    edge_dict = {
                        "id": f"e{index}",
                        "source_id": "n1",
                        "target_id": "n2",
                        "type": edge_type
                    }
                    quesion_graph['edges'].append(edge_dict)
            question_templates.append({"question_graph": quesion_graph})
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