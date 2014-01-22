#coding=utf-8
from libs.wechat import Wechat
import libs.message as message
from bottle import *
import json

main = Bottle()

@main.post('/')
def reply():
    user_msg=request.body.read()
    
    m=message.TextMsg(user_msg)
    m.setReply(u'哦')
    return m.getReply(True)


if __name__=='__main__':
    debug(True)
    run(main,host='0.0.0.0', port=8888,reloader=True)
