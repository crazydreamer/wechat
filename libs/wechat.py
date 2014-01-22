# coding=utf-8
import urllib2
import json
import config as conf
import common
from time import time
try:
    from pylibmc import Client
    cache = Client()
except Exception, e:
    cache = common.Cache()
    
get_logger = common.get_logger

class WeChatError(Exception):
    '''
    抛出异常并记录日志
    '''
    def __init__(self, info):
        self.info = info
        self.log = get_logger(WeChatError.__name__, 'error')
        self.log.error(info)
    
    def __str__(self):
        return repr(self.info)

class Wechat(object):
    '''
    中间操作方法(如获取access token)返回self以链式调用
    '''
    
    # TODO:get from memcache
    __ac_token = None
    
    def __init__(self, **option):
        '''
        初始化参数集option需包含微信token,appid,appsecret以获取access token
        '''
        self.log = get_logger(Wechat.__name__, 'debug')
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
        发送http请求,根据data是否为空发送GET or POST,返回一个由微信产生的json转换的dict
        '''
        if isinstance(data, basestring):
            data = json.dumps(data, ensure_ascii=False)
        resp = urllib2.urlopen(url, data)
        result = json.load(resp)
        self.log.info(url[:100] + '... response: ' + `result`)
        self._checkError(result)
        return result
        
    def refreshACtoken(self):
        '''
        cache和静态变量保存actoken,若超过存活期则从微信API重新获取
        '''
        timegoes = lambda a, b:a - b
        if timegoes(time(), cache.get('wc_ac_timestamp')) > conf.AC_TOKEN_EXPIRES_IN:
            url = conf.ACCESS_URL % (self.appid, self.appsecret)
            result = self.httpReq(url)
            Wechat.__ac_token = result['access_token']
            # save to memcache
            cache.set('wc_ac_token', Wechat.__ac_token)
            cache.set('wc_ac_timestamp', time())
            self.log.info('已刷新actoken: ' + str(Wechat.__ac_token))
        else:
            Wechat.__ac_token = cache.get('wc_ac_token')
        return self
    

    def sendMsg(self, openid, msg_instance):
        '''
        主动发送消息,需在用户发送过消息的48小时内
        msg_instance
            一个设置好回复内容的Message实例
        '''
        Msg = msg_instance.getReply()
        msgtype = Msg['MsgType']
        msg_to_send = {
                       "touser":openid,
                       "msgtype":msgtype.lower(),
                       }
        # 怪微信咯
        if msgtype == conf.TEXT:
            msg_to_send[msgtype.lower()] = {'content':Msg['Content']}
        elif msgtype == conf.NEWS:
            items = Msg['Articles']  # a list
            msg_to_send[msgtype.lower()] = {'articles':items}
        else:
            msg_to_send[msgtype.lower()] = Msg[msgtype][0]  # image,music,voice,video类型的消息
            
        data = json.dumps(msg_to_send, ensure_ascii=False)
#         return data
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
            data = json.dumps(menu, ensure_ascii=False)
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
            headimgurl     用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，
                            0代表640*640正方形头像），用户没有头像时该项为空
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
        if openid is None:
            url = conf.USER_GET_URL_FIRST % Wechat.__ac_token
        else:
            url = conf.USER_GET_URL % (Wechat.__ac_token, openid)
        
        return self.httpReq(url)
    
    #####分组管理#####
    
    def createGroup(self, name):
        '''
        一个公众账号，最多支持创建500个分组
        '''
        url = conf.GROUP_CREATE_URL % Wechat.__ac_token
        data = {'group':{'name':name}}
        return self.httpReq(url, data)
        
    def getGroup(self):
        url = conf.GROUP_GET_URL % Wechat.__ac_token
        return self.httpReq(url)
    
    def getGroupUser(self, openid):
        url = conf.GROUP_USER_GET_URL % Wechat.__ac_token
        data = {'openid':openid}
        return self.httpReq(url, data)
    
    def updateGroupName(self, id, newname):
        url = conf.GROUP_UPDATE_URL % Wechat.__ac_token
        data = {"group":{"id":id, "name":newname}}
        return self.httpReq(url, data)
    
    def moveGroupUser(self, openid, to_groupid):
        url = conf.GROUP_MEMBER_UPDATE_URL % Wechat.__ac_token
        data = {"openid":openid, "to_groupid":to_groupid}
        return self.httpReq(url, data)

    #####网页授权#####
    
    def getOauthRedirect(self, redirect_uri, userinfo=False, state=None):
        '''
        获取引导关注者授权的页面(即使在未关注的情况下，只要用户授权，也能获取其信息)
        userinfo -- 要获取详细用户信息则为True
        state -- 重定向后会带上state参数
        '''
        if userinfo:
            scope = 'snsapi_userinfo'
        else:
            scope = 'snsapi_base'  # 不弹出授权页面，直接跳转，只能获取用户openid
        arg = dict(appid=self.appid, uri=redirect_uri, state=state, scope=scope, code='code')
        return conf.OAUTH_AUTHORIZE_URL.format(**arg)  # url str
        
    def getOauthAccessToken(self, oauth_code):
        '''
        用户同意授权后,重定向会带着code参数,可通过code获取oauth_access_token与openid
        '''
        arg = dict(appid=self.appid, secret=self.appsecret, code=oauth_code, grant_type='authorization_code')
        url = conf.OAUTH_TOKEN_URL.format(**arg)
        return self.httpReq(url)
        
    def getOauthRefreshToken(self, token):
        '''
        当oauth_access_token超时后，可以使用refresh_token进行刷新;
        refresh_token拥有较长的有效期（7天、30天、60天、90天），当refresh_token失效的后，需要用户重新授权
        '''
        arg = dict(appid=self.appid, refresh_token=token, grant_type='refresh_token')
        url = conf.OAUTH_REFRESH_URL.format(**arg)
        return self.httpReq(url)
    
    def getOauthUserinfo(self, token, openid):
        '''
        如果网页授权作用域为snsapi_userinfo，则可通过oauth_access_token和openid拉取用户信息
        '''
        url = conf.OAUTH_USERINFO_URL.format(access_token=token, openid=openid, lang='zh_CN')
        return self.httpReq(url)
    
    
    #####带参数二维码#####
    def getQRTicket(self, id, forever=False, expire=1800):
        '''
        申请临时二维码或永久二维码的ticket
        id -- 场景值ID，临时二维码时为32位非0整型，永久二维码时最大值为100000（目前参数只支持1--100000）
        forever -- 申请永久二维码则为True
        expire -- 该二维码有效时间，以秒为单位。 最大不超过1800。
        return
            {"ticket":"_____","expire_seconds":_____}
        '''
        url = conf.QRCODE_CREATE_URL % Wechat.__ac_token
        data = {"action_info": {"scene": {"scene_id": id}}}
        if forever:
            data['action_name'] = 'QR_LIMIT_SCENE'
        else:
            data['action_name'] = 'QR_SCENE'
            data['expire_seconds'] = expire
        return self.httpReq(url, data)
    
    def getQRUrl(self, ticket):
        '''
        根据ticket获取二维码图片url
        '''
        return conf.QRCODE_IMG_URL % ticket  # url str
