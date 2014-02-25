##############
# msg type   #
##############
TEXT = 'text'
IMAGE = 'image'
LOCATION = 'location'
LINK = 'link'
EVENT = 'event'
MUSIC = 'music'
NEWS = 'news'
VOICE = 'voice'
VIDEO = 'video'

##############
# API URL    #
##############

API_URL_PREFIX = 'https://api.weixin.qq.com/cgi-bin'

ACCESS_URL = API_URL_PREFIX + '/token?grant_type=client_credential&appid=%s&secret=%s' 

MENU_CREATE_URL = API_URL_PREFIX + '/menu/create?access_token=%s'
MENU_GET_URL = API_URL_PREFIX + '/menu/get?access_token=%s'   
MENU_DELETE_URL = API_URL_PREFIX + '/menu/delete?access_token=%s' 
MEDIA_GET_URL = API_URL_PREFIX + '/media/get?access_token=%s' 

USER_GET_URL_FIRST = API_URL_PREFIX + '/user/get?access_token=%s'
USER_GET_URL = USER_GET_URL_FIRST + '&next_openid=%s'
USER_INFO_URL = API_URL_PREFIX + '/user/info?access_token=%s&openid=%s' 
  
GROUP_GET_URL = API_URL_PREFIX + '/groups/get?access_token=%s'  
GROUP_CREATE_URL = API_URL_PREFIX + '/groups/create?access_token=%s'
GROUP_USER_GET_URL = API_URL_PREFIX + '/groups/getid?access_token=%s'
GROUP_UPDATE_URL = API_URL_PREFIX + '/groups/update?access_token=%s'
GROUP_MEMBER_UPDATE_URL = API_URL_PREFIX + '/groups/members/update?access_token=%s' 

CUSTOM_SEND_URL = API_URL_PREFIX + '/message/custom/send?access_token=%s'   

OAUTH_AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={uri}&response_type={code}&scope={scope}&state={state}#wechat_redirect'   
OAUTH_TOKEN_PREFIX = 'https://api.weixin.qq.com/sns/oauth2'   
OAUTH_TOKEN_URL = OAUTH_TOKEN_PREFIX + '/access_token?appid={appid}&secret={secret}&code={code}&grant_type={grant_type}'
OAUTH_REFRESH_URL = OAUTH_TOKEN_PREFIX + '/refresh_token?appid={appid}&grant_type={grant_type}&refresh_token={refresh_token}'
OAUTH_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang={lang}'

QRCODE_CREATE_URL = API_URL_PREFIX + '/qrcode/create?access_token=%s'
QRCODE_IMG_URL = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s'  

AC_TOKEN_EXPIRES_IN = 7200
OAUTH_AC_TOKEN_EXPIRES_IN = 7200
