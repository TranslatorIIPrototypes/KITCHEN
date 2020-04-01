from kgx.validator import Validator, ValidationError, ErrorType, MessageLevel
from kgx.transformers.neo_transformer import NeoTransformer
from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.config import config
import time
import json

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


class KGXValidator:
    def __init__(self, neo4j_uri: str, neo4j_auth: tuple):
        """

        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_auth = neo4j_auth

        self.validator = Validator()

        logger.debug(f'Graph contains {self.graph_paths_count}')

    def get_part_of_graph(self, start, end):
        """
        Fetches part of the graph.
        """
        neo4j_transformer = NeoTransformer(uri=self.neo4j_uri,
                                           username=self.neo4j_auth[0],
                                           password=self.neo4j_auth[1])
        neo4j_transformer.load(start, end)
        return neo4j_transformer.graph

    @property
    def graph_paths_count(self):
        neo4j_transformer = NeoTransformer(uri=self.neo4j_uri,
                                           username=self.neo4j_auth[0],
                                           password=self.neo4j_auth[1])
        return neo4j_transformer.count()

    def validate_sub_graph(self, start, end):
        """
        Loops through the graph and validates it.
        """
        mini_graph = self.get_part_of_graph(start, end)
        node_errors = {}
        edge_errors = {}
        # try to cache nodes in the multigraph that have int ids
        # remove them from the multigraph so kgx can go on with doing its thing
        # report these nodes.
        nodes_to_remove = []
        for id, node_attr in mini_graph.nodes(data=True):
            if isinstance(id, int):
                labels = ','.join(node_attr.get('category', ['unidentified']))
                nodes_to_remove.append(id)
                node_errors[labels] = node_errors.get(labels, set())
                node_errors[labels].add('Node id cannot be integer')
        mini_graph.remove_nodes_from(nodes_to_remove)
        # make sure we have stuff left
        if len(mini_graph):
            edge_errors = self.validate_edges(mini_graph)
            node_errors.update(self.validate_nodes(mini_graph))

        return edge_errors, node_errors

    def validate_nodes(self, graph):
        errors = self.validator.validate_nodes(graph)
        error_by_type = {}
        if errors:
            for e in errors:
                labels = frozenset(graph.nodes[e.entity].get('category', ['unidentified']))
                error_by_type[labels] = error_by_type.get(labels, [])
                error_by_type[labels].append(e.message)
        # convert back to dict to dump as json
        response = {}
        for k, value in error_by_type.items():
            l = ','.join(k)
            response[l] = response.get(l, [])
            for e in value:
                response[l].append(e)
        return response

    def validate_edges(self, graph):
        errors = self.validator.validate_edges(graph)
        errors_by_type = {}
        if errors:
            for e in errors:
                error_type = e.error_type.name
                errors_by_type[error_type] = errors_by_type.get(error_type, list())
                # use set to avoid adding same error message again
                errors_by_type[error_type].append(e.message)
        # convert sets to list for json dump
        return errors_by_type

    def validate(self, report_to_files=True):
        start_time = time.time()
        # batch here is number of paths to grab and step through the graph till everything is consumed
        batch = self.graph_paths_count
        node_errors = {}
        edge_errors = {}
        total_paths = batch
        for i in range(0, total_paths, batch):
            start = i
            end = start + batch + 1
            # for some reason kgx returns nothing if skip and limit
            # are equal in its compiled cypher. Here start is skip and
            # batch is limit
            e_errors, n_errors = self.validate_sub_graph(start, end)
            # convert things values to list
            for error_type, value in e_errors.items():
                e_errors[error_type] = list(value)
            for label, value in n_errors.items():
                n_errors[label] = list(value)
            node_errors.update(n_errors)
            edge_errors.update(e_errors)
        if report_to_files:
            logger.info('Writing report to files.')
            with open('../logs/node_errors.json', 'w') as f:
                json.dump(node_errors, f, indent=2)
            with open('../logs/edge_errors.json', 'w') as f:
                json.dump(edge_errors, f, indent=2)
            logger.info('Files placed under logs/node_errors.json and logs/edges_errors.json')
        print(f'Took {time.time() - start_time}')
        if node_errors or edge_errors:
            return False
        return True
