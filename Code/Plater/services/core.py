###################
#
# Core service of the plater that co-ordinates Accepting a stream of KGS data , Validates it and loads onto a Neo4j POD
#
####################

from Code.Plater.services.validators.Validator import Validator
from Code.Plater.services.config import Config



class Plater:
    def __init__(self, build_tag, validate = True):
        self.settings = {
            'validate': validate
        }
        self.validator = Validator()
        self.build_tag = build_tag
        self.config = Config('plater.conf')



    def plate(self, kgx_dict):
        valid = True
        if self.settings['validate'] :
            valid = self.validator(kgx_dict)
        if valid:
            self.deploy_graph(self.build_tag, kgx_dict)






