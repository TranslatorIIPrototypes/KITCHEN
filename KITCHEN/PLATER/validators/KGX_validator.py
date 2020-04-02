import asyncio
import json
import os
import time

import kgx.validator
from networkx import MultiDiGraph

from PLATER.services.config import config
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.logutil import LoggingUtil

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )

class KGXValidator:
    def __init__(self, graph_interface: GraphInterface):
        self.kgxvalidator = kgx.validator.Validator()
        self.graph_interface = graph_interface
        # query how many paths are there
        query = "MATCH p=()-->() return count(p) as path_count"
        result = self.async_wrapper(self.graph_interface.run_cypher(query))
        result = self.graph_interface.convert_to_dict(result)
        self.path_count = result[0]['path_count']
        # query how many disconnected nodes are there
        query = "MATCH (n) where not (n)--() return count(n) as node_counts"
        result = self.async_wrapper(self.graph_interface.run_cypher(query))
        result = self.graph_interface.convert_to_dict(result)
        self.island_nodes_count = result[0]['node_counts']
        logger.debug(f'Graph contains {self.path_count} Paths and {self.island_nodes_count} disconnected nodes.')

    def async_wrapper(self, async_fx):
        result = asyncio.get_event_loop().run_until_complete(async_fx)
        return result

    def validate_nodes(self, graph):
        error_by_type = {}
        for id, node in graph.nodes(data=True):
            errors = self.kgxvalidator.validate_node_property_values(id, node)
            errors += self.kgxvalidator.validate_node_property_types(id, node)
            errors += self.kgxvalidator.validate_node_property_values(id, node)
            errors += self.kgxvalidator.validate_categories(id, node)
            errors += self.kgxvalidator.validate_node_properties(id, node)
            for e in errors:
                labels = ','.join(graph.nodes[e.entity].get('category', ['unidentified']))
                error_by_type[labels] = error_by_type.get(labels, [])
                error_by_type[labels].append(e.message)
                # check if name is set
        return error_by_type

    def validate_edges(self, graph):
        errors = self.kgxvalidator.validate_edges(graph)
        errors_by_type = {}
        if errors:
            for e in errors:
                error_type = e.error_type.name
                errors_by_type[error_type] = errors_by_type.get(error_type, list())
                # use set to avoid adding same error message again
                errors_by_type[error_type].append(e.message)
        # convert sets to list for json dump
        return errors_by_type

    async def get_island_nodes_page(self, start, page_size):
        """
        Grab nodes that are disconnected.
        :param start: Skip nodes upto start. 0 is initial start.
        :param page_size: number of nodes to grab
        :return: list of nodes
        """
        query = f"""MATCH (node) WHERE not (node)--() RETURN node, labels(node) as category, ID(node) as internal_id"""
        query += '\n ORDER BY internal_id'
        if start:
            query += f'\n SKIP {start}'
        limit = start + page_size
        if limit:
            query += f'\n LIMIT {limit}'

        response = await self.graph_interface.run_cypher(query)
        return self.graph_interface.convert_to_dict(response)

    async def get_paths_per_page(self, start, page_size):
        query = f"""
            MATCH (source)-[predicate]->(target)
            RETURN source, 
            predicate, 
            target, 
            TYPE(predicate) as predicate_type, 
            ID(source) as internal_source_id,
            ID(predicate) as internal_predicate_id,
            ID(target) as internal_target_id
            ORDER BY internal_predicate_id
        """
        if start:
            query += f'\n SKIP {start}'
        limit = start + page_size
        if limit:
            query += f'\n LIMIT {limit}'
        response = await self.graph_interface.run_cypher(query)
        return self.graph_interface.convert_to_dict(response)

    def make_nx_graph_from_nodes(self, nodes):
        graph = MultiDiGraph()
        for n in nodes:
            node_properties = n['node']
            node_properties['category'] = n['category']
            idd = node_properties.get('id', n['internal_id'])
            graph.add_node(idd, **node_properties)
        return graph

    def make_nx_graph_from_paths(self, paths):
        graph = MultiDiGraph()
        for p in paths:
            source = p['source']
            source['id'] = source.get('id', p['internal_source_id'])
            target = p['target']
            target['id'] = target.get('id', p['internal_target_id'])
            edge = p['predicate']
            edge['type'] = p['predicate_type']
            edge['id'] = edge.get('id', p['internal_predicate_id'])
            graph.add_node(source['id'], **source)
            graph.add_node(target['id'], **target)
            graph.add_edge(source['id'], target['id'], edge['id'], **edge)
        return graph

    def validate(self, report_to_files=True):
        start_time = time.time()
        node_errors = {}
        edge_errors = {}
        logger.info(f'Found {self.island_nodes_count} disconnected nodes.')
        logger.info(f'Validating disconnected nodes')
        step = 1000
        for i in range(0, self.island_nodes_count, step):
            logger.debug(f'Fetching {step} skipping first {i}')
            coroutine = self.get_island_nodes_page(i, step)
            nodes = self.async_wrapper(coroutine)
            logger.debug(f'got nodes... running validation')
            nodes_graph = self.make_nx_graph_from_nodes(nodes)
            node_errors.update(
                self.validate_nodes(nodes_graph)
            )
            complete = 100 if self.island_nodes_count < step else (i / self.island_nodes_count) * 100
            logger.info(f'{complete}% complete.')

        for i in range(0, self.path_count, step):
            logger.debug(f'Fetching {step} paths skipping first {i} paths.')
            coroutine = self.get_paths_per_page(i, step)
            paths = self.async_wrapper(coroutine)
            paths_graph = self.make_nx_graph_from_paths(paths)
            edge_errors.update(
                self.validate_edges(paths_graph)
            )
            complete = 100 if self.path_count < step else (i / self.path_count) * 100
            logger.info(f'{complete}% complete.')

        if report_to_files:

            logger.info('Writing report to files.')
            with open(os.path.join(os.path.dirname(__file__), '..', 'logs', 'node_errors.json'), 'w') as f:
                for k in node_errors:
                    node_errors[k] = list(set(node_errors[k]))
                json.dump(node_errors, f, indent=2)
            with open(os.path.join(os.path.dirname(__file__), '..', 'logs', 'edge_errors.json'), 'w') as f:
                for k in edge_errors:
                    edge_errors[k] = list(set(edge_errors[k]))
                json.dump(edge_errors, f, indent=2)
            logger.info('KGX validation error Files placed under logs/node_errors.json and logs/edges_errors.json')
        print(f'Took {time.time() - start_time}')
        if node_errors or edge_errors:
            return False
        return True
