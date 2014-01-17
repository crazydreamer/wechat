from libs.wechat import Wechat
import libs.message as message
from bottle import *

@post('/')
def reply():
    user_msg=request.body.read()
    m=message.NewsMsg(user_msg)
    m.setReply('dddd','aaaa','http','http2').addItem('dddd','aaaa','http','http2').addItem('dddd','aaaa','http','http2')
    t=message.MusicMsg(user_msg)
    t.setReply('title',None,None,None,None)
    print m.getReply()
    return t.getReply(True)


main = default_app()

if __name__=='__main__':
    debug(True)
    run(main,host='0.0.0.0', port=8888,reloader=True)
