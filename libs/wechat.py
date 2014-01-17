# coding=utf-8
import urllib2
import logging
import json
import wc_config as conf
from time import time


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("|%(levelname)s - %(asctime)s - %(name)s: %(message)s"))
        logger.addHandler(sh)
    return logger

class WeChatError(Exception):
    '''
    抛出异常并记录日志
    '''
    def __init__(self, info):
        self.info = info
        self.log = get_logger(WeChatError.__name__, logging.ERROR)
        self.log.error(info)
    
    def __str__(self):
        return repr(self.info)

class Wechat(object):
    '''
    中间操作方法(如获取access token)返回self以链式调用
    '''
    
    # TODO:get from memcache
    __ac_token = None
    __ac_timestamp = None
    
    def __init__(self, **option):
        '''
        初始化参数集option需包含微信token,appid,appsecret以获取access token
        '''
        self.log = get_logger(Wechat.__name__, logging.DEBUG)
        self._errcode = None
        if option:
            self.token = option['token']
            self.appid = option['appid']
            self.appsecret = option['appsecret']
            self.refreshACtoken()
        
    ######通用方法######
    def _valid(self, signature, timestamp, nonce, echostr=None):
        '''
        验证消息真实性,每次开发者接收用户消息的时候，微信也都会带上前面三个参数
        '''
        import hashlib
        tmpList = [self.token, timestamp, nonce]
        tmpList.sort()
        tmpstr = "%s%s%s" % tuple(tmpList)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            raise WeChatError('valid failed!')
        
    def _checkError(self, result):
        '''
        检查微信响应的信息有无错误,无错则返回self
        '''
        assert(result)
        if result.has_key('errcode') and result['errcode'] != 0:
            self._errcode = result['errcode']
            raise WeChatError(result['errmsg'] + '(%d)' % self._errcode)
        return self

    def httpReq(self, url, data=None):
        '''
        发送http请求,根据data是否为空发送GET or POST
        '''
        resp = urllib2.urlopen(url, data)
        result = json.load(resp)
        self._checkError(result)
        return result
        
    def refreshACtoken(self):
        '''
        全局变量保存actoken,若超过存活期则从微信API重新获取
        '''
        if Wechat.__ac_token is None or (time() - Wechat.__ac_timestamp) > conf.AC_TOKEN_EXPIRES_IN:
            url = conf.AUTH_URL % (self.appid, self.appsecret)
            result = self.httpReq(url)
            Wechat.__ac_token = result['access_token']
            Wechat.__ac_timestamp = time()
            self.log.debug('已刷新actoken: ' + str(Wechat.__ac_token))
        return self
    

    def sendMsg(self, openid, type, **arg):
        '''
        设置主动回复消息,类型有text,image,music,news,voice,video
        arg -- 一个dict
        '''
        msg_type=conf.MSGTYPE[type]
        msg = {"touser":openid, "msgtype":msg_type}
        msg[msg_type] = {}
        for k, v in arg.items():
            msg[msg_type][k] = v
        data = json.dumps(msg, ensure_ascii=False)
        url = conf.CUSTOM_SEND_URL % Wechat.__ac_token
        self.httpReq(url, data)
        return self
        
    
    #######自定义菜单######
    def createMenu(self, fp=None, **menu):
        '''
        传入流对象或者一个dict,转化成json以调用请求
        '''
        if fp:
            data = fp.read()
        else:
            data = json.dump(menu, ensure_ascii=False)
        url = conf.MENU_CREATE_URL % Wechat.__ac_token        
        self.httpReq(url, data)
        return self
        
    def getMenu(self):
        '''
        获取已设置的menu,返回一个dict
        '''
        url = conf.MENU_GET_URL % Wechat.__ac_token
        return self.httpReq(url)
    
    def deleteMenu(self):
        '''
        删除已设置的menu
        '''
        url = conf.MENU_DELETE_URL % Wechat.__ac_token
        self.httpReq(url)
        return self
            
    ######用户管理######
    def getUserInfo(self, openid):
        '''
        获取用户基本信息,返回一个dict
        openid -- 唯一用户标识符
        return 
            subscribe     用户是否订阅该公众号标识，值为0时，代表此用户没有关注该公众号，拉取不到其余信息。
            openid     用户的标识，对当前公众号唯一
            nickname     用户的昵称
            sex     用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
            city     用户所在城市
            country     用户所在国家
            province     用户所在省份
            language     用户的语言，简体中文为zh_CN
            headimgurl     用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空
            subscribe_time     用户关注时间，为时间戳。如果用户曾多次关注，则取最后关注时间
        '''
        url = conf.USER_INFO_URL % (Wechat.__ac_token, openid)
        return self.httpReq(url)
    
    def getUserFollowed(self, openid=None):
        '''
        获取关注者列表,返回一个dict
        openid -- 第一个拉取的OPENID，不填默认从头开始拉取
        return
            total     关注该公众账号的总用户数
            count     拉取的OPENID个数，最大值为10000
            data     列表数据，OPENID的列表
            next_openid     拉取列表的后一个用户的OPENID
        '''
        if openid:
            url = conf.USER_GET_URL % (Wechat.__ac_token, openid)
        else:
            url = conf.USER_GET_URL % (Wechat.__ac_token, openid)
        
        return self.httpReq(url)
    
    # TODO:用户分组管理,网页授权
    

