###############
# Register validators here and they will all be called by the core service
# Validators should have validate class and constructor with no arguments.
#
############

from KITCHEN.PLATER.services.validators.KGX_validator import KGX_Validator
from KITCHEN.PLATER.logs import init_logger

logger = init_logger(__name__)

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


