from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.schemas import SchemaGenerator
from PLATER.services.util.graph_adapter import GraphInterface



class EndpointFactory:
    """
    This class generates HTTPEndpoint
    """
    HOP_ENDPOINT_TYPE = 'hop'
    NODE_ENDPOINT_TYPE = 'node'
    CYPHER_ENDPOINT_TYPE = 'cypher'
    OPEN_API_ENDPOINT_TYPE = 'open_api'
    GRAPH_SCHEMA_ENDPOINT_TYPE='graph_schema'

    def __init__(self, graph_interface: GraphInterface):
        self.graph_interface = graph_interface
        self._endpoint_loader = {
            EndpointFactory.HOP_ENDPOINT_TYPE: lambda kwargs: self.create_hop_endpoint(**kwargs),
            EndpointFactory.NODE_ENDPOINT_TYPE: lambda kwargs: self.create_node_endpoint(**kwargs),
            EndpointFactory.CYPHER_ENDPOINT_TYPE: lambda kwargs: self.create_cypher_endpoint(),
            EndpointFactory.OPEN_API_ENDPOINT_TYPE: lambda kwargs: self.create_open_api_schema_endpoint(),
            EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE: lambda kwargs: self.create_graph_schema_endpoint()
        }

    def create_app(self):
        graph_schema = self.graph_interface.get_schema()
        # first create Hop endpoints
        endpoints = []
        node_types = []
        for source_node in graph_schema:
            node_types.append(source_node)
            target_nodes = graph_schema[source_node]
            for target_node in target_nodes:
                node_types.append(target_node)
                endpoints.append(
                    self.create_endpoint(
                        EndpointFactory.HOP_ENDPOINT_TYPE,
                        **{
                            'source_type': source_node,
                            'target_type': target_node
                        }
                    )
                )

        # remove duplicates
        node_types = set(node_types)
        # create node endpoints
        for node in node_types:
            endpoints.append(
                self.create_endpoint(
                    EndpointFactory.NODE_ENDPOINT_TYPE,
                    **{
                        'node_type': node
                    }
                )
            )

        # add cypher endpoint

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.CYPHER_ENDPOINT_TYPE
            )
        )

        # add open_api spec

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.OPEN_API_ENDPOINT_TYPE
            )
        )

        # add graph schema

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE
            )
        )

        routes = list(map(lambda endpoint: endpoint, endpoints))
        app = Starlette(
            debug=True,
            routes=routes
        )
        return app

    def create_hop_endpoint(self, source_type, target_type):
        """

        """
        graph_interface = self.graph_interface

        async def get_handler(request: Request) -> JSONResponse:
            curie = request.path_params['curie']
            response = graph_interface.get_single_hops(source_type, target_type, curie)
            return JSONResponse(response)

        return Route(f"/{source_type}/{target_type}/{{curie}}", get_handler)

    def create_node_endpoint(self, node_type):

        graph_interface = self.graph_interface

        async def get_handler(request: Request) -> JSONResponse:
            curie = request.path_params['curie']
            response = graph_interface.get_node(node_type, curie)
            return JSONResponse(response)

        return Route(f'/{node_type}/{{curie}}', get_handler)

    def create_cypher_endpoint(self):
        """

        """

        graph_interface = self.graph_interface

        async def post_handler(request: Request) -> JSONResponse:
            query = await request.json()
            query = query['query']
            response = graph_interface.run_cypher(query)
            return JSONResponse(response)

        return Route('/cypher', post_handler, methods=['post'])

    def create_open_api_schema_endpoint(self):
        paths = {}

        graph_schema = self.graph_interface.get_schema()

        for source_node in graph_schema:
            target_nodes = graph_schema[source_node]
            # add /<source_type>/curie path
            paths[f'/{source_node}/{{curie}}'] = {
                'get': {
                    'description': f'Returns `{source_node}` based on curie.',
                    'summary': f'Find {source_node} by curie.',
                    'operationId': f'get_{source_node}_by_curie',
                    'parameters': {
                        'name': 'curie',
                        'in': 'path',
                        'description': f'The curie of {source_node} that needs to be fetched.',
                        'required': True,
                        'schema': {
                            'type': 'string'
                        }
                    }
                }
            }

            # add /<source_type>/<target_type>/curie paths
            for target_node in target_nodes:
                paths[f'/{source_node}/{target_node}/{{curie}}'] = {
                    'get': {
                        'description': f'Returns one hop paths from {source_node} with `curie` to target type {target_node}.',
                        'summary': f'Get one hop results from {source_node} to {target_node}.',
                        'operationId': f'get_one_hop_{source_node}_to_{target_node}',
                        'parameters': {
                            'name': 'curie',
                            'in': 'path',
                            'description': f'The curie of {source_node} that needs that path starts from.',
                            'required': True,
                            'schema': {
                                'type': 'string'
                            }
                        }
                    }
                }

        schemas = SchemaGenerator(
            {
                "openapi": "3.0.0",
                "info": {
                    "title": "Example API", "version": "1.0"
                },
                "paths": paths
            }
        )

        return Route('/openapi', schemas.OpenAPIResponse)

    def create_graph_schema_endpoint(self):
        """

        """
        graph_interface = self.graph_interface
        async def get_handler(request):
            response = graph_interface.get_schema()
            return JSONResponse(response)
        return Route('/graph/schema', get_handler)

    def create_endpoint(self, endpoint_type, **kwargs) -> Route:
        """

        """
        endpoint_router = self._endpoint_loader.get(endpoint_type)
        if endpoint_router is None:
            raise TypeError(f"Unable to load endpoint type: {endpoint_type}")
        return endpoint_router(kwargs)




