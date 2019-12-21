import requests
import base64



class Neo4j_HTTP_Driver:
    def __init__(self, host: str, port: int,  auth: set):
        """

        :param host:
        :param auth:
        """
        self._host = host
        self._neo4j_transaction_endpoint = "/db/data/transaction/commit"
        self._full_transaction_path = f"http://{self._host}:{port}{self._neo4j_transaction_endpoint}"
        self._port = port
        self._header = {
                'Accept' : 'application/json; charset=UTF-8',
                'Content-Type' : 'application/json',
                'Authorization' : base64.b64encode(f"{auth[0]}:{auth[1]}".encode("utf-8"))
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






class Graph_Interface:

    def __init__(self, host, port, auth):
        self.driver = Neo4j_HTTP_Driver(host=host, port= port, auth= auth)


    def get_schema(self):
        neo_result = self.driver.run(
            'Call apoc.meta.schema'
        )
        return neo_result

if __name__=="__main__":
    graph_interface = Graph_Interface('localhost', 7474, ('neo4j', 'ncatsgamma'))
    print(len(graph_interface.get_schema()['results'][0]['data'][0]['row'][0]))

