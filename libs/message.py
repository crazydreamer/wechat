# coding=utf-8
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from time import time

class Message(object):
    '''
    设置回复消息请用对应类型的子类,使用子类setReply方法设置消息的各项参数
    msg_body
        接收消息的实体
    '''
    
    def __init__(self, msg_body):
        self._receive = {}
        self._reply = {}
        self.items = []
        self.receiveMsg(msg_body)
    
    #########接收/回复消息#######
    def receiveMsg(self, msg_body):
        '''
        转化从HTTP接收而来的XML
        '''
        root = ET.fromstring(msg_body)
        # 微信发来的XML只有一层
        for child in root:
            self._receive[child.tag] = child.text
        return self
    
    def setReply(self, **arg):
        '''
        自定义添加回复消息的键值
        '''
        for k, v in arg.items():
            self._reply[k] = v
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
        assert(self._reply)
        self._reply.update({
                     'ToUserName':self._receive['FromUserName'],
                     'FromUserName':self._receive['ToUserName'],
                     'CreateTime':'%d' % time()
                     })
        if toxml:
            return self.reply2XML()
        else:
            return self._reply
        
    def reply2XML(self, root=None, body=None):
        '''
        dict => xml,键对应树名,值为str则为树值,非str则为子树
        怪微信咯,这坑爹的6种XML格式不统一
        '''
        if (body and root) is None:
            body = self._reply
            root = ET.Element('xml')
        for k in body:
            tmp = ET.SubElement(root, k)
            if isinstance(body[k], basestring):
                tmp.text = body[k]
            else:
                # now body[k] is a list who is carrying dict
                if tmp.tag == 'Articles':
                    item_tag = 'item'
                    for i in body[k]:
                        item = ET.SubElement(tmp, item_tag)
                        self.reply2XML(root=item, body=i)
                else:
                    # 非图文消息第2层只有一项
                    self.reply2XML(tmp, body[k][0])
        if root.tag == 'xml':
            return ET.tostring(root, encoding='utf-8')
        
class TextMsg(Message):

    def setReply(self, content):
        Message.setReply(self, MsgType='text', Content=content)
        return self
    
class ImageMsg(Message):
    def setReply(self, media_id):
        self.items.append({'MediaId':media_id})
        Message.setReply(self, MsgType='image', Image=self.items)
        return self

class VoiceMsg(Message):
    def setReply(self, media_id):
        self.items.append({'MediaId':media_id})
        Message.setReply(self, MsgType='voice', Voice=self.items)
        return self
    
class VideoMsg(Message):
    def setReply(self, media_id, title, description):
        self.items.append({'MediaId':media_id, 'Title':title, 'Description':description})
        Message.setReply(self, MsgType='video', Video=self.items)
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
            
        Message.setReply(self, MsgType='Music', Music=self.items)
        return self
        
class NewsMsg(Message):
    '''
    可链式调用addItem方法继续增加图文:news.setReply(...).addItem(...).addItem(...)
    '''
        
    def setReply(self, title, description, picurl, url):
        self.addItem(title, description, picurl, url)._reply['MsgType'] = 'news'
        return self
        
    def addItem(self, title, description, picurl, url):
        self.items.append({
                           'Title':title,
                           'Description':description,
                           'PicUrl':picurl,
                           'Url':url
                           })
        Message.setReply(self, Articles=self.items, ArticleCount=str(len(self.items)))
#         self._reply['Articles']=self.items
#         self._reply['ArticleCount']=str(len(self.items))
        return self
        
        
