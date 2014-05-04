#coding=utf-8
from wechat.wechat import Wechat
import wechat.message as message
from bottle import *
import json

main = Bottle()

@main.post('/')
def reply():
    user_msg=request.body.read()
    response.set_header('Content-Type', 'text/xml; charset=UTF-8')
    
    m=message.Message(user_msg)
    m.newsReply(u'哦',u'纳尼','http://z.cn','http://z.cn').newsReply(u'哦',u'纳尼','http://z.cn','http://z.cn').newsReply(u'哦',u'纳尼','http://z.cn','http://z.cn')
    
    return m.getReply()


if __name__=='__main__':
    debug(True)
    run(main,host='0.0.0.0', port=8888,reloader=True)
