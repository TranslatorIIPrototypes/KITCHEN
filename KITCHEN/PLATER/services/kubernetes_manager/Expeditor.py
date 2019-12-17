##############################
#
#    Just like your favorite restaurant expeditor (if its a busy one) this class will do serving the 'Plate'
#    plate is just a validated KGS compliant graph.
#
#
#############################

from kubernetes import client, config as k8_config
from KITCHEN.Common.logutil import LoggingUtil
from KITCHEN.PLATER.services.config import Config
from kubernetes.client.rest import ApiException
import json

logger = LoggingUtil.init_logging(__name__)


class Expeditor:

    def __init__(self, config: Config, build_tag):
        k8_config.load_kube_config(config['k8_config_file'], persist_config=False)

        self._build_tag = build_tag

        self._namespace = config['k8_namespace']
        self._container_name_prefix = config['neo4j_container_name']
        self._container_name = f"{self._container_name_prefix}-{build_tag}"
        self._deployment_name = self._container_name

        self._image_name = config['neo4j_image_name']
        self._api_version = config.get('k8_api_version','apps/v1')

        # k8s clients
        self._apps_client = client.AppsV1Api()
        self._core_client = client.CoreV1Api()

        self._state = 0  # @TODO Use this to maintain the status of a pod only while completing Expedition

    @staticmethod
    def delete_deployment(deployment_name, namespace):
        api_reponse = client.AppsV1Api().delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )
        return api_reponse

    @property
    def deployment_name(self):
        return self._deployment_name

    @property
    def namespace(self):
        return self._namespace

    def _create_deployment_spec(self):
        # k8s has restrictions on what could be a valid container name due to DNS issues (no under scores etc...)
        # @TODO validate that build tag is good or we might need to hash it to a DNS  compatible format
        container_name = self._container_name
        deployment_name = self._container_name
        image_name = self._image_name
        pod_label = {
            'app': container_name
        }

        # create the container
        container = client.V1Container(
            name=container_name,
            image=image_name
            # @TODO lets worry about ports after this works
        )

        # create pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=pod_label),
            spec=client.V1PodSpec(containers=[container])
        )

        # create deployment spec
        deployment_spec = client.V1DeploymentSpec(
            replicas=1,
            template=pod_template,
            selector={'matchLabels': pod_label}
        )

        deployment = client.V1Deployment(
            api_version=self._api_version,
            kind='Deployment',
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=deployment_spec
        )
        return deployment

    def deploy(self):
        deployment_spec = self._create_deployment_spec()
        api_response = self._apps_client.create_namespaced_deployment(
            body=deployment_spec,
            namespace=self.namespace,
        )
        return api_response

    def is_deployed(self):
        try:
            response = self._apps_client.read_namespaced_deployment(
                namespace=self.namespace,
                name= self.deployment_name
            )
        except ApiException as e:
            logger.error(f'Exception caught while checking if {self._deployment_name} was deployed : [x] {e.body}')
            # return false iff not found
            if json.loads(e.body)['code']== 404:
                return False
            raise e
        # return false if replicas are 0 ~ maybe it was scaled down
        return response.status.replicas > 0


if __name__ == '__main__':
    conf = Config('plater.conf')
    exp = Expeditor(conf, build_tag='build-9')
    response = exp.is_deployed()
    print(response)




