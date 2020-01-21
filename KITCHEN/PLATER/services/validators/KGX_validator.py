#############
# Adaptor for KGX Validator Class
#
###########
from kgx import  Validator

from PLATER.services.util.logutil import LoggingUtil
import logging
from networkx import DiGraph
from kgx.transformers.json_transformer import JsonTransformer
import json
from PLATER.services.config import config

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )
class KGX_Validator():
    """
    Wrapper class for KGX validator
    """
    def __init__(self):
        logger.debug('Init KGX_Validator')
        self.validator = Validator()
        self.transformer = JsonTransformer()


    def validate(self, kgx_dict: dict)-> bool:
        """
        Validates  if a graph compatible against KGX rules.
        :param kgx_dict: dictionary KGX graph representation
        :return: boolean indicating validation pass
        """

        logger.debug(f'validating {json.dumps(kgx_dict, indent=2) }')
        valid = True

        try:
            # validate using kgx and check for errors and catch exceptions as errors too
            self.validator.validate(self._transform(kgx_dict))
            if len(self.validator.errors):
                logger.debug(f'validation failed due to errors - {self.validator.errors}')
                valid = False
        except Exception as ex:
            logger.debug(f'validation failed due to exception - [x] - {ex}')
            valid = False

        return valid


    def _transform(self, kgx_dict: dict) -> DiGraph:
        """
        Transforms a dictionary formatted KGX graph to networkx.DiGraph
        :param kgx_dict: dictionary KGX graph representation
        :return: networkx.DiGraph representation
        """
        self.transformer.load(kgx_dict)
        return self.transformer.graph


if __name__ == '__main__':
    logger.error('hi')