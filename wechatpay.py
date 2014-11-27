# coding=utf-8
import random, string, os
from requests import post, get
from hashlib import md5
from time import time, strftime
from xmltodict import parse, unparse
from simplejson import dumps
from wechat import Wechat, WechatError
from config import DOWNLOAD_PATH, NOTIFY_URL, CERT_PATH, KEY_PATH

MYIP = get('http://api.ipify.org').text


class Parameters(object):
    def __init__(self, *args, **kwargs):
        self.name = []
        self.fixed_parameters = {}
        for i in args:
            self.name.append(i)
        for k, v in kwargs.items():
            self.fixed_parameters[k] = v

    def __call__(self, fn):
        def wrapped(real_self, *args, **kwargs):
            parameters = self.fixed_parameters.copy()
            if len(args) != 0 and len(kwargs) == 0:
                assert len(self.name) == len(args)
                parameters.update(zip(self.name, args))
            else:
                parameters.update(kwargs)
            return fn(real_self, parameters)

        return wrapped


class WechatPayError(WechatError): pass


class WechatPayBase(Wechat):
    api_host = 'https://api.mch.weixin.qq.com'

    def __init__(self, appid, appsecret, mch_id, payKey):
        super(WechatPayBase, self).__init__(appid, appsecret)
        self.mch_id = mch_id
        self.payKey = payKey

    def _sign(self, parameters):
        keys = sorted(parameters.keys())
        _ = [u'{}={}'.format(k, parameters[k]) for k in keys if parameters[k]]
        _.append(u'key={}'.format(self.payKey))
        sighstr = '&'.join(_).encode('utf8')
        return md5(sighstr).hexdigest().upper()


    def _createXML(self, parameters):
        parameters.update(dict(
            appid=self.appid,
            mch_id=self.mch_id,
            nonce_str=''.join(random.choice(string.letters) for i in range(10)),
        ))
        parameters['sign'] = self._sign(parameters)
        return unparse({'xml': parameters}, full_document=False).encode('utf8')

    def _check_error(self, xml_result, path=None):
        self.log.debug('response: ' + os.linesep + xml_result + os.linesep + 'FROM: ' + path)
        try:
            result = parse(xml_result)['xml']
        except Exception:
            t = strftime('%y%m%d%H%M%S')
            file_name = os.path.join(DOWNLOAD_PATH, '{}.xml'.format(t))
            with open(file_name, 'w') as f:
                f.write(xml_result)
        else:
            if result['return_code'] != 'SUCCESS':
                raise WechatPayError(result['return_msg'].encode('utf8'))
            elif result['result_code'] != 'SUCCESS':
                msg = 'result fail: {} - {}'.format(result['err_code_des'].encode('utf8'), result['err_code'])
                raise WechatPayError(msg, result['err_code'])
            else:
                sign = result.pop('sign')
                if sign != self._sign(result): raise WechatPayError('invalid sign', 'INVALID SIGN')
            return result


    def _post(self, path, parameters, cert=False):
        url = WechatPayBase.api_host + path
        parameters = self._createXML(parameters)
        cert = (CERT_PATH, KEY_PATH) if cert else ()
        result = post(url, parameters, cert=cert)
        return self._check_error(result.text, path)


class WechatPay(WechatPayBase):
    @Parameters('body', 'out_trade_no', 'total_fee', 'trade_type', 'openid', 'product_id',
                spbill_create_ip=MYIP, notify_url=NOTIFY_URL)
    def common_pay(self, parameters, *arg, **kwargs):
        return self._post('/pay/unifiedorder', parameters)

    def jsapi_parameters(self, prepay_id):
        parameters = dict(
            appId=self.appid,
            timeStamp=str(int(time())),
            nonceStr=''.join(random.choice(string.letters) for i in range(10)),
            package='prepay_id={}'.format(prepay_id),
            signType='MD5',
        )
        parameters['paySign'] = self._sign(parameters)
        return dumps(parameters)

    def check_notify(self, xml_notify, callback):
        content = self._check_error(xml_notify, 'request of Wechat pay notify')
        result, fail_msg = callback(**content)
        if result:
            return unparse({'return_code': 'SUCCESS'})
        else:
            return unparse({'return_code': 'FAIL', 'return_msg': ''})

    @Parameters('out_trade_no')
    def order_query(self, param):
        return self._post('/pay/orderquery', param)

    @Parameters('out_trade_no')
    def order_close(self, param):
        return self._post('/pay/closeorder', param)

    @Parameters('out_trade_no', 'out_refund_no', 'total_fee', 'refund_fee', op_user_id='')
    def refund_require(self, param):
        if not param['op_user_id']:
            param['op_user_id'] = self.mch_id
        return self._post('/secapi/pay/refund', param, True)

    @Parameters('out_refund_no', 'out_trade_no')
    def refund_query(self, param):
        return self._post('/pay/refundquery', param)

    @Parameters('bill_date', 'bill_type')
    def downloadBill(self, param):
        self._post('/pay/downloadbill', param)
