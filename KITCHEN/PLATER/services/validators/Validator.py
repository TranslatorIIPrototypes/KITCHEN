###############
# Register validators here and they will all be called by the core service
# Validators should have validate class and constructor with no arguments.
#
############

from PLATER.services.validators.KGX_validator import KGX_Validator
from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.config import config

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )

class Validator():
    def __init__(self):
        self.lazy_loader  = {
            'kgx_validator': lambda : KGX_Validator()
        }


    def validate(self, kgx_dict: dict) -> bool:
        valid = True
        for validator_name in self.lazy_loader:
            validator = self.lazy_loader.get(validator_name)()
            valid = validator.validate(kgx_dict)
            if not valid:
                logger.error(f'validation via {validator_name} failed')
                break
        return valid


