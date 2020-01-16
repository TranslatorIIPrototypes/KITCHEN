from PLATER.services.endpoint_factory import EndpointFactory
from PLATER.services.util.graph_adapter import GraphInterface


graph_interface = GraphInterface('robokopdev.renci.org', 7474, ('neo4j', 'ncatsgamma'))
endpoint_factory = EndpointFactory(graph_interface)


app = endpoint_factory.create_app()

