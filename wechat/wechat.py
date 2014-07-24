# coding=utf-8
import os
reload(os.sys)
os.sys.setdefaultencoding('utf8')
from urllib2 import urlopen
import json
from hashlib import sha1
import config as conf
import common
from msgtype import TEXT, IMAGE, MUSIC, NEWS, VOICE, VIDEO
from time import time

cache = common.get_cache()  
get_logger = common.get_logger

def valid(token, signature, timestamp, nonce):
    '''
    验证消息真实性,每次开发者接收用户消息的时候，微信也都会带上前面三个参数
    '''
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return True
    else:
        return False


class WechatError(Exception):
    '''
    抛出异常并记录日志
    '''
    def __init__(self, info):
        self.info = info
        self.log = get_logger(WechatError.__name__, 'error')
        self.log.error(info)
    
    def __str__(self):
        return repr(self.info)

class Wechat(object):
    '''
    中间操作方法(如获取access token)返回self以链式调用
    '''
    
    __ac_token = None
    
    def __init__(self, appid, appsecret):
        '''
        初始化参数集option需包含微信token,appid,appsecret以获取access token
        '''
        if __debug__:
            self.log = get_logger(Wechat.__name__, 'debug')
        else:
            self.log = get_logger(Wechat.__name__, 'info')
        self._errcode = None
        self.appid = appid
        self.appsecret = appsecret
        # self.refreshACtoken()
        
    ######通用方法######
        
    def _checkError(self, result):
        '''
        检查微信响应的信息有无错误(微信总是响应"{"开头的json),无错则返回结果
        '''
        assert(result)
        if result.has_key('errcode') and result['errcode'] != 0:
            self._errcode = result['errcode']
            raise WechatError(result['errmsg'].encode('utf8') + '(%d)' % self._errcode)
        return result

    def _httpReq(self, url, data=None):
        '''
        发送http请求,根据data是否为空发送GET or POST,返回一个由微信产生的json转换的dict
        data -- 若非字符串则转化为json字符串
        '''
        if data is not None and not isinstance(data, basestring) :
            data = json.dumps(data, ensure_ascii=False).encode('utf8')
        resp = urlopen(str(url), data).read().decode('utf8')  # maybe url is unicode
        self.log.info('WeChat response: ' + resp + os.linesep + 'FROM: ' + url.split('?')[0])
        result = json.loads(resp)
        return self._checkError(result)
        
    def refreshACtoken(self, force=False):
        '''
        cache和静态变量保存actoken,若超过存活期则从微信API重新获取
        '''
        if force or cache.get('wc_ac_token') is None \
                or (time() - cache.get('wc_ac_timestamp')) > conf.AC_TOKEN_EXPIRES_IN:
            url = conf.ACCESS_URL % (self.appid, self.appsecret)
            result = self._httpReq(url)
            Wechat.__ac_token = result['access_token']
            # save to memcache
            cache.set('wc_ac_token', Wechat.__ac_token)
            cache.set('wc_ac_timestamp', time())
            self.log.debug('已刷新actoken: ' + str(Wechat.__ac_token))
        else:
            Wechat.__ac_token = cache.get('wc_ac_token')
        return self
    
    #######发送消息#######
    def sendMsg(self, openid, msg_instance):
        '''
        主动发送消息,需在用户发送过消息的48小时内
        msg_instance
            一个设置好回复内容的Message实例
        '''
        Msg = msg_instance.getReply(raw=True)
        msgtype = Msg['MsgType']
        msg_to_send = {
                       "touser":openid,
                       "msgtype":msgtype.lower(),
                       }
        # 怪微信咯
        if msgtype == TEXT:
            msg_to_send[msgtype.lower()] = {'content':Msg['Content']}
        elif msgtype == NEWS:
            items = Msg['Articles']  # a list
            msg_to_send[msgtype.lower()] = {'articles':items}
        else:
            msg_to_send[msgtype.lower()] = Msg[msgtype][0]  # image,music,voice,video类型的消息
            
        data = json.dumps(msg_to_send, ensure_ascii=False)
#         return data
        url = conf.CUSTOM_SEND_URL % Wechat.__ac_token
        self._httpReq(url, data)
        return self
        
    
    #######自定义菜单######
    def createMenu(self, *button):
        '''
        button -- a list of Button object
        '''
        menu={'button':button}
        url = conf.MENU_CREATE_URL % Wechat.__ac_token
        return self._httpReq(url, menu)
        
    def getMenu(self):
        '''
        获取已设置的menu,返回一个dict
        '''
        url = conf.MENU_GET_URL % Wechat.__ac_token
        return self._httpReq(url)['menu']['button']
    
    def deleteMenu(self):
        '''
        删除已设置的menu
        '''
        url = conf.MENU_DELETE_URL % Wechat.__ac_token
        return self._httpReq(url)
            
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
        return self._httpReq(url)
    
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
        
        return self._httpReq(url)
    
    #####分组管理#####
    
    def createGroup(self, name):
        '''
        一个公众账号，最多支持创建500个分组
        '''
        url = conf.GROUP_CREATE_URL % Wechat.__ac_token
        data = {'group':{'name':name}}
        return self._httpReq(url, data)
        
    def getGroup(self):
        url = conf.GROUP_GET_URL % Wechat.__ac_token
        return self._httpReq(url)
    
    def getGroupUser(self, openid):
        url = conf.GROUP_USER_GET_URL % Wechat.__ac_token
        data = {'openid':openid}
        return self._httpReq(url, data)
    
    def updateGroupName(self, id_, newname):
        url = conf.GROUP_UPDATE_URL % Wechat.__ac_token
        data = {"group":{"id":id_, "name":newname}}
        return self._httpReq(url, data)
    
    def moveGroupUser(self, openid, to_groupid):
        url = conf.GROUP_MEMBER_UPDATE_URL % Wechat.__ac_token
        data = {"openid":openid, "to_groupid":to_groupid}
        return self._httpReq(url, data)

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
        return self._httpReq(url)
        
    def getOauthRefreshToken(self, token):
        '''
        当oauth_access_token超时后，可以使用refresh_token进行刷新;
        refresh_token拥有较长的有效期（7天、30天、60天、90天），当refresh_token失效的后，需要用户重新授权
        '''
        arg = dict(appid=self.appid, refresh_token=token, grant_type='refresh_token')
        url = conf.OAUTH_REFRESH_URL.format(**arg)
        return self._httpReq(url)
    
    def getOauthUserinfo(self, token, openid):
        '''
        如果网页授权作用域为snsapi_userinfo，则可通过oauth_access_token和openid拉取用户信息
        '''
        url = conf.OAUTH_USERINFO_URL.format(access_token=token, openid=openid, lang='zh_CN')
        return self._httpReq(url)
    

    
    #####带参数二维码#####
    def getQRImage(self, id_, forever=False, expire=1800):
        '''
        根据ticket获取二维码图片url
        id_ -- 场景值ID，临时二维码时为32位非0整型，永久二维码时最大值为100000（目前参数只支持1--100000）
        forever -- 申请永久二维码则为True
        expire -- 该二维码有效时间，以秒为单位。 最大不超过1800。
        '''
        def getQRTicket():
            '''
            申请临时二维码或永久二维码的ticket
            return
                {"ticket":"_____","expire_seconds":_____}
            '''
            url = conf.QRCODE_CREATE_URL % Wechat.__ac_token
            data = {"action_info": {"scene": {"scene_id": id_}}}
            if forever:
                data['action_name'] = 'QR_LIMIT_SCENE'
            else:
                data['action_name'] = 'QR_SCENE'
                data['expire_seconds'] = expire
            return self._httpReq(url, data)
        url = conf.QRCODE_IMG_URL % getQRTicket()['ticket']
        return url
        
    #######多媒体上传/下载########
    def uploadMedia(self, type_, data):
        '''
        return
            type         媒体文件类型，分别有图片（image）、语音（voice）、视频（video）和缩略图（thumb)
            media_id     媒体文件上传后，获取时的唯一标识
            created_at     媒体文件上传时间戳
        '''
        url = conf.FILE_UPLOAD_URL % (Wechat.__ac_token, type_)
        return self._httpReq(url, data)
        
    def downloadMedia(self, media_id):
        '''
        通过media_id获取已上传的多媒体文件(不支持下载视频)
        正常情况直接返回HTTP头与实体
        '''
        url = conf.FILE_DOWNLOAD_URL % (Wechat.__ac_token, media_id)
        r = urlopen(url)
        if r.headers['Content-Type'] == 'image/jpeg':
            return r.read()
        else:
            result = json.load(r)
            return self._checkError(result)


class Button(dict):
    """
    创建自定义菜单时使用:createMenu(Button[,Button[,Button]])
    """

    def __init__(self, name, type_=None, value=None, **kwargs):
        super(Button, self).__init__(**kwargs)
        self['name'] = name
        if type_ and value:
            self.setEffect(type_, value)
        
    def setEffect(self, type_, value):
        '''
        value -- it is key or url
        e.g.
        {
           "type":"click",
           "name":"赞一下我们",
           "key":"V1001_GOOD"
        }
        '''
        if self.has_key('sub_button'):
            raise WechatError('sub_button only have name attribute')
        self['type'] = type_
        if 'click' == type_:
            self['key'] = value
        elif 'view' == type_:
            self['url'] = value

    def addSubButton(self, button):
        '''
        Param:
            button -- a Button instance
        Example:
            addSubButton(Button('xxx','view','http://z.cn'))
        '''
        if button is self :
            raise WechatError('sub_button not allow itself!')
        if self.has_key('type'):
            tmp = self['name']
            self.clear()
            self['name'] = tmp
        if self.get('sub_button') is None:
            self['sub_button'] = []
        self['sub_button'].append(button)


wc = Wechat('wx5818f8be30f01b6f','3cc07f434ec80b41be9559d4bcff9d31')
