# coding=utf-8
from msgtype import TEXT, IMAGE, MUSIC, NEWS, VOICE, VIDEO, EVENT
from wechat import get_logger
from wechat import WechatError
import xml.etree.ElementTree as ET
from time import time

class Message(object):
    '''
    接收请求时可用该类初始化,然后调用各类消息类型的reply方法响应.
    参考http://mp.weixin.qq.com/wiki/index.php?title=%E6%8E%A5%E6%94%B6%E6%99%AE%E9%80%9A%E6%B6%88%E6%81%AF
    '''
    def __init__(self, raw_msg=None, log=False):
        '''
        根据接收到的消息实体初始化会自动设置被动回复的to/from user.若主动发送客服消息则无需消息实体
        :param raw_msg: 消息的XML实体
        :param log: 是否将接收到的XML记录到日志
        '''
        self._receive = {}
        self._reply = {}
        self.items = []  # 通常为用户可见的消息实体
        if __debug__:
            self.log = get_logger(Message.__name__, 'debug')
        else:
            self.log = get_logger(Message.__name__, 'info')
        if raw_msg is not None:
            self.receiveMsg(raw_msg, log)

    #########接收/回复消息#######
    def receiveMsg(self, raw_msg, log):
        '''
        转化从HTTP接收而来的XML
        :param raw_msg: 消息的XML实体,用于将其转换为可操作类型
        :param log: 是否将接收到的XML记录到日志
        '''
        if log:
            self.log.info('receive: ' + raw_msg)
        root = ET.fromstring(raw_msg)
        # 微信发来的XML只有一层
        for child in root:
            self._receive[child.tag] = child.text
        return self

    def setReply(self, **arg):
        '''
        广泛地设置回复内容
        '''
        for k, v in arg.items():
            self._reply[k] = v
        return self


    def updateReplyItems(self, **item):
        '''
        设置回复消息的items项,并去除其中的非必填项(值为None)
        '''
        for k, v in item.items():
            if v is None:
                del item[k]
        self.items.append(item)
        return self

    def getRev(self, *arg):
        '''
        获取已接收的消息,返回一个dict;若参数含有消息键,则返回对应键值的list
        :return:
            ToUserName    开发者微信号
            FromUserName     发送方帐号（一个OpenID）
            CreateTime     消息创建时间 （整型）
            MsgType     消息类型
            ...        ...
            MsgId     消息id，64位整型
        '''
        assert(self._receive)
        arglen = len(arg)

        if arglen == 0:
            return self._receive
        elif arglen == 1 :
            return self._receive.get(arg[0])
        else:
            r = []
            for i in arg:
                r.append(self._receive.get(i))
            return r

    def getReply(self,raw=False):
        '''
        获取要回复的消息,设置回复时间
        :return: 返回XML格式的微信消息
        '''
        assert(self._reply)
        if raw:
            tmp = self._reply
        else:
            self._reply['ToUserName'],self._reply['FromUserName'] = self.getRev('FromUserName','ToUserName')
            self._reply['CreateTime'] = '%d' % time()
            tmp = self.reply2XML()
        self._reply.clear()
        return tmp


    def reply2XML(self, root=None, body=None):
        '''
        dict => xml,键对应树名,值为str则为树值,list则为子树
        怪微信咯,这坑爹的6种XML格式不统一
        '''
        if (body and root) is None:
            body = self._reply
            root = ET.Element('xml')
        for k in body:
            tmp = ET.SubElement(root, k)
            if isinstance(body[k], basestring):
                # 要用unicode赋值
                tmp.text = body[k]
            else:
                # now body[k] is a list who is carrying dict
                if tmp.tag == 'Articles':
                    item_tag = 'item'
                    for i in body[k]:
                        item = ET.SubElement(tmp, item_tag)
                        self.reply2XML(root=item, body=i)
                else:
                    # image,music,voice,video消息的list只有一项
                    self.reply2XML(tmp, body[k][0])
        if root.tag == 'xml':
            return ET.tostring(root, encoding='utf-8')


    ###########类属性#########
    @property
    def msgtype(self):
        '''
        为方便,将event消息的事件类型当作消息类型.
        参考http://mp.weixin.qq.com/wiki/index.php?title=%E6%8E%A5%E6%94%B6%E4%BA%8B%E4%BB%B6%E6%8E%A8%E9%80%81
        '''
        msgtype = self.getRev('MsgType')
        if EVENT == msgtype:
            return self.getRev('Event')
        else:
            return msgtype
    @property
    def fromusername(self):
        return self.getRev('FromUserName')
    @property
    def tousername(self):
        return self.getRev('ToUserName')
    @property
    def createtime(self):
        return self.getRev('CreateTime')

    ######回复各类型消息######

    def textReply(self, content):
        self.setReply(MsgType=TEXT, Content=content)
        return self

    def imageReply(self, media_id):
        self.items.append({'MediaId':media_id})
        self.setReply(MsgType=IMAGE, Image=self.items)
        return self

    def voiceReply(self, media_id):
        self.items.append({'MediaId':media_id})
        self.setReply(MsgType=VOICE, Voice=self.items)
        return self

    def videoReply(self, media_id, title, description):
        self.items.append({'MediaId':media_id, 'Title':title, 'Description':description})
        self.setReply(MsgType=VIDEO, Video=self.items)
        return self

    def musicReply(self, title, description, musicurl, hqmusicurl, thumbmediaid):
        self.updateReplyItems(
            Title=title,
            Description=description,  # can be None
            MusicUrl=musicurl,
            HQMusicUrl=hqmusicurl,  # can be None
            ThumbMediaId=thumbmediaid  # can be None
            )
        self.setReply(MsgType=MUSIC, Music=self.items)
        return self

    def newsReply(self, title, description, picurl, url):
        '''
        4个参数均为非必须;多条图文信息可重复调用此方法设置
        e.g. msg.newsReply(...).newsReply(...).newsReply(...).newsReply(...)
        '''
        self.updateReplyItems(Title=title, Description=description, PicUrl=picurl, Url=url)

        if len(self.items) > 10:
            raise WechatError('news message limit 10 items')
        self.setReply(MsgType=NEWS, Articles=self.items, ArticleCount=str(len(self.items)))
        return self
        
