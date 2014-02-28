# coding=utf-8
from msgtype import TEXT, IMAGE, MUSIC, NEWS, VOICE, VIDEO
from wechat import get_logger
from wechat import WechatError
import xml.etree.ElementTree as ET
from time import time

class Message(object):
    '''
    设置回复消息请用对应类型的子类
    @attention: 对于微信传来的XML,Event键值统一转为小写
    @see: http://mp.weixin.qq.com/wiki/index.php?title=%E6%8E%A5%E6%94%B6%E6%99%AE%E9%80%9A%E6%B6%88%E6%81%AF
    '''
    def __init__(self, msg=None, log=False):
        '''
        默认新建一个空实例,消息内容通常在子类的setReply方法中设置
        @param msg: 消息的XML实体,用于将其转换为可操作类型
        @param log: 是否将接收到的XML记录到日志        
        '''
        self._receive = {}
        self._reply = {}
        self._replyOK = False  # 回复内容完整flag
        self.items = []  # 通常为用户可见的消息实体
        if __debug__:
            self.log = get_logger(Message.__name__, 'debug')
        else:
            self.log = get_logger(Message.__name__, 'info')
        if msg is not None:
            self.receiveMsg(msg, log)
    
    #########接收/回复消息#######
    def receiveMsg(self, msg_body, log):
        '''
        转化从HTTP接收而来的XML
        @param msg: 消息的XML实体,用于将其转换为可操作类型
        @param log: 是否将接收到的XML记录到日志
        '''
        if log:
            self.log.info('receive: ' + msg_body)
        root = ET.fromstring(msg_body)
        # 微信发来的XML只有一层
        for child in root:
            self._receive[child.tag] = child.text
            
        if self._receive.has_key('Event'):
            self._receive['Event']=self._receive['Event'].lower()
        self.setReplyTo(self)
        return self
    
    def setReply(self, **arg):
        '''
        仅供具体类型的消息子类使用,设置回复内容
        '''
        if arg.get('MsgType') != TEXT:
            assert(self.items)
        for k, v in arg.items():
            self._reply[k] = v
        self._replyOK = True  # getReply() will check this flag
        return self
    
    def setReplyTo(self,msg):
        '''
        根据接收消息设置回复消息的fromusername/tousername
        若Message实例化时未传入XML实体,则需要手动调用此方法
        '''
        self._reply.update({'ToUserName':msg.fromusername,'FromUserName':msg.tousername})
        return self
    
    
    def updateReplyItems(self, **item):
        '''
        设置回复消息的items项,并去除其中的非必填项(值为None)
        '''
        for k, v in item.items():
            if v is None:
                del item[k]
        self.items.append(item)
        #return None
        
    
    def cleanReplyItems(self):
        '''
        清除已设置的回复消息items
        '''
        self._replyOK = False
        self.items = []
        return self
    
    def getRev(self, *arg):
        '''
        获取已接收的消息,返回一个dict;若参数含有消息键,则返回对应键值的list
        @return: 
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
            return self._receive[arg[0]]
        else:
            r = []
            for i in arg:
                r.append(self._receive[i])
            return r
            
    def getReply(self, toxml=False):
        '''
        获取要回复的消息,设置回复时间
        @param toxml:是否将回复内容以xml格式返回(str型),默认返回dict
        '''
        assert(self._replyOK)
        if self._reply.get('ToUserName') is None:
            raise WechatError('do not find which user to reply!')
        self._reply['CreateTime'] = '%d' % time()
        if toxml:
            return self.reply2XML()
        else:
            return self._reply
        
        
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
        return self._receive.get('MsgType')
    @property
    def fromusername(self):
        return self._receive.get('FromUserName')
    @property
    def tousername(self):
        return self._receive.get('ToUserName')
    @property
    def createtime(self):
        return self._receive.get('CreateTime')
        
class TextMsg(Message):

    def setReply(self, content):
        Message.setReply(self, MsgType=TEXT, Content=content)
        return self
    
class ImageMsg(Message):
    def setReply(self, media_id):
        self.items.append({'MediaId':media_id})
        Message.setReply(self, MsgType=IMAGE, Image=self.items)
        return self

class VoiceMsg(Message):
    def setReply(self, media_id):
        self.items.append({'MediaId':media_id})
        Message.setReply(self, MsgType=VOICE, Voice=self.items)
        return self
    
class VideoMsg(Message):
    def setReply(self, media_id, title, description):
        self.items.append({'MediaId':media_id, 'Title':title, 'Description':description})
        Message.setReply(self, MsgType=VIDEO, Video=self.items)
        return self
    
class MusicMsg(Message):
    def setReply(self, title, description, musicurl, hqmusicurl, thumbmediaid):
        self.updateReplyItems(
            Title=title,
            Description=description,  # can be None
            MusicUrl=musicurl,
            HQMusicUrl=hqmusicurl,  # can be None
            ThumbMediaId=thumbmediaid  # can be None
            )
        Message.setReply(self, MsgType=MUSIC, Music=self.items)
        return self
        
class NewsMsg(Message):
    '''
    可多次调用setReply方法继续增加图文:news.setReply(...).setReply(...).setReply(...)
    '''
        
    def setReply(self, title, description, picurl, url):
        '''
        4个参数均为非必须
        '''
        self.updateReplyItems(Title=title, Description=description, PicUrl=picurl, Url=url)
       
        if len(self.items) > 10:
            raise WechatError('news message limit 10 items')
        Message.setReply(self, MsgType=NEWS, Articles=self.items, ArticleCount=str(len(self.items)))
        return self
        
