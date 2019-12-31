import requests
import base64


class Neo4j_HTTP_Driver:
    def __init__(self, host: str, port: int,  auth: set, scheme: str = 'http'):
        """
        :param host:
        :param auth:
        """
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
        :param query:
        :return:
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


class GraphInterface:
    def __init__(self, host, port, auth):
        self.driver = Neo4j_HTTP_Driver(host=host, port= port, auth= auth)

    def get_schema(self):
        # TODO: replace this by a real call to neo4j
        return {
              "chemical_substance": {
                  "gene": [
                      "directly_interacts_with"
                  ]
              },
              "gene": {
                  "disease": [
                      "has_basis_in"
                  ]
              }
             }

        # return {
        #     'Query': f"TODO: execute and parse schema query against neo4j."
        # }

    def get_node(self, node_type: str, curie: str) -> dict:
        query = f"MATCH (c:{node_type}{{id: '{curie}'}}) return c"
        response = self.driver.run(query)
        rows = response['results'][0]['data'][0]['row']
        return rows

    def get_single_hops(self, source_type, target_type, curie):

        query = f'MATCH (c:{source_type}{{id: \'{curie}\'}})-[e]->(b:{target_type}) return distinct c , e, b'
        print(query)
        response = self.driver.run(query)
        rows = list(map(lambda data: data['row'], response['results'][0]['data']))
        return rows

    def run_cypher(self, cypher):
        return self.driver.run(cypher)

    def get_sample(self, node_type):
        query = f"MATCH (c:{node_type}) return c limit 5"
        response = self.driver.run(query)
        rows = response['results'][0]['data'][0]['row']
        return rows

    def get_graph_schema(self):
        query = """
            match (a)-[x]->(b) with
                filter(la in labels(a) where not la in ['named_thing', 'Concept']) as las,
                filter(lb in labels(b) where not lb in ['named_thing', 'Concept']) as lbs,
            type(x) as predicate
            unwind las as la unwind lbs as lb
            return distinct predicate, la, lb
            """
        result = self.driver.run(query)
        records = [list(r) for r in result]
        return records


if __name__=="__main__":
    graph_interface = GraphInterface('localhost', 7474, ('neo4j', 'ncatsgamma'))
    # print(graph_interface.get_sample('chemical_substance')[0]['id'])
    import json
    # print(json.dumps(graph_interface.get_single_hops(source_type='chemical_substance', target_type='chemical_substance', curie='CHEBI:15377')[:5], indent=2))
    print(json.dumps(graph_interface.get_schema(), indent=4 ))




    # print(len(graph_interface.get_schema()['results'][0]['data'][0]['row'][0]))

