from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.schemas import OpenAPIResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.schemas import SchemaGenerator
from starlette.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from swagger_ui_bundle import swagger_ui_3_path
from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.config import config

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )

from PLATER.services.util.graph_adapter import GraphInterface


class EndpointFactory:
    """
    This class generates HTTPEndpoint
    """
    HOP_ENDPOINT_TYPE = 'hop'
    NODE_ENDPOINT_TYPE = 'node'
    CYPHER_ENDPOINT_TYPE = 'cypher'
    OPEN_API_ENDPOINT_TYPE = 'open_api'
    GRAPH_SCHEMA_ENDPOINT_TYPE = 'graph_schema'
    SWAGGER_UI_ENDPOINT = 'swagger_ui'

    def __init__(self, graph_interface: GraphInterface):
        self.graph_interface = graph_interface
        self._endpoint_loader = {
            EndpointFactory.HOP_ENDPOINT_TYPE: lambda kwargs: self.create_hop_endpoint(**kwargs),
            EndpointFactory.NODE_ENDPOINT_TYPE: lambda kwargs: self.create_node_endpoint(**kwargs),
            EndpointFactory.CYPHER_ENDPOINT_TYPE: lambda kwargs: self.create_cypher_endpoint(),
            EndpointFactory.OPEN_API_ENDPOINT_TYPE: lambda kwargs: self.create_open_api_schema_endpoint(**kwargs),
            EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE: lambda kwargs: self.create_graph_schema_endpoint(),
            EndpointFactory.SWAGGER_UI_ENDPOINT: lambda kwargs: self.create_swagger_ui_endpoint(**kwargs),
        }

    def create_app(self, build_tag):
        """
        Creates a startlette web application, based on a neo4j backend.
        :return: starlette web application.
        :rtype: Starlette
        """
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
                EndpointFactory.OPEN_API_ENDPOINT_TYPE,
                **{
                    'build_tag': build_tag
                }
            )
        )

        # add graph schema

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE
            )
        )

        # add swagger UI

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.SWAGGER_UI_ENDPOINT,
                **{
                    'build_tag': build_tag
                }
            )
        )

        routes = list(map(lambda endpoint: endpoint, endpoints))
        app = Starlette(
            debug=int(config.get('logging_level')) == 10,
            routes=routes
        )
        # mount swagger ui files
        app.router.mount('/', app=StaticFiles(directory=f'{swagger_ui_3_path}'))
        return app

    def create_hop_endpoint(self, source_type, target_type):
        """
        Returns a Json endpoint for returning triplets for every related node types in the graph.
        :param source_type: Source node type.
        :type source_type: str
        :param target_type: Target node type.
        :type target_type: str
        :return: A request handler callable.
        :rtype: Callable
        """
        graph_interface = self.graph_interface

        async def get_handler(request: Request) -> JSONResponse:
            curie = request.path_params['curie']
            response = await graph_interface.get_single_hops(source_type, target_type, curie)
            return JSONResponse(response)

        return Route(f"/{source_type}/{target_type}/{{curie}}", get_handler)

    def create_node_endpoint(self, node_type):
        """
        Creates an endpoint handler that would return a node.
        :param node_type: Node type.
        :type node_type: str
        :return: A request handler callable.
        :rtype: Callable
        """
        graph_interface = self.graph_interface

        async def get_handler(request: Request) -> JSONResponse:
            curie = request.path_params['curie']
            response = await graph_interface.get_node(node_type, curie)
            return JSONResponse(response)

        return Route(f'/{node_type}/{{curie}}', get_handler)

    def create_cypher_endpoint(self):
        """
        Creates an endpoint handler that would return result of a cypher.
        :return: A request handler callable.
        :rtype: Callable
        """

        graph_interface = self.graph_interface

        async def post_handler(request: Request) -> JSONResponse:
            query = await request.json()
            query = query['query']
            response = await graph_interface.run_cypher(query)
            return JSONResponse(response)

        return Route('/cypher', post_handler, methods=['post'])

    def create_open_api_schema_endpoint(self, build_tag):
        """
        Creates a swagger spec for the endpoints to be created and exposes it as an endpoint too.
        :return: A request handler callable.
        :rtype: Callable
        """


        async def get_handler(request: Request) -> OpenAPIResponse:

            paths = {}

            graph_schema = self.graph_interface.get_schema()

            for source_node in graph_schema:
                target_nodes = graph_schema[source_node]
                # add /<source_type>/curie path
                example = await self.graph_interface.get_examples(source_node)
                paths[f'/{source_node}/{{curie}}'] = {
                    'get': {
                        'description': f'Returns `{source_node}` based on `curie`.',
                        'summary': f'Find {source_node} by curie.',
                        'operationId': f'get_{source_node}_by_curie',
                        'parameters': [{
                            'name': 'curie',
                            'in': 'path',
                            'description': f'The curie of {source_node} that needs to be fetched.',
                            'required': True,
                            'schema': {
                                'type': 'string'
                            }
                        }],
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'example': example
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                # add /<source_type>/<target_type>/curie paths
                for target_node in target_nodes:
                    example = await self.graph_interface.get_examples(source_node, target_node)
                    paths[f'/{source_node}/{target_node}/{{curie}}'] = {
                        'get': {
                            'description': f'Returns one hop paths from {source_node} with `curie` to target type {target_node}.',
                            'summary': f'Get one hop results from {source_node} to {target_node}.',
                            'operationId': f'get_one_hop_{source_node}_to_{target_node}',
                            'parameters': [{
                                'name': 'curie',
                                'in': 'path',
                                'description': f'The curie of {source_node} that path starts from.',
                                'required': True,
                                'schema': {
                                    'type': 'string'
                                }
                            }],
                            'responses': {
                                '200': {
                                    'description': 'OK',
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'example': example
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

            # adding schema to openapi spec

            paths['/graph/schema'] = {
                'get': {
                    'description': 'Returns an object where outer keys represent source types with second level keys as '
                                   'targets. And the values of the second level keys is the type of possible edge types'
                                   'that connect these concepts.',
                    'operationId': 'get_graph_schema',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'example': {
                                            'chemical_substance': {
                                                'gene': ['directly_interacts_with']
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # adding cypher endpoint to openapi spec

            example_cypher = 'MATCH (c) return c limit 1'
            paths['/cypher'] = {
                'post': {
                    'summary': 'Run cypher query.',
                    'description': 'Runs cypher query against the Neo4j instance, and returns an equivalent '
                                   'response exepected from a Neo4j HTTP endpoint '
                                   '(https://neo4j.com/docs/rest-docs/current/).',
                    'requestBody': {
                        'description': 'Cypher query.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'example': {
                                        'query': example_cypher
                                    }
                                }
                            }
                        },
                        'allowEmptyValue': False,
                        'required': True
                    },
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'example': await self.graph_interface.run_cypher(example_cypher)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Add build tag to all the paths
            for path in paths:
                for method in paths[path]:
                    paths[path][method]['tags'] = [{'name': build_tag}]

            schemas = SchemaGenerator(
                {
                    'openapi': '3.0.2',
                    'info': {
                        'title': f'PLATER - {build_tag}',
                    },
                    'paths': paths
                }
            )

            return schemas.OpenAPIResponse(request)

        return Route('/openapi.yml', get_handler)

    def create_graph_schema_endpoint(self):
        """
        Creates a graph schema endpoint. This endpoint is a representation of the graph schema as
        ```
        [{
            source_type: {
                target_type: [
                    'predicate_1',
                    'predicate_2'
                ]
            }
        }]
        ```
        :return: endpoint handler.
        :rtype: Callable
        """
        graph_interface = self.graph_interface

        async def get_handler(request):
            response = graph_interface.get_schema()
            return JSONResponse(response)

        return Route('/graph/schema', get_handler)

    def create_swagger_ui_endpoint(self, build_tag):
        """

       """
        # build Swagger UI
        env = Environment(
            loader=FileSystemLoader(swagger_ui_3_path)
        )
        template = env.get_template('index.j2')
        html_content = template.render(
            title=f'Plater- {build_tag}',
            openapi_spec_url="./openapi.yml",
        )

        async def swagger_doc_handler(request):
            return HTMLResponse(content=html_content, media_type='text/html')

        return Route('/apidocs', swagger_doc_handler)

    def create_endpoint(self, endpoint_type, **kwargs) -> Route:
        """
        Interfaces creation of endpoints.
        :param endpoint_type: type of endpoint to create.
        :type endpoint_type: str
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        endpoint_router = self._endpoint_loader.get(endpoint_type)
        if endpoint_router is None:
            raise TypeError(f"Unable to load endpoint type: {endpoint_type}")
        return endpoint_router(kwargs)
