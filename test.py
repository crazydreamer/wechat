#coding=utf-8
from libs.wechat import Wechat
import libs.message as message
from bottle import *
import json

main = Bottle()

@main.post('/')
def reply():
    user_msg=request.body.read()
    response.set_header('Content-Type', 'text/xml; charset=UTF-8')
    
    m=message.NewsMsg(user_msg)
    m.setReply(u'哦',u'纳尼','http://z.cn','http://z.cn').cleanReplyItems().setReply(u'哦',u'纳尼','http://z.cn','http://z.cn').setReply(u'哦',u'纳尼','http://z.cn','http://z.cn')
    
    return m.getReply(True)


if __name__=='__main__':
    debug(True)
    run(main,host='0.0.0.0', port=8888,reloader=True)
