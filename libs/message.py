# coding=utf-8
from config import TEXT, IMAGE, LOCATION, LINK, EVENT, MUSIC, NEWS, VOICE, VIDEO
from common import get_logger
import xml.etree.ElementTree as ET
from time import time

class Message(object):
    '''
    设置回复消息请用对应类型的子类,使用子类setReply方法设置消息的各项参数
    msg_body
        接收消息的实体
    '''
    def __init__(self, msg_body=None):
        self._receive = {}
        self._reply = {}
        self._replyOK = False  # 回复内容完整flag
        self.items = []
        self.log = get_logger(Message.__name__, 'info')
        if msg_body is not None:
            self.receiveMsg(msg_body)
    
    #########接收/回复消息#######
    def receiveMsg(self, msg_body):
        '''
        转化从HTTP接收而来的XML
        '''
        self.log.info('receive: ' + msg_body)
        root = ET.fromstring(msg_body)
        # 微信发来的XML只有一层
        for child in root:
            self._receive[child.tag] = child.text
        self._reply.update({'ToUserName':self._receive['FromUserName'],
                            'FromUserName':self._receive['ToUserName']})
        return self
    
    def setReply(self, **arg):
        '''
        仅供具体类型的消息子类使用,设置回复内容
        '''
        for k, v in arg.items():
            self._reply[k] = v
        self._replyOK = True  # getReply() will check this flag
        return self
    
    def cleanReplyItems(self):
        self._replyOK = False
        self.items=[]
        return self
    
    def getRev(self):
        '''
        获取已接收的消息,返回一个dict
        return 
            ToUserName    开发者微信号
            FromUserName     发送方帐号（一个OpenID）
            CreateTime     消息创建时间 （整型）
            MsgType     消息类型
            ...        ...
            MsgId     消息id，64位整型
        '''
        assert(self._receive)
        return self._receive
            
    def getReply(self, toxml=False):
        '''
        获取要发送的消息,自动设置回复时的接收人+发送人+回复时间,返回一个dict或xml的str
        '''
        assert(self._replyOK)
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
        return self._receive['MsgType']
    @property
    def fromusername(self):
        return self._receive['FromUserName']
    @property
    def tousername(self):
        return self._receive['ToUserName']
    @property
    def createtime(self):
        return self._receive['CreateTime']
        
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
        tmp = {
                'Title':title,
                'Description':description,
                'MusicUrl':musicurl,
                'HQMusicUrl':hqmusicurl,
                'ThumbMediaId':thumbmediaid
               }
        for k, v in tmp.items():
            if v is None:
                del tmp[k]
        self.items.append(tmp)
            
        Message.setReply(self, MsgType=MUSIC, Music=self.items)
        return self
        
class NewsMsg(Message):
    '''
    可多次调用setReply方法继续增加图文:news.setReply(...).setReply(...).setReply(...)
    '''
    def setReply(self, title, description, picurl, url):
        self.items.append({
                           'Title':title,
                           'Description':description,
                           'PicUrl':picurl,
                           'Url':url
                           })
        if len(self.items) > 10:
            raise Exception('limit 10 items')
        Message.setReply(self, MsgType=NEWS, Articles=self.items, ArticleCount=str(len(self.items)))
        return self
        
