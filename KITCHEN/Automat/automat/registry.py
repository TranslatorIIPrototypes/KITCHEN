import time
from typing import NamedTuple
from automat.config import config
from automat.util.logutil import LoggingUtil


logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format'),
                                  config.get('logging_file_path')
                                  )


class Heartbeat(NamedTuple):
    host: str
    port: int
    tag: str

    def __str__(self):
        return f'{self.host}:{self.port}'

    def __eq__ (self, tag):
        return self.tag == tag


class Registry:
    """
    Registry with expiry.
    """

    # Enums for our expiration margin
    # Warning if now -  last seen is age + TTL_WARNING
    # OFFLINE if last seen is age + TTL_OFFLINE
    TTL_WARNING = 2
    TTL_OFFLINE = 3
    TTL_DELETE_ENTRY = 10*60  # Delete if last update was more than a minute.
    TTL_ALIVE = 0
    LABELS = {
        TTL_WARNING: 'warn ',
        TTL_OFFLINE: 'off line',
        TTL_DELETE_ENTRY: 'off line - deleted',
        TTL_ALIVE: 'alive'
    }
    instance = None

    def __init__(self, age: int):
        if not Registry.instance:
            Registry.instance = Registry.__Registry(age)
        else:
            Registry.instance.age = age

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __Registry:
        def __init__(self, age: int):
            """
                    :param age: Time in milliseconds of expiry.
                    """
            self._registry = {}
            self.age = age

        def refresh(self, key: str):
            """
            Refreshes expiry of key.
            :param key: Entry to update expiry
            :return: Status of the registry.
            """
            self._registry[key] = time.time()
            #  Also update the whole thing
            return self.get_registry()

        def get_registry(self):
            """
            Computes expiry entries when called.
            :return: Parsed registry.
            """
            response = {}
            delete_keys = []
            for heart_beat in self._registry:
                key = heart_beat.tag
                response[key] = {
                    'url': str(heart_beat)
                }
                last_seen = self._registry[heart_beat]
                now = time.time()
                ttl = (now - last_seen - self.age)
                if ttl > Registry.TTL_DELETE_ENTRY:
                    # response[key]['status'] = Registry.LABELS[Registry.TTL_DELETE_ENTRY]
                    delete_keys.append(heart_beat)  # once done with this loop remove expired entries.
                elif ttl > Registry.TTL_OFFLINE:
                    response[key]['status'] = Registry.LABELS[Registry.TTL_OFFLINE]
                elif ttl > Registry.TTL_WARNING:
                    response[key]['status'] = Registry.LABELS[Registry.TTL_WARNING]
                else:
                    response[key]['status'] = Registry.LABELS[Registry.TTL_ALIVE]

            for heart_beat in delete_keys:
                del self._registry[heart_beat]
            return response

        def get_host_by_tag(self, tag):
            for hearts in self._registry:
                if hearts == tag:
                    return str(hearts)
            return ''
