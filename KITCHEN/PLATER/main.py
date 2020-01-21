import argparse
from PLATER.services.core import Plater
from Common.logutil import LoggingUtil

def parse_args(args):
    settings = {}
    build_tag = args.build_tag

    if args.dump_file:
        # settings['load'] = True
        settings['dump_file'] = args.dump_file
    plater = Plater(build_tag=build_tag, settings=settings)
    plater.run_web_server()


if __name__=='__main__':
    # first command
    # load a dump file on to a neo4j container and save it.

    parser = argparse.ArgumentParser(
        description= 'PLATER, stand up a REST-api in front of neo4j database.'
    )
    parser.add_argument(
        'build_tag', metavar='build_tag', type=str, help='Build tag is an identifier to be used for the '
                                                                    'current running instance. It will help identify'
                                                                    'containers generated.'
    )
    parser.add_argument(
        '-d',
        '--dump_file',
        help='A neo4j dump file to load into the neo4j instance. If this is specified it will force create a new'
             'container instance with the specified `build_tag`. This will DELETE existing builds.'
    )
    # parser.add_argument(
    #     '-s',
    #     '--run_server',
    #     help='Run webserver.'
    # )


    args = parser.parse_args()

    parse_args(args)