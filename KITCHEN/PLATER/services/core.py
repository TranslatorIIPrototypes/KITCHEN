###################
#
#
#
####################
import logging
import requests
import time
import uvicorn

from PLATER.services.config import config
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.endpoint_factory import EndpointFactory
from PLATER.services.util.logutil import LoggingUtil


logger = LoggingUtil.init_logging(__name__,
                                  #
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


class Plater:
    def __init__(self, build_tag: str, settings: dict):

        self.settings = settings
        validate = self.settings.get('validate', False)
        self.config = config
        if validate:
            logger.debug('[0] Validation turned on.')
        self.build_tag = build_tag
        self.graph_adapter = GraphInterface(
            self.config.get('NEO4J_HOST'),
            self.config.get('NEO4J_HTTP_PORT'),
            (
                self.config.get('NEO4J_USERNAME'),
                self.config.get('NEO4J_PASSWORD')
            )
        )
        self.endpoint_factory = EndpointFactory(self.graph_adapter)

    def run_web_server(self):
        """
        Runs a Uvicorn web server instance by creating a starlette app on the setup.
        Expects neo4j to be up.
        """
        logger.debug('[0] Starting web server')
        app = self.endpoint_factory.create_app(self.build_tag)
        web_server_host = self.config.get('WEB_HOST', '127.0.0.1')
        web_server_port: int = int(self.config.get('WEB_PORT', 8080))
        uvicorn.run(
            app,
            host=web_server_host,
            port=web_server_port
        )

    @staticmethod
    def send_heart_beat(automat_host, build_tag):
        import time
        heart_rate = config.get('heart_rate', 30)
        logging.getLogger('requests').setLevel(logging.CRITICAL)
        logger.debug(f'contacting {automat_host}')
        automat_heart_beat_url = f'{automat_host}/heartbeat'
        plater_address = config.get('PLATER_SERVICE_ADDRESS')
        if not plater_address:
            logger.error('PLATER_SERVICE_ADDRESS environment variable not set. Please set this variable'
                         'to the address of the host PLATER is running on.')
            raise ValueError('PLATER_SERVICE_ADDRESS cannot be None when joining automat cluster.')
        payload = {
            'host': plater_address,
            'tag': build_tag,
            'port': config.get('WEB_PORT', 8080)
        }
        while True:
            try:
                resp = requests.post(automat_heart_beat_url, json=payload, timeout=0.5)
                logger.debug(f'heartbeat to {automat_host} returned {resp.status_code}')
            except Exception as e:
                logger.error(f'[X] Error contacting automat sever {e}')
            time.sleep(heart_rate)

