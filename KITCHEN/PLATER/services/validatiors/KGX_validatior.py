from kgx.validator import Validator
from kgx.transformers.neo_transformer import NeoTransformer

class KGXValidator:

    def __init__(self, neo4j_uri: str, neo4j_auth: tuple):
        """

        """
        self.neo4j_transformer = NeoTransformer(uri=neo4j_uri,
                                                username=neo4j_auth[0],
                                                password=neo4j_auth[1])



    def validate_node_types(self):
        pass


    def validate(self):
        pass