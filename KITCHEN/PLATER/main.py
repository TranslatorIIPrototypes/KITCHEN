import argparse
from PLATER.services.core import Plater
from PLATER.services.util.logutil import LoggingUtil
from PLATER.services.config import config
import threading

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )
def parse_args(args):
    """
    Parse
    :param args:
    :return:
    """
    settings = {}
    build_tag = args.build_tag
    if args.automat_host:
        logger.debug(f'Running in clustered mode about to join {args.automat_host}')

        # start heart beat thread.
        heart_beat_thread = threading.Thread(
            target=Plater.send_heart_beat,
            args=(args.automat_host, build_tag),
            daemon=True
        )
        heart_beat_thread.start()

    plater = Plater(build_tag=build_tag, settings=settings)
    plater.run_web_server()


if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description= 'PLATER, stand up a REST-api in front of neo4j database.'
    )
    parser.add_argument(
        'build_tag', metavar='build_tag', type=str, help='Build tag is an identifier to be used for the '
                                                                    'current running instance. It will help identify'
                                                                    'containers generated.'
    )
    parser.add_argument(
        '-a',
        '--automat_host',
        help='Needs to be a full http/https url. Eg. http://<automat_location>:<automat_port>'
             'If you have an Automat (https://github.com/TranslatorIIPrototypes/KITCHEN/tree/master/KITCHEN/Automat) '
             'cluster and you\'d like this instance to be accessible via the Automat interface.'
             'Needs PLATER_SERVICE_ADDRESS env variable to the host name of where this instance is deployed.'

    )


    args = parser.parse_args()
    parse_args(args)
