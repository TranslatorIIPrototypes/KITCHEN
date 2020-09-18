from PLATER.services.config import config
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.util.logutil import LoggingUtil
# from PLATER.validators.KGX_validator import KGXValidator
from PLATER.validators.build_compare import BuildComparisionValidator

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


class PLATER_Validator:
    def __init__(self, graph_interface: GraphInterface, reset_summary: bool):
        self.neo4j_url = f'http://{config.get("NEO4J_HOST")}:{config.get("NEO4J_HTTP_PORT")}'
        logger.debug(f'Initializing validator {self.neo4j_url}')
        # self.kgx_validator = KGXValidator(graph_interface)
        self.build_comparision = BuildComparisionValidator(graph_interface, reset_summary)

    def validate(self, report_to_file=True):
        """
        Runs validation
        """
        kgxValid = self.kgx_validator.validate()
        if not kgxValid:
            logger.warning(f'Graph is not KGX compliant. '
                           f'View {self.kgx_validator.edge_errors_file} and {self.kgx_validator.node_errors_file} '
                           f'to see full error report.')
        build_indifferent = self.build_comparision.validate()
        if not build_indifferent:
            logger.warning(f'Graph is different from previous plater instance.'
                           f'View {self.build_comparision.diff_file} to view full report.')
        # return kgxValid and build_indifferent
        return self.kgx_validator.validate(report_to_files=report_to_file)
