import aiohttp
from aiohttp.web import HTTPException
import traceback
from Automat.automat.config import config
from Automat.automat.util.logutil import LoggingUtil


logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )


async def async_get_json(url, headers = {}):
    """
        Gets json response from url asyncronously.
    """
    async with aiohttp.ClientSession() as session :
        try:
            async with session.get(url, headers= headers) as response:
                if response.status != 200:
                    error = f"Failed to get response from {url}. Status code {response.status}"
                    logger.error(error)
                    return {
                        'error': error
                    }
                return await response.json()
        except HTTPException as e:
            logger.error(f'error contacting {url} -- {e}')
            logger.debug(traceback.print_exc())
            return {
                'error': f"Backend server at {url} caused  {e}"
            }
        except Exception as e:
            logger.error(f"Failed to get response from {url}.")
            logger.debug(traceback.print_exc())
            return {
                'error': f'Internal server error {e}'
            }



async def async_post_json(url, headers= {} , body = ''):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=body, headers=headers) as response:
                if response.status != 200:
                    error = f"Failed to get response from {url}. Status code {response.status}"
                    logger.error(error)
                    return {
                        'error': error
                    }
                return await response.json()
        except Exception as e:
            logger.error(f"Failed to get response from {url}.")
            return {
                'error': f"Server returned {e}"
            }


async def async_get_text(url,headers = {}):
    """
        Gets text response from url asyncronously
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers= headers) as response:
            if response.status != 200:
                logger.error(f'Failed to get response from {url}, returned status : {response.status}')
                return ''
            return await response.text()

async def async_get_response(url, headers= {}, timeout=5*60):
    """
    Returns the whole reponse object
    """
    timeout = aiohttp.ServerTimeoutError
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers= headers) as response:
            try:
                json = await response.json()
            except:
                json = {}
            try:
                text = await response.text()
            except:
                text = ''
            try:
                raw = await response.read()
            except:
                raw = ''
            return {
                'headers' : response.headers,
                'json': json,
                'text': text,
                'raw': raw,
                'status': response.status
            }

