##############
# API URL    #
##############

API_URL_PREFIX = 'https://api.weixin.qq.com/cgi-bin'

ACCESS_URL = API_URL_PREFIX + '/token?grant_type=client_credential&appid=%s&secret=%s' 

MENU_CREATE_URL = API_URL_PREFIX + '/menu/create?access_token=<ac_token>'
MENU_GET_URL = API_URL_PREFIX + '/menu/get?access_token=<ac_token>'
MENU_DELETE_URL = API_URL_PREFIX + '/menu/delete?access_token=<ac_token>'
MEDIA_GET_URL = API_URL_PREFIX + '/media/get?access_token=<ac_token>'

USER_GET_URL = API_URL_PREFIX + '/user/get?access_token=<ac_token>'
USER_INFO_URL = API_URL_PREFIX + '/user/info?access_token=<ac_token>&openid=%s'
  
GROUP_GET_URL = API_URL_PREFIX + '/groups/get?access_token=<ac_token>'
GROUP_CREATE_URL = API_URL_PREFIX + '/groups/create?access_token=<ac_token>'
GROUP_USER_GET_URL = API_URL_PREFIX + '/groups/getid?access_token=<ac_token>'
GROUP_UPDATE_URL = API_URL_PREFIX + '/groups/update?access_token=<ac_token>'
GROUP_MEMBER_UPDATE_URL = API_URL_PREFIX + '/groups/members/update?access_token=<ac_token>'

CUSTOM_SEND_URL = API_URL_PREFIX + '/message/custom/send?access_token=<ac_token>'
TEMP_MSG_SEND_URL = API_URL_PREFIX + '/message/template/send?access_token=<ac_token>'

OAUTH_AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect'
OAUTH_TOKEN_PREFIX = 'https://api.weixin.qq.com/sns/oauth2'
OAUTH_TOKEN_URL = OAUTH_TOKEN_PREFIX + '/access_token?appid=%s&secret=%s&code=%s&grant_type=%s'
OAUTH_REFRESH_URL = OAUTH_TOKEN_PREFIX + '/refresh_token?appid=%s&grant_type=%s&refresh_token=%s'
OAUTH_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=%s'

QRCODE_CREATE_URL = API_URL_PREFIX + '/qrcode/create?access_token=<ac_token>'
QRCODE_IMG_URL = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s'  

FILE_UPLOAD_URL = 'http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=<ac_token>&type=%s'
FILE_DOWNLOAD_URL = 'http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=<ac_token>&media_id=%s'

AC_TOKEN_EXPIRES_IN = 7200
OAUTH_AC_TOKEN_EXPIRES_IN = 7200