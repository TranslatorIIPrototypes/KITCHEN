###################
#
# Main coordination of the plater app happens here.
#
####################

from PLATER.services.validators.Validator import Validator
from PLATER.services.docker_interface import DockerInterface
from PLATER.services.config import config
from PLATER.services.util.graph_adapter import GraphInterface
from PLATER.services.endpoint_factory import EndpointFactory
from PLATER.services.util.logutil import LoggingUtil

import uvicorn


logger = LoggingUtil.init_logging(__name__,
                                  #
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )

class Plater:
    def __init__(self, build_tag: str, settings: dict):

        self.settings = settings
        validate = self.settings.get('validate', False)
        self.config = config
        if validate:
            logger.debug('[0] Validation turned on.')
            self.validator = Validator()

        self.build_tag = build_tag


        # here we try to build and commit a container with build tag and the dump file already loaded.
        if self.settings.get('load'):
        # docker connection settings, if socket is set up with tls
        # we will assume that cert.pem and key.pem files are iht the tls path
        # and exist as such.
            self.docker_interface = DockerInterface(
                base_url=self.config.get('DOCKER_URL'),
                tls_dir=self.config.get('DOCKER_TLS_FILES_PATH')
            )
            logger.debug(f"[0] Loading dump file {self.settings.get('dump_file')}")
            self.build_neo4j_image_with_dump()

        self.graph_adapter = GraphInterface(
            self.config.get('NEO4J_HOST'),
            self.config.get('NEO4J_HTTP_PORT'),
            (
                self.config.get('NEO4J_USERNAME'),
                self.config.get('NEO4J_PASSWORD')
            )
        )
        self.endpoint_factory = EndpointFactory(self.graph_adapter)

    def plate(self, kgx_dict: dict):
        """

        :param kgx_dict:
        :type kgx_dict:
        :return:
        :rtype:
        """
        # @TODO make this do more stuff like upload stuff and etc....
        valid = True
        if self.settings['validate']:
            valid = self.validator(kgx_dict)
        if valid:
            self.deploy_graph(self.build_tag, kgx_dict)

    def run_web_server(self):
        """
        Runs a Uvicorn web server instance by creating a starlette app on the setup.
        Expects neo4j to be up.
        """
        app = self.endpoint_factory.create_app()
        web_server_host = self.config.get('WEB_HOST', '127.0.0.1')
        web_server_port = self.config.get('WEB_PORT', 8080)
        uvicorn.run(
            app,
            host=web_server_host,
            port=web_server_port
        )

    def build_neo4j_image_with_dump(self):
        docker_repository = 'new'
        # to keep track of images to delete
        image_ids_to_remove = []

        old_image = self.docker_interface.images.get(f'{docker_repository}:{self.build_tag}')
        logger.debug(f'[x] Found old image {old_image.short_id}, ({old_image.labels})')
        image_ids_to_remove.append(old_image.id)
        self.docker_interface.images.remove(old_image.id)

        base_image = self.docker_interface.build_neo4j_image(self.build_tag)
        # get the image we just built
        image = self.docker_interface.images.list(self.build_tag)[0]
        container = self.docker_interface.run_neo4j_container(image)

        neo4j_data_dir = '/data2/'

        # define a new data dir for our new image
        # committing original image after loading data doesn't really save the data inside the container.
        # This is because /data is defined as a volume in neo4j base image
        # to work this around we can define a new 'data' directory that will be used by neo4j processes and
        # load data there.

        neo4j_data_dir_env_var = f'NEO4J_dbms_directories_data={neo4j_data_dir}'

        # setup data dir

        self.docker_interface.set_up_data_dir_permissions(container, neo4j_data_dir)

        # copy dump file
        self.docker_interface.copy_dump_file(container,
                                             dump_file_path=self.settings.get('dump_file'),
                                             neo4j_data_dir=neo4j_data_dir)

        # save image
        new_image = container.commit(
            repository=docker_repository,
            tag=self.build_tag,
            changes=f'ENV {neo4j_data_dir_env_var}'
        )

        # kill the committed container, and run new instance of the image
        # for our env to take full effect in configuring neo4j

        self.docker_interface.kill_running_container(container)
        container = self.docker_interface.run_neo4j_container(new_image)

        dump_file_name = self.settings.get('dump_file').split('/')[-1]

        # neo4j load dump data command.

        command = f'bin/neo4j-admin load --from {neo4j_data_dir}{dump_file_name}'
        logger.info(f'[x] Running command {command} on container {container.short_id}')

        exit_code = self.docker_interface.exec_cmd(
            container,
            command,
            **{
                'environment': [
                    neo4j_data_dir_env_var
                ]
            })

        if exit_code:
            logger.error(
                f'[!] Load command failed exiting... '
            )
            # if we don't have a valid archive nothing more to do...
            return

        logger.info('f[x] Committing image with loaded data')
        # save the loaded image.

        # again set file permissions for safety

        self.docker_interface.set_up_data_dir_permissions(container, neo4j_data_dir)

        # before commiting try to remove existing image with same <docker_repository>:<build_tag>

        logger.debug(f'removing image  {docker_repository}:{self.build_tag}')

        new_image = container.commit(
            repository=docker_repository,
            tag=self.build_tag,
            changes=f'ENV {neo4j_data_dir_env_var}'
        )

        self.docker_interface.kill_running_container(container)
        logger.info(f'[x] Image created {docker_repository}:{self.build_tag} ({new_image.short_id})')

        logger.info(f'[x] Removing uncessary images')
        # for image_id in image_ids_to_remove:
        #     result = self.docker_interface.images.remove(
        #         image_id,
        #         True,  # -f flag on docker rmi
        #     )
        #     logger.info(f'[x] Removed image - {image_id}')