import aiohttp

from aiohttp.web import HTTPException
import traceback
from automat.config import config
from automat.util.logutil import LoggingUtil


logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


async def async_get_json(url, headers={}, timeout=5*6):
    """
        Gets json response from url asyncronously.
    """
    client_timeout = aiohttp.ClientTimeout(connect=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error = f"Failed to get response from {url}. Status code {response.status}"
                    logger.error(error)
                    return {
                        'error': error
                    }, response.status
                return await response.json(), 200
        except HTTPException as e:
            logger.error(f'error contacting {url} -- {e}')
            logger.debug(traceback.print_exc())
            return {
                'error': f"Backend server at {url} caused  {e}"
            }, 500
        except Exception as e:
            logger.error(f"Failed to get response from {url}.")
            logger.debug(traceback.print_exc())
            return {
                'error': f'Internal server error {e}'
            }, 500


async def async_post_json(url, headers={}, body='', timeout=5*6):
    client_timeout = aiohttp.ClientTimeout(connect=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        try:
            async with session.post(url, data=body, headers=headers) as response:
                if response.status != 200:
                    try:
                        content = await response.json()
                    except:
                        content = await response.content.read()
                        content = {
                            'error': content.decode('utf-8')
                        }
                    logger.error(f'{url} returned {response.status}. {content}')
                    return content, response.status
                return await response.json(), 200
        except Exception as e:
            logger.error(f"Failed to get response from {url}.")
            return {
                'error': f"Server returned {e}"
            }, 500


async def async_get_text(url,headers={}):
    """
        Gets text response from url asyncronously
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.error(f'Failed to get response from {url}, returned status : {response.status}')
                return ''
            return await response.text()


async def async_get_response(url, headers={}, timeout=5*60):
    """
    Returns the whole reponse object
    """
    client_timeout = aiohttp.ClientTimeout(connect=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        async with session.get(url, headers=headers) as response:
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

