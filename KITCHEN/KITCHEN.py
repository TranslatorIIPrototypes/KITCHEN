#######################################################
#
# KITCHEN.py
# Created on:      06-Jan-2020 9:28:36 AM
# Original author: powen
#
# Implementation of the KITCHEN process:
#
# Brings the KITCHEN process together and exucutes all componentns in a sequenced manner.
#######################################################
from INA.INAintrospect import INA_introspect
from CHEF.CHEFprocess import CHEFprocess
from COOKER.COOKERprocess import COOKERprocess

#from PLATER import PLATER

import os
import logging
from Common.logutil import LoggingUtil

# create a class logger
logger = LoggingUtil.init_logging("KITCHEN.orchestrate", logging.INFO, format_sel='medium', log_file_path=f'{os.environ["KITCHEN"]}/logs/')

#######
# Main - Stand alone entry point KITCHEN orchestration
#######
if __name__ == '__main__':
    # get the data definition
    data_def = ''

    # directory with GTEx data to process
    intermediate_out_path = '.'

    # create a new introspection object
    INA = INA_introspect(data_def, intermediate_out_path)

    try:
        logger.info(f'Starting INA introspection.')

        # load up all the GTEx data
        recipe: dict = INA.introspect()

        # was the execution successful
        if recipe is not None:
            logger.info(f'INA introspection complete. Starting CHEF processing.')

            # continue with the orchestration
            common_format: dict = CHEFprocess(recipe)

            # check the return, continue if possible
            if common_format is not None:
                logger.info(f'CHEF processing complete. Starting COOKER process.')

                # continue with the orchestration
                cooked = COOKERprocess(common_format)

                # check the return, continue if possible
                # if cooked is not None:
                #     rv = PLATERprocess(cooked)
                # else:
                #     logger.error('Error in PLATER processing')

            else:
                logger.error('Error in CHEF processing. Aborting.')
        else:
            logger.error('Error in INA RECIPE. Aborting.')

    except Exception as e:
        logger.exception(e)
        raise
