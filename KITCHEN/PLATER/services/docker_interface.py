from docker import DockerClient
from docker.tls import TLSConfig
from docker.models.images import Image
from docker.models.containers import Container
import io
import tarfile
import atexit

from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.config import config

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )


class DockerInterface(DockerClient):
    def __init__(self, base_url: str, tls_dir: str = None, version: str = '1.35'):
        logger.debug(f'[0] Initializing docker-client...connecting to {base_url}')
        kwargs = {
            'base_url': base_url,
            'version': version,
        }
        # if tls is on it mean we have to securely communicate with docker ...
        if tls_dir is not None:
            tls_dir += '/' if tls_dir[-1] != '/' else ''
            kwargs['tls'] = TLSConfig(
                client_cert=(
                    f'{tls_dir}key.pem',
                    f'{tls_dir}cert.pem'
                )
            )
        self.running_container: Container = None
        super().__init__(**kwargs)
        logger.debug('[x] Pinging docker host...')
        self.ping()
        logger.debug('[x] Pinging success')

        # register atexit. __del__ method doesn't like logging much
        atexit.register(self.kill_running_container, self.running_container)

    def kill_running_container(self, running_container: Container):
        if running_container is not None:
            logger.info(f'[x] Killing container {running_container.short_id}....')
            self.running_container.kill(9)  # 9=SIGKILL (forceful terminate)
            logger.info(f'[x] Container killed.')
            self.running_container = None

    def build_neo4j_image(self, build_name):
        """
        Builds a Neo4j image.
        :param build_name: Tag to be given to the image
        :type build_name: str
        :return: the image model
        :rtype: Image
        """
        logger.debug(f'[x] Creating image {build_name}....')
        image, logs = self.images.build(**{
            'path': 'services/resources', #
            'tag': build_name, # use build name as a tag
            'network_mode': 'host', # when running on nodes where network is managed by kubernetes
            'forcerm': True # remove intermediate containers
        })
        logger.debug(f'[x] Image created {image.short_id} ({image.tags}) ... ')
        logger.debug(f'[x] Image build logs ------------------------------------')
        #log out what docker has to say
        for log in logs:
            for key in log:
                logger.debug(f'[x] DOCKER IMAGE LOG [x] {log[key]}')
        return image

    def run_neo4j_container(self, neo4j_image: Image) -> Container:
        """
        Run the image passed.
        :param neo4j_image: Image to run
        :type neo4j_image: Image
        :return: the running container
        :rtype: Container
        """
        logger.debug(f'[x] Creating container')
        # kill running container before
        self.kill_running_container(self.running_container)

        container = self.containers.run(
            image=neo4j_image,  # image we just built
            stdin_open=True,  # keep container running
            detach=True  # detach and return
        )

        self.running_container: Container = container
        logger.debug(f'[x] created container {container.id} from {neo4j_image.short_id}--({neo4j_image.tags})')

        return container

    def copy_dump_file(self, container: Container, dump_file_path: str, neo4j_data_dir: str = '/data/'):
        """
        Copies a file to /data/ dir inside the container.
        :param container: Container to copy the file into
        :type container: Container
        :param dump_file_path: local path of the file to copy
        :type dump_file_path: str
        :param neo4j_data_dir: Data directory with in the neo4j dir. Default is /data/
        :type neo4j_data_dir:str
        :return: Nothing
        :rtype: None
        """
        logger.debug(f'[x] Copying file {dump_file_path} to {container.short_id}:/data/')
        tar_ball = io.BytesIO()
        with tarfile.open(mode='w:gz', fileobj=tar_ball) as tar_file:
            tar_file.add(dump_file_path)
        container.put_archive(neo4j_data_dir, tar_ball.getvalue())
        logger.debug(f'[x] Done copying file.')

    def exec_cmd(self, container: Container, command: str, **kwargs):
        """
        Run a command inside the container
        :param container: Container to run commands on.
        :type container: Container
        :param command: The command to run.
        :type command: str
        :param kwargs: additional kwargs to pass to container.exec_run method
        :type kwargs: dict
        :return:
        :rtype:
        """
        logger.debug(f'[x] Running {command} inside {container.short_id}')
        exit_code, out_put = container.exec_run(
            command,
            **kwargs
        )
        if exit_code:
            logger.error(f'[!] Commmand {command} failed!')
            logger.error(f'[!] {out_put.decode("utf-8")}')
        return exit_code

    def set_up_data_dir_permissions(self, container: Container,  neo4j_data_dir: str = '/data/'):
        """
        Sets up permission on data dir.
        :param container: The container to setup permissions.
        :type container: Container
        :param neo4j_data_dir: Data dir to setup.
        :type neo4j_data_dir: str
        """
        self.exec_cmd(
            container,
            f'mkdir -p {neo4j_data_dir}/databases' # make dir
        )

        self.exec_cmd(
            container,
            f'chown -R neo4j:neo4j {neo4j_data_dir}'  # change owner of dir to user neo4j
        )

        self.exec_cmd(
            container,
            f'chmod u=rwx,g=rwx {neo4j_data_dir}'  # change permission of user neo4j to read and write on that dir.
        )



if __name__ == '__main__':
    dooker = DockerInterface('tcp://localhost:2375')
    dooker.build_neo4j_image('built-by-dooker')
    image = dooker.images.list('built-by-dooker')[0]
    container = dooker.run_neo4j_container(image)
    dooker.copy_dump_file(container, 'test.dump')
    container.kill('1')






