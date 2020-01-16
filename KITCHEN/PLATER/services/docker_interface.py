from docker import DockerClient
from docker.tls import TLSConfig
from docker.models.images import Image
from docker.models.containers import Container
import io, tarfile

class DockerInterface(DockerClient):
    def __init__(self, base_url: str = "tcp://192.168.99.100:2376",  version: str = '1.35'):
        # Todo move to config in core service
        self.tls_config = TLSConfig(
            client_cert=(
                'C:\\Users\\19193\\.docker\\machine\\machines\\dev\\cert.pem',
                'C:\\Users\\19193\\.docker\\machine\\machines\\dev\\key.pem'
            )
        )
        super().__init__(base_url=base_url, version=version, tls=self.tls_config)
        self.ping()

    def build_neo4j_image(self, build_name='test-build'):

        image = self.images.build(**{
            'path': 'resources', #
            'tag': build_name, # use build name as a tag
            'network_mode': 'host', # when running on nodes where network is managed by kubernetes
            'forcerm': True # remove intermediate containers
        })

    def run_neo4j_container(self, neo4j_image: Image) -> Container:
        container = self.containers.run(
            image=neo4j_image,  # image we just built
            stdin_open=True,  # keep container running
            detach=True  # detach and return
        )
        return container

    def copy_dump_file(self, container: Container, dump_file_path: str):
        tar_ball = io.BytesIO()
        with tarfile.open(mode='w:gz', fileobj=tar_ball) as tar_file:
            tar_file.add(dump_file_path)
        container.put_archive('/data/dump.db', tar_ball.getvalue())








if __name__ == '__main__':
    dooker = DockerInterface()
    dooker.build_neo4j_image('built-by-dooker')
    image = dooker.images.list('built-by-dooker')[0]
    container = dooker.run_neo4j_container(image)
    dooker.copy_dump_file(container, 'test.dump')







