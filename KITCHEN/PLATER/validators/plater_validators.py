from PLATER.services.config import config
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.logutil import LoggingUtil
from PLATER.validators.KGX_validator import KGXValidator

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


class PLATER_Validator:
    def __init__(self, graph_interface: GraphInterface):
        self.neo4j_url = f'http://{config.get("NEO4J_HOST")}:{config.get("NEO4J_HTTP_PORT")}'
        logger.debug(f'Initializing validator {self.neo4j_url}')
        self.kgx_validator = KGXValidator(graph_interface)

    def validate(self, report_to_file=True):
        """
        Runs validation
        """
        return self.kgx_validator.validate(report_to_files=report_to_file)
