import logging

def get_logger(name, level='debug'):
    logger = logging.getLogger(name)
    level=eval('logging.'+level.upper())
    logger.setLevel(level)
    if not logger.handlers:
        try:
            #require to replace with your available one
            from bae_log import handlers
            handler = handlers.BaeLogHandler(ak='',sk='')
        except Exception, e:
            handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter("|%(levelname)s - %(asctime)s - %(name)s - %(message)s"))
        logger.addHandler(handler)
    return logger

class Cache(object):
    '''
    just a local cache in single process
    '''
    __tmp={}
    def get(self,key):
        return self.__tmp.get(key)
    
    def set(self,key,value):
        self.__tmp[key]=value

def get_cache():
    try:
        #require to replace with your available one
        from bae_memcache import BaeMemcache
        cache_id = ''
        cache_addr = ''
        api_key = ''
        secret_key = ''
        cache = BaeMemcache(cache_id, cache_addr, api_key, secret_key)
    except Exception, e:
        cache = Cache()
    return cache