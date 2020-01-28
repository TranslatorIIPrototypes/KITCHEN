from starlette.requests import Request
from Automat.automat.core import Automat
import aiohttp


# async def proxy_to_plater(request: Request):
#     build_tag = request.path_params['build_tag']
#     source_type = request.path_params['source_type']
#     target_type = request.path_params['target_type']
#     curie = request.path_params['curie']


async def app (scope, recieve, send):
    assert scope['type'] == 'http'
    a = Automat()
    await a.handle_request(scope, recieve, send)
    # request = Request(scope, recieve)
    # print(scope['path'])
    # await send({
    #     'type': 'http.response.start',
    #     'status': 200,
    #     'headers': [
    #         [b'content-type', b'text/plain'],
    #     ]
    # })
    # await send({
    #     'type': 'http.response.body',
    #     'body': b'',
    # })

