import logging


def get_logger(name, level='debug'):
    logger = logging.getLogger(name)
    level = eval('logging.' + level.upper())
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("|%(levelname)s - %(asctime)s - %(name)s - %(message)s"))
        logger.addHandler(handler)
    return logger

class Cache(object):
    '''
    just a local cache
    '''
    __tmp = {}
    def get(self, key):
        return self.__tmp.get(key)
    
    def set(self, key, value):
        self.__tmp[key] = value

def get_cache():
    cache = Cache()
    return cache
