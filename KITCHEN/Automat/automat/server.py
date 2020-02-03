from automat.core import Automat

automat = Automat()

async def app (scope, recieve, send):
    assert scope['type'] == 'http'
    await automat.handle_request(scope, recieve, send)