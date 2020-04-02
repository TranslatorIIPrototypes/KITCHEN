
from automat.config import config
from automat.util.logutil import LoggingUtil
from automat.server import app
import uvicorn

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )

if __name__=='__main__':
    logger.info('[0] Starting web server')
    web_server_host = config.get('WEB_HOST', '127.0.0.1')
    web_server_port: int = int(config.get('WEB_PORT', 8081))
    uvicorn.run(
        app,
        host=web_server_host,
        port=web_server_port,
        log_level='error'
    )
    logger.info(f'[0] Webserver listening at {web_server_host}:{web_server_port}')
