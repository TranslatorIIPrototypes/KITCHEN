from starlette.requests import Request
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.schemas import OpenAPIResponse
from starlette.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_3_path

from PLATER.services.config import config
from PLATER.services.util.bl_helper import BLHelper
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.util.question import Question

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )



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
    REASONER_API_ENDPOINT = 'reasonerapi'
    SIMPLE_ONE_HOP_SPEC = 'simple'
    SUMMARY_ENDPOINT_TYPE = 'graph_summary'

    def __init__(self, graph_interface: GraphInterface):
        self.graph_interface = graph_interface
        self.bl_helper = BLHelper(config.get('BL_HOST', 'https://bl-lookup-sri.renci.org'))
        self._endpoint_loader = {
            EndpointFactory.HOP_ENDPOINT_TYPE: lambda kwargs: self.create_hop_endpoint(**kwargs),
            EndpointFactory.NODE_ENDPOINT_TYPE: lambda kwargs: self.create_node_endpoint(**kwargs),
            EndpointFactory.CYPHER_ENDPOINT_TYPE: lambda kwargs: self.create_cypher_endpoint(),
            EndpointFactory.OPEN_API_ENDPOINT_TYPE: lambda kwargs: self.create_open_api_schema_endpoint(**kwargs),
            EndpointFactory.GRAPH_SCHEMA_ENDPOINT_TYPE: lambda kwargs: self.create_graph_schema_endpoint(),
            EndpointFactory.SWAGGER_UI_ENDPOINT: lambda kwargs: self.create_swagger_ui_endpoint(**kwargs),
            EndpointFactory.REASONER_API_ENDPOINT: lambda kwargs: self.create_reasoner_api_endpoint(),
            EndpointFactory.SIMPLE_ONE_HOP_SPEC: lambda kwargs: self.create_simple_one_hop_spec_endpoint(),
            EndpointFactory.SUMMARY_ENDPOINT_TYPE: lambda kwargs: self.create_graph_summary_api_endpoint()
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

        # add reasoner api endpoint

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.REASONER_API_ENDPOINT
            )
        )

        # add one hop

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.SIMPLE_ONE_HOP_SPEC
            )
        )

        # add graph summary

        endpoints.append(
            self.create_endpoint(
                EndpointFactory.SUMMARY_ENDPOINT_TYPE
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
            # lets hold on to an example so we can use it later in reasoner api spec.
            last_curie = ''

            for source_node in graph_schema:
                target_nodes = graph_schema[source_node]
                # add /<source_type>/curie path
                example = await self.graph_interface.get_examples(source_node)
                last_curie = example[0].get('id', '') if example else last_curie
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

            # adding paths to reasoner api in opane api spec
            example_questions = Question.transform_schema_to_question_template({'gene': {'chemical_substance': ['is_affected_by']}})
            example_question = example_questions[0]
            node_ids = list(map(lambda x: x['id'], example_question[Question.QUERY_GRAPH_KEY][Question.NODES_LIST_KEY]))
            edge_ids = list(map(lambda x: x['id'], example_question[Question.QUERY_GRAPH_KEY][Question.EDGES_LIST_KEY]))
            db_returns = {
                key : {
                    'id': f'{key}\'s DB ID',
                    'name': f'{key} has name',
                }
                for key in node_ids + edge_ids}
            db_returns.update({
                f'type_{key}': f"{key}'s type" for key in edge_ids + node_ids
            })
            class GI_MOCK:
                pass
            async def run(a, b): return None
            GI_MOCK.run_cypher = run
            GI_MOCK.convert_to_dict = lambda x,y :  [db_returns]
            q = Question(example_question)
            answer_eg = await q.answer(GI_MOCK(), yank=False)
            answer_eg[Question.KNOWLEDGE_GRAPH_KEY] = {}
            answer_eg[Question.KNOWLEDGE_GRAPH_KEY][Question.NODES_LIST_KEY] = [db_returns[node_id] for node_id in
                                                                                node_ids]
            answer_eg[Question.KNOWLEDGE_GRAPH_KEY][Question.EDGES_LIST_KEY] = [db_returns[edge_id] for edge_id in
                                                                                edge_ids]

            paths['/reasonerapi'] = {
                 'get': {
                     'description': 'Returns a list of question templates '
                                    'that can be used to query this plater instance/',
                     'operationId': 'get_question_templates',
                     'parameters': [],
                     'responses': {
                         '200': {
                             'description': 'OK',
                             'content': {
                                 'application/json': {
                                     'schema': {
                                         'type': 'object',
                                         'example': example_questions
                                     }
                                 }
                             }
                         }
                     }
                 },
                'post': {
                    'description': 'Given a question graph return question graph plus answers.',
                    'operationId': 'post_question',
                    'requestBody': {
                        'description': 'Reasoner api question.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'example': example_question
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
                                        'example': answer_eg
                                    }
                                }
                            }
                        }
                    }
                }
            }


            paths['/simple_spec'] = {
                'get': {
                    'description': 'Returns a list of available predicates when choosing a single source or target '
                                   'curie. Calling this endpoint with no query parameters will return all '
                                   'possible hops for all types.',
                    'operationId': 'get_simple_spec',
                    'parameters': [{
                            'name': 'source',
                            'in': 'query',
                            'description': f'The curie of source that needs to be fetched.',
                            'required': False,
                            'schema': {
                                'type': 'string',
                                'example': 'CHEBI:33216'
                            }
                        }, {
                            'name': 'target',
                            'in': 'query',
                            'description': f'The curie of target that needs to be fetched.',
                            'required': False,
                            'schema': {
                                'type': 'string',
                                'example': 'NCBIGene:1'
                            }
                        }],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'example': [{
                                            "source_type": "chemical_substance",
                                            "target_type": "chemical_substance",
                                            "edge_type": "similar_to"
                                        }]
                                    }
                                }
                            }
                        }
                    }
                }
            }
            # add schema for graph summary

            paths['/graph/summary'] = {
                'get': {
                    'description': 'Returns summary of the graph',
                    'operationId': 'get_graph_summary',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'example': {
                                            'chemical_substance:molecular_entity:named_thing': {
                                                'gene:biological_entity:named_thing': {'directly_interacts_with': 20}
                                            }
                                        }
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

            schema = {
                'openapi': '3.0.2',
                'info': {
                    'title': f'PLATER - {build_tag}',
                },
                'paths': paths
            }
            return JSONResponse(schema)

        return Route('/openapi.json', get_handler)

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
            openapi_spec_url="./openapi.json",
        )

        async def swagger_doc_handler(request):
            return HTMLResponse(content=html_content, media_type='text/html')

        return Route('/apidocs', swagger_doc_handler)

    def create_simple_one_hop_spec_endpoint(self):

        async def get_handler(request: Request) -> JSONResponse:
            source_id = request.query_params.get('source', None)
            target_id = request.query_params.get('target', None)
            if source_id or target_id:
                source_id = urllib.parse.unquote_plus(source_id) if source_id else None
                target_id = urllib.parse.unquote_plus(target_id) if target_id else None
                minischema = []
                mini_schema_raw = await self.graph_interface.get_mini_schema(source_id, target_id)
                for row in mini_schema_raw:
                    source_labels = await self.bl_helper.get_most_specific_concept(row['source_label'])
                    target_labels = await self.bl_helper.get_most_specific_concept(row['target_label'])
                    for source_type in source_labels:
                        for target_type in target_labels:
                            minischema.append((source_type, row['predicate'], target_type))
                minischema = list(set(minischema)) # remove dups
                return JSONResponse(list(
                    map(lambda x: {'source_type': x[0], 'target_type': x[2], 'edge_type': x[1]}, minischema)
                ))
            else:
                schema = self.graph_interface.get_schema()
                reformatted_schema = []
                for source_type in schema:
                    for target_type in schema[source_type]:
                        for edge in schema[source_type][target_type]:
                            reformatted_schema.append({
                                'source_type': source_type,
                                'target_type': target_type,
                                'edge_type': edge
                            })
                return JSONResponse(reformatted_schema)

        return Route('/simple_spec', get_handler)

    def create_reasoner_api_endpoint(self):
        """
        Creates an endpoint for handling get and post requests to reasoner api endpoint.

        Get endpoint returns list of questions supported by the instance as templates.
        :return:
        """
        graph_interface = self.graph_interface

        async def get_handler(request: Request) -> JSONResponse:
            templates = Question.transform_schema_to_question_template(graph_interface.get_schema())
            return JSONResponse(templates)

        async def post_handler(request: Request) -> JSONResponse:
            try:
                request_json = await request.json()
                question = Question(request_json)
            except Exception as e:
                 return JSONResponse({"Error": f"{str(type(e))} - {e}"}, 400)
            response = await question.answer(graph_interface)
            return JSONResponse(response)

        async def wrapper(request: Request) -> JSONResponse:
            if request.method == 'GET':
                return await get_handler(request)
            else:
                return await post_handler(request)
        return Route('/reasonerapi', wrapper, methods=['GET', 'POST'])

    def create_graph_summary_api_endpoint(self):
        async def get_handler(request: Request) -> JSONResponse:
            self.graph_interface.get_schema()
            summary = self.graph_interface.summary
            return JSONResponse(summary)

        return Route('/graph/summary', get_handler)

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

