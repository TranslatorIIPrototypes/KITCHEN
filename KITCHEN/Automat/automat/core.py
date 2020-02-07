import asyncio
from automat.registry import Registry, Heartbeat
from automat.config import config
from automat.util.logutil import LoggingUtil
from automat.util.async_client import async_get_json, async_get_response, async_post_json
from starlette.responses import JSONResponse, HTMLResponse, PlainTextResponse
from jinja2 import Environment, FileSystemLoader
from swagger_ui_bundle import swagger_ui_3_path
from starlette.staticfiles import StaticFiles
import json
import yaml

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )


class Automat:
    def __init__(self):
        self.registry = Registry(age=1)
        self.config = config
        self.swagger_ui_html = Automat.setup_swagger_ui_html()

    # /heartbeat
    async def handle_heartbeat(self, scope, receive, send):
        body = await Automat.read_body(receive)
        heart_beat_json = json.loads(body.decode('utf-8'))

        heart_beat = Heartbeat(host=heart_beat_json['host'],
                               port=heart_beat_json['port'],
                               tag=heart_beat_json['tag'])

        current_state = self.registry.refresh(heart_beat)
        json_response = JSONResponse(current_state)
        await json_response(scope, receive, send)

    # /openapi.yml
    async def handle_open_api_yaml(self, scope, receive, send):
        ### For each registered endpoint try and grab its open_api_spec.
        logger.debug(f'paths for open_api specs of each server')
        open_api_spec = {
            'openapi': '3.0.2',
            'info': {
                'title': f'Automat',
            },
            'paths': {}
        }
        server_status = self.registry.get_registry()
        tasks = []
        for tag in server_status:
            server = server_status[tag]['url']
            tasks.append(self.get_swagger_paths(server, tag))
        # do requests parallel
        responses = await asyncio.gather(*tasks, return_exceptions=False)
        for response in responses:
            # Expecting something like
            # { tag : open_api_spec_object }
            #
            if not response.items():
                continue
            tag, response = response.popitem()
            spec_paths = response.get('paths')
            if not spec_paths:
                continue
            # append the tag with the build tag ,
            # this way we can route to them from UI too...
            for spec_path in spec_paths:
                new_path = f'/{tag}{spec_path}'
                open_api_spec['paths'][new_path] = spec_paths[spec_path]
        open_api_spec['paths']['/registry'] = {
            'get': {
                'description': 'Returns list of available PLATER instances.'
                               'An entry from this list can be a prefix to route requests to specific PLATER backend',
                'operationId': 'get_question_templates',
                'parameters': [],
                'tags': ['automat'],
                'responses': {
                     '200': {
                         'description': 'OK',
                         'content': {
                             'application/json': {
                                 'schema': {
                                     'type': 'object',
                                     'example': ['plater-1', 'plater-2']
                                 }
                             }
                         }
                     }
                 }
            }
        }
        response = JSONResponse(open_api_spec)
        await response(scope, receive, send)

    # /<x>/*
    async def handle_route_to_backend(self, scope, receive, send, backend_server_url, path):
        final_path = f'http://{backend_server_url}/{"/".join(path)}'
        logger.debug(f'[0] proxing request to {final_path}')
        if scope['method'] == 'GET':
            response = await async_get_json(final_path, Automat.parse_headers_to_dict(scope['headers']))
        elif scope['method'] == 'POST':
            body = await Automat.read_body(receive)
            response = await async_post_json(
                final_path,
                Automat.parse_headers_to_dict(scope['headers']),
                body
            )
        await Automat.send_json_response(scope, receive, send, response)

    # /registry
    async def handle_registry(self, scope, receive, send):
        await Automat.send_json_response(scope, receive, send, list(self.registry.get_registry().keys()))

    # /<Swagger ui files>
    @staticmethod
    async def handle_static_files(scope, receive, send):
        static_file = StaticFiles(directory=swagger_ui_3_path)
        await static_file(scope, receive, send)

    # /apidocs
    async def handle_swagger_docs(self, scope, recieve, send):
        html_response = HTMLResponse(content=self.swagger_ui_html, media_type='text/html')
        await html_response(scope, recieve, send)

    async def handle_request(self, scope, receive, send):
        # get the backend we want to get to
        path = list(filter(lambda x: x != '', scope['path'].split('/')))
        logger.debug(f'{path}')
        # redirect index to apidocs ??
        if not path:
            await self.handle_swagger_docs(scope, receive, send)
            return

        root_path = path[0]

        # IF API DOCS WAS REQUESTED JUST RETURN THAT
        if root_path == 'apidocs':
            await self.handle_swagger_docs(scope, receive, send)
            return

        if root_path == 'openapi.yml':
            await self.handle_open_api_yaml(scope, receive, send)
            return

        if root_path == 'heartbeat':
            await self.handle_heartbeat(scope, receive, send)
            return

        if root_path == 'registry':
            await self.handle_registry(scope, receive, send)
            return

        backend_sever_url = self.registry.get_host_by_tag(root_path)
        if backend_sever_url:
            logger.debug(f'[0] found entry for backend server {root_path} --- {backend_sever_url}')
            await self.handle_route_to_backend(scope, receive, send, backend_sever_url, path[1:])
            return
        try:
            await self.handle_static_files(scope, receive, send)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def setup_swagger_ui_html():
        env = Environment(
            loader=FileSystemLoader(swagger_ui_3_path)
        )
        template = env.get_template('index.j2')
        html_content = template.render(
            title=f'Automat',
            openapi_spec_url="./openapi.yml",
        )
        return html_content

    @staticmethod
    def parse_headers_to_dict(headers):
        return {key[0].decode('utf-8'): key[1].decode('utf-8') for key in headers}

    @staticmethod
    async def read_body(receive):
        """
        Read and return the entire body from an incoming ASGI message.
        """
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body

    @staticmethod
    async def send_json_response(scope, receive, send, data):
        json_response = JSONResponse(data)
        await json_response(scope, receive, send)

    @staticmethod
    async def send_404_response(scope, receive, send):
        json_response = JSONResponse({
            'error': f'No registered backend servers on {scope["path"]}'
        }, status_code=404)
        await json_response(scope, receive, send)

    @staticmethod
    async def get_swagger_paths(server_url,tag,  timeout=5*6):
        open_api_path = '/openapi.json'
        full_path = f'http://{server_url}{open_api_path}'
        response = await async_get_json(full_path, timeout=timeout)
        if 'error' in response:
            logger.error(response['error'])
            return {}
        logger.debug(response)
        return {tag: response}




