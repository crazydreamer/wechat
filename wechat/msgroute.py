# coding=utf-8
from msgtype import *
from message import Message

class MsgRoute(object):
    '''
    处理http到来的post body,根据消息类型与消息关键字匹配响应函数
    路由动态保存在self.route里,例如:
        {
            'text':{'1':...,'2':...,'3':...,None:...},
            'image':{None:...},
            'click':{...},
            'subscribe':{None:...}
        }

    P.S. 未定义的消息类型为undefine,已定义消息类型未定义关键字为"msgtype:{None:callback}"
    '''
    def __init__(self):
        self.route = {'undefine':{
            None:lambda x:''
        }}
        self.keyword_tags={TEXT:'Content',event['click']:'EventKey',event['scan']:'EventKey'}
        self.msg=Message()


    def reply(self,msg,*args,**kw):
        '''
        根据接收的消息类型和触发关键字调用回调函数.英文统一转小写处理
        注意:对于扫二维码,未关注和已关注的EventKey值的格式不一样,未关注为"qrscene_<id>",已关注则为"<id>",请随时参考微信坑爹的官方文档
        :param msg: 原生XML消息或Message实例
        :param kw: 回复时用到的外部参数
        :return: 最终响应给微信的消息内容(xml格式),若路由里不存在已定义的类型则返回空串
        '''
        if type(msg) == Message:
            self.msg=msg
        else:
            self.msg=Message(msg,True)
        keyword_tag = self.keyword_tags.get(self.msg.msgtype)
        keyword = self.msg.getRev(keyword_tag)
        routetype = self.msg.msgtype
        try:
            callback = self.route[routetype].get(keyword.lower()) or self.route[routetype][None]
        except KeyError:
            return (self.route['undefine'][None])()
        else:
            return callback(*args,**kw)


    def match(self,msgtype,*keywords):
        '''
        消息触发匹配修饰器,用于被动回复的函数
        :param msgtype: 触发的消息类型
        :param keywords: 触发关键字(全等匹配,可多个),若不设置则为该类型的默认匹配
        :return: 原样返回callback
        '''
        def wrapper(callback):
            if self.route.get(msgtype) is None:
                self.route[msgtype]={}
            if keywords:
                for keyword in keywords:
                    self.route[msgtype][keyword] = callback
            else:
                self.route[msgtype][None] = callback
            return callback
        return wrapper

    #未定义的类型或未定义默认关键字都匹配此响应
    def undefine(self):return self.match('undefine')

    def text(self,*keywords):return self.match(TEXT,*keywords)
    def click(self,*keywords):return self.match(event['click'],*keywords)
    def location(self,*keywords):return self.match(LOCATION,*keywords)
    def subscribe(self,*keywords):return self.match(event['subscribe'],*keywords)
    def scan(self,*keywords):return self.match(event['scan'],*keywords)