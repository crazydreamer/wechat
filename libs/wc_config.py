API_URL_PREFIX = 'https://api.weixin.qq.com/cgi-bin'  

AUTH_URL = API_URL_PREFIX + '/token?grant_type=client_credential&appid=%s&secret=%s' 

MENU_CREATE_URL = API_URL_PREFIX + '/menu/create?access_token=%s'
MENU_GET_URL = API_URL_PREFIX +'/menu/get?access_token=%s'   
MENU_DELETE_URL = API_URL_PREFIX +'/menu/delete?access_token=%s' 
MEDIA_GET_URL = API_URL_PREFIX+'/media/get?access_token=%s' 

QRCODE_CREATE_URL = '/qrcode/create?'   
QR_SCENE = 0  
QR_LIMIT_SCENE = 1
QRCODE_IMG_URL = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket='  

USER_GET_URL_FIRST= API_URL_PREFIX +'/user/get?access_token=%s'
USER_GET_URL = USER_GET_URL_FIRST+'&next_openid=%s'
USER_INFO_URL = API_URL_PREFIX + '/user/info?access_token=%s&openid=%s' 
  
GROUP_GET_URL = API_URL_PREFIX +'/groups/get?'  
GROUP_CREATE_URL = API_URL_PREFIX +'/groups/create?'
GROUP_UPDATE_URL = API_URL_PREFIX +'/groups/update?'
GROUP_MEMBER_UPDATE_URL = API_URL_PREFIX +'/groups/members/update?' 

CUSTOM_SEND_URL = API_URL_PREFIX +'/message/custom/send?access_token=%s'   

OAUTH_PREFIX = 'https://open.weixin.qq.com/connect/oauth2'
OAUTH_AUTHORIZE_URL = '/authorize?'   
OAUTH_TOKEN_PREFIX = 'https://api.weixin.qq.com/sns/oauth2'   
OAUTH_TOKEN_URL = '/access_token?'
OAUTH_REFRESH_URL = '/refresh_token?' 
OAUTH_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo?'

AC_TOKEN_EXPIRES_IN = 7200
