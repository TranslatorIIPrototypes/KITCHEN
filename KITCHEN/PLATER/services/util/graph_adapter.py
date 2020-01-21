import requests
import base64



class Neo4j_HTTP_Driver:
    def __init__(self, host: str, port: int,  auth: set, scheme: str = 'http'):
        self._host = host
        self._neo4j_transaction_endpoint = "/db/data/transaction/commit"
        self._scheme = scheme
        self._full_transaction_path = f"{self._scheme}://{self._host}:{port}{self._neo4j_transaction_endpoint}"
        self._port = port
        self._header = {
                'Accept': 'application/json; charset=UTF-8',
                'Content-Type': 'application/json',
                'Authorization': base64.b64encode(f"{auth[0]}:{auth[1]}".encode("utf-8"))
            }

    def run(self, query):
        """
        Runs a neo4j query.
        :param query: Cypher query.
        :type query: str
        :return: result of query.
        :rtype: dict
        """
        # make the statement dictionary
        payload = {
            "statements": [
                {
                    "statement": f"{query}"
                }
            ]
        }

        response = requests.post(
            self._full_transaction_path,
            headers=self._header,
            json=payload).json()

        return response

    def convert_to_dict(self, response):
        """
        Converts a neo4j result to a structured result.
        :param response: neo4j http raw result.
        :type response: dict
        :return: reformatted dict
        :rtype: dict
        """
        results = response.get('results')
        array = []
        if results:
            for result in results:
                cols = result.get('columns')
                if cols:
                    data_items = result.get('data')
                    for item in data_items:
                        new_row = {}
                        row = item.get('row')
                        for col_name, col_value in zip(cols, row):
                            new_row[col_name] = col_value
                        array.append(new_row)
        return array

class GraphInterface:
    """
    Singleton class for interfacing with the graph.
    """

    class _GraphInterface:
        def __init__(self, host, port, auth):
            self.driver = Neo4j_HTTP_Driver(host=host, port= port, auth= auth)
            self.schema = None


        def get_schema(self):
            """
            Gets the schema of the graph.
            :return: Dict of structure source label as outer most keys, target labels as inner keys and list of predicates
            as value.
            :rtype: dict
            """
            if self.schema is None:
                query = """
                           MATCH (a)-[x]->(b) WITH
                               filter(la in labels(a) where not la in ['named_thing', 'Concept']) as las,
                               filter(lb in labels(b) where not lb in ['named_thing', 'Concept']) as lbs,
                           type(x) as predicate
                           UNWIND las as source_label
                           UNWIND lbs as target_label 
                           RETURN DISTINCT source_label, predicate, target_label
                           """
                result = self.driver.run(query)

                structured = self.driver.convert_to_dict(result)
                schema_bag = {}
                for triplet in structured:
                    subject = triplet['source_label']
                    predicate = triplet['predicate']
                    objct = triplet['target_label']
                    if subject not in schema_bag:
                        schema_bag[subject] = {}
                    if objct not in schema_bag[subject]:
                        schema_bag[subject][objct] = []
                    if predicate not in schema_bag[subject][objct]:
                        schema_bag[subject][objct].append(predicate)
                self.schema = schema_bag
            return self.schema

        def get_node(self, node_type: str, curie: str) -> dict:
            """
            Returns a node that matches curie as its ID.
            :param node_type: Type of the node.
            :type node_type:str
            :param curie: Curie.
            :type curie: str
            :return: value of the node in neo4j.
            :rtype: dict
            """
            query = f"MATCH (c:{node_type}{{id: '{curie}'}}) return c"
            response = self.driver.run(query)

            data = response.get('results',[{}])[0].get('data', [])
            '''
            data looks like 
            [
            {'row': [{...node data..}], 'meta': [{...}]},
            {'row': [{...node data..}], 'meta': [{...}]},
            {'row': [{...node data..}], 'meta': [{...}]}
            ]            
            '''
            rows = []
            if len(data):
                from functools import reduce
                rows = reduce(lambda x, y: x + y.get('row', []), data, [])
            return rows

        def get_single_hops(self, source_type, target_type, curie):
            """
            Returns a triplets of source to target where source id is curie.
            :param source_type: Type of the source node.
            :type source_type: str
            :param target_type: Type of target node.
            :type target_type: str
            :param curie: Curie of source node.
            :type curie: str
            :return: list of triplets where each item contains source node, edge, target.
            :rtype: list
            """

            query = f'MATCH (c:{source_type}{{id: \'{curie}\'}})-[e]->(b:{target_type}) return distinct c , e, b'
            response = self.driver.run(query)
            rows = list(map(lambda data: data['row'], response['results'][0]['data']))
            return rows

        def run_cypher(self, cypher):
            """
            Runs cypher directly.
            :param cypher: cypher query.
            :type cypher: str
            :return: unprocessed neo4j response.
            :rtype: dict
            """
            return self.driver.run(cypher)

        def get_sample(self, node_type):
            """
            Returns a few nodes.
            :param node_type: Type of nodes.
            :type node_type: str
            :return: Node dict values.
            :rtype: dict
            """
            query = f"MATCH (c:{node_type}) return c limit 5"
            response = self.driver.run(query)
            rows = response['results'][0]['data'][0]['row']
            return rows

        def get_examples(self, source, target=None):
            """
            Returns an example for source node only if target is not specified, if target is specified a sample one hop
            is returned.
            :param source: Node type of the source node.
            :type source: str
            :param target: Node type of the target node.
            :type target: str
            :return: A single source node value if target is not provided. If target is provided too, a triplet.
            :rtype:
            """
            import json
            if target:
                query = f"MATCH (source:{source})-[edge]->(target:{target}) return source, edge, target limit 1"
                response = self.run_cypher(query)
                final = list(map(lambda data: data['row'], response['results'][0]['data']))
                return final
            else:
                query = f"MATCH ({source}:{source}) return {source} limit 1"
                response = self.run_cypher(query)
                final = list(map(lambda node: node[source], self.driver.convert_to_dict(response)))
                return final

    instance = None

    def __init__(self, host, port, auth):
        # create a new instance if not already created.
        if not GraphInterface.instance:
            GraphInterface.instance = GraphInterface._GraphInterface(host=host, port=port, auth=auth)

    def __getattr__(self, item):
        # proxy function calls to the inner object.
        return getattr(self.instance, item)

if __name__=="__main__":
    graph_interface = GraphInterface('192.168.99.101', 7474, ('neo4j', 'pass'))
    import json
    print(json.dumps(graph_interface.get_single_hops(source_type='chemical_substance', target_type='chemical_substance', curie='CHEBI:15377')[:5], indent=2))
    print(json.dumps(graph_interface.get_schema(), indent=4 ))
