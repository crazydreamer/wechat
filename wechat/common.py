import logging

API_KEY = ''
SECRET_KEY = ''

def get_logger(name, level='debug'):
    logger = logging.getLogger(name)
    level = eval('logging.' + level.upper())
    logger.setLevel(level)
    if not logger.handlers:
        try:
            from bae_log import handlers
            handler = handlers.BaeLogHandler(ak=API_KEY, sk=SECRET_KEY, bufcount=1)
        except Exception, e:
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
    try:
        from bae_memcache import BaeMemcache
        cache_id = ""
        cache_addr = ""
        cache = BaeMemcache(cache_id, cache_addr, API_KEY, SECRET_KEY)
    except Exception, e:
        cache = Cache()
    return cache
