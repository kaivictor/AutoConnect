#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   logonServer.py
@Time    :   2023/05/18
@Author  :   kai
@Version :   0.2.1
@Contact :   https://github.com/kaivictor
@Desc    :   Function of Logon
'''


import requests
import urllib.parse as urlparse
import json
import re
from helpInfo import Report
import encrypt


class NetConnect():
    def __init__(self):
        self.rqSession = requests.session()
        self.rqSession.proxies = {}  # 不使用代理
        self.rqSession.trust_env = False  # 不使用代理
        self.rqSession.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
            "AppleWebKit/537.36 (KHTML, like Gecko)" +
            "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
        }
        self.cookieInfo = {
            'Host': "aaa.cqust.edu.cn",
            'Origin': "http://aaa.cqust.edu.cn"
        }
        self.Info = {}

    def logonServer(self, userId, password, encrtpted='false'):
        try:
            s = self.rqSession.get('http://aaa.cqust.edu.cn')
        except Exception:
            return Report(False, 'Missing component')
        if not (s.status_code == 200 and s.url == 'http://123.123.123.123/'):
            # 说明可能已经登录，也有可能没有接入校园网
            return Report(False, 'Error locating login server')
        relocationUrl = re.findall(
            r"<script>top.self.location.href='(.*)'</script>", s.text)
        if not relocationUrl:   # 说明访问的123.123不对,返回的结果不对
            return Report(False, 'Relay server error')
        query = urlparse.urlparse(relocationUrl[0]).query
        if not query:           # 说明访问的123.123返回的结果不对
            return Report(False, 'Relay server error')
        # 获取服务器类型,学校是这么定义的,固定为“互联网”,这边就不麻烦我了 #
        # 修改refer
        interFaceUrl = ('http://aaa.cqust.edu.cn/eportal/InterFace.do?' +
                        'method=getServices')
        # 如果想获取验证状态信息请启用这个
        # rqDate = {'queryString': query}
        # self.rqSession.post(interFaceUrl, data=rqDate)
        referUrl = (interFaceUrl + '&queryString=' + query)
        self.cookieInfo['Referer'] = referUrl
        # >>> 登录
        # self.rqSession.cookies.set('EPORTAL_COOKIE_SAVEPASSWORD', 'true')
        interFaceUrl = ('http://aaa.cqust.edu.cn/eportal/InterFace.do?' +
                        'method=login')
        rqDate = {
            'userId': userId,
            'password': password,
            'service': urlparse.quote('互联网'),
            'queryString': query,
            'operatorPwd': '',
            'operatorUserId': '',
            'validcode': '',
            'passwordEncrypt': encrtpted
        }
        loginPost = self.rqSession.post(url=interFaceUrl, data=rqDate)
        # print(loginPost.status_code, loginPost.content, loginPost.url)
        if loginPost.status_code != 200:
            return Report(False, 'Server does not work')
        result = json.loads(loginPost.content.decode('utf-8'))
        if result['result'] == "fail":
            return Report(False, result['message'])
        elif result['result'] == "success":
            userIndex = result['userIndex']
            return Report(True, {'userIndex': userIndex, 'query': query})
        return Report(False, 'UnkonwError')

    def accontInfo(self, userIndex, rebreak=False):  # 返回登录状态与用户信息
        serverTest = requests.get('http://aaa.cqust.edu.cn',
                                  proxies={}, timeout=5)
        if serverTest.status_code != 200:
            return Report(isTrue=False, msg='Net Error')
        sucessUrl = "http://aaa.cqust.edu.cn/eportal/./success.jsp"
        if sucessUrl not in serverTest.url:
            return Report(isTrue=False, msg='Host off-line')
        interFaceUrl = ("http://aaa.cqust.edu.cn/eportal/InterFace.do?" +
                        "method=getOnlineUserInfo")
        rqData = {'userIndex': userIndex}
        infoPost = self.rqSession.post(interFaceUrl, data=rqData)
        if infoPost.status_code != 200:
            return Report(isTrue=False, msg='Host Error')
        if not infoPost.content:
            return Report(isTrue=False, msg='Host Error')
        uer_Info = json.loads(infoPost.content.decode('utf-8'))
        if uer_Info['result'] == 'fail':
            return Report(isTrue=False, msg='Host Error')
        uerInfos = {'apMac': '', 'message': '', 'portalIp': '',
                    'realServiceName': '', 'redirectUrl': '', 'result': '',
                    'userGroup': '', 'userId': '', 'userIndex': '',
                    'userIp': '', 'userMac': '', 'userName': '',
                    'userPackage': '', 'welcomeTip': ''}
        # 信息过滤
        # print(uer_Info)
        for keyName in uerInfos.keys():
            uerInfos[keyName] = uer_Info[keyName]
        if uer_Info['result'] == 'wait' and not rebreak:
            uerInfos = self.accontInfo(userIndex, True).msg
        return Report(isTrue=True, msg=uerInfos)

    def EncryptPassword(self, passward, query):
        serverTest = requests.get('http://aaa.cqust.edu.cn',
                                  proxies={}, timeout=5)
        if serverTest.status_code != 200:
            return Report(False, 'Net is not up')
        sucessUrl = "http://aaa.cqust.edu.cn/eportal/./success.jsp"
        if sucessUrl not in serverTest.url:
            return {}
        interFaceUrl = ("http://aaa.cqust.edu.cn/eportal/InterFace.do?" +
                        "method=pageInfo")
        rqData = {'queryString': query}
        infoPost = self.rqSession.post(interFaceUrl, data=rqData)
        if infoPost.status_code != 200:
            return Report(False, 'Server is not work')
        if not infoPost.content:
            return Report(False, 'Server returned wrong value')
        page_Info = json.loads(infoPost.content.decode('utf-8'))
        pswKey = {'publicKeyExponent': '', 'publicKeyModulus': ''}
        for keyName in page_Info.keys():
            pswKey[keyName] = page_Info[keyName]
        # 模仿js进行密码加密
        encryptedPsw = encrypt.encrypt().encryptPsw(
            passward, pswKey['publicKeyExponent'], pswKey['publicKeyModulus'])
        return Report(True, encryptedPsw)


if __name__ == '__main__':
    test = NetConnect()
    test.logonServer('my id', 'error psw')
