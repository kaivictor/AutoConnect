#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   control.py
@Time    :   2023/05/18
@Author  :   kai
@Version :   0.2.1
@Contact :   https://github.com/kaivictor
@Desc    :   Help control computer
'''


import datetime
import time
import psutil
import requests
# import urllib.parse.urlparse
import pywifi
import ping3
# import socket  # 可用于检查连通性


class systemStatu:
    def __init__(self):
        self.runCount = 0
        # 用于保存调用的最开始时间，一般作开机时间，可更新
        self.startTime = datetime.datetime.now()
        self.runClockLast = self.startTime
        self.askClockLast = self.startTime

    def relaxTime(self, update=False) -> tuple[int, int]:  # 询问的时间间隔
        if (not self.runCount) or update:
            self.runCount += 1
        now = datetime.datetime.now()
        waitTime = int((now-self.runClockLast).seconds)
        starttime = int((now-self.startTime).seconds)
        askTime = int((now-self.askClockLast).seconds)
        self.askClockLast = datetime.datetime.now()
        if update:
            self.runClockLast = datetime.datetime.now()  # 保存近一次运行时刻
        return starttime, waitTime, askTime

    def internetTest(self, checkLogon=True):
        # 网络测试，返回网络状态与可用的网卡
        netReport = {
            'internets': False,
            'isLogin': False,
            'drivers': {'isDriver': 0}}
        # 检查网卡
        netDriveStatu = psutil.net_if_stats()
        if '以太网' in netDriveStatu.keys():  # 判断有线网卡是否存在
            netReport['drivers']['wired'] = 'notup'
            # print(netDriveStatu['以太网'])
            if netDriveStatu['以太网'].isup:  # 判断网线是否连接
                netReport['drivers']['wired'] = 'isup'
            netReport['drivers']['isDriver'] += 1
        if 'WLAN' in netDriveStatu.keys():  # 判断无线网卡是否存在
            netReport['drivers']['WLAN'] = 'notup'
            if netDriveStatu['WLAN'].isup:  # 判断无线是否连接
                netReport['drivers']['WLAN'] = 'isup'
            netReport['drivers']['isDriver'] += 1
        # 暂不支持其他网卡自动连接
        if netReport['drivers']['isDriver']:
            # 检查网络
            intnetStatu = False
            hostname = "www.baidu.com"
            response_time = ping3.ping(hostname)
            if response_time is not False:
                print("当前网络已连接")
                intnetStatu = True
            if response_time is None:
                print("www.baidu.com not achieve")
                # 需要进一步检测
                try:
                    requests.get("https://www.baidu.com", timeout=1)
                    intnetStatu = True
                except Exception:
                    intnetStatu = False
            # 检查外网连通性
            netReport['internets'] = intnetStatu
            # 检查登录
            if not checkLogon:
                netReport['isLogin'] = None
                return netReport
            proxies = {}  # 设置空字典来跳过 Clash 代理
            loginHost = "http://aaa.cqust.edu.cn/"
            try:
                loginStatu = requests.get(
                    loginHost, proxies=proxies, timeout=5)
            except Exception:
                netReport['isLogin'] = None  # 实际上不知道
            else:
                sucessUrl = "http://aaa.cqust.edu.cn/eportal/./success.jsp"
                locateUrl = "http://123.123.123.123/"
                # urllib.parse.urlparse(loginStatu.url)
                # 偷懒，根据跳转的页面判断登录与否以及是否在校内用网
                # 之后改为使用验证
                if loginStatu.status_code == 200:
                    if (sucessUrl in loginStatu.url):
                        netReport['isLogin'] = True
                    elif locateUrl in loginStatu.url:
                        netReport['isLogin'] = None
                    else:
                        netReport['isLogin'] = False
                else:
                    netReport['isLogin'] = None  # 异常被捕获了,504处理不了
        else:
            netReport['drivers']['isDriver'] = 'Not support'
        return netReport

    def connectWLAN(self, allowWLAN: list):
        # 用于扫描与连接wifi
        if 'WLAN' in self.internetTest()['drivers'].keys():
            # 确保无线网卡存在
            # 开启/关闭WiFi等用C语言写
            wifi = pywifi.PyWiFi()
            self.iface = wifi.interfaces()[0]
            self.iface.disconnect()
            self.iface.scan()
            time.sleep(2)
            try:
                return self.connect_WLAN(allowWLAN, self.iface.scan_results())
            except BaseException:
                # 说明wifi扫描功能未启用
                WLANReport = {
                    'driverStatu': False,  # 表示存在，但未启用
                    'scanfList': [],
                    'connectStatu': 'WLAN not open'}
                return WLANReport

    def connect_WLAN(self, allowWLAN, scanResult, interface=None) -> dict:
        # 连接设定Wifi
        # 处理返回的数据
        nearWLAN = []
        for profile in scanResult:
            nearWLAN.append(profile.ssid)
        WLANReport = {
            'driverStatu': True,
            'scanfList': nearWLAN,
            'connectStatu': ''}
        # 选择接口
        if interface is None:
            useInterface = self.iface
        else:
            useInterface = self.iface
        for wifiSet in allowWLAN:
            profiles = pywifi.Profile()  # 设置wifi连接文件
            profiles.auth = pywifi.const.AUTH_ALG_OPEN
            # tuple 元组  str
            if type(wifiSet) == tuple:  # 带有密码
                wifiSSID = wifiSet[0]
                if wifiSSID in nearWLAN:
                    profiles.ssid = wifiSet[0]
                    profiles.cipher = pywifi.const.CIPHER_TYPE_CCMP
                    profiles.key = wifiSet[1]
            else:
                wifiSSID = wifiSet
                if wifiSSID in nearWLAN:
                    profiles.ssid = wifiSet
                    profiles.akm.append(pywifi.const.AKM_TYPE_NONE)
                    profiles.cipher = pywifi.const.CIPHER_TYPE_NONE
            if wifiSSID in nearWLAN:
                print("try to connect :", wifiSSID)
                tep_profile = useInterface.add_network_profile(profiles)
                useInterface.connect(tep_profile)
                time.sleep(2)
                if useInterface.status() == pywifi.const.IFACE_CONNECTED:
                    print("Connected %s" % wifiSSID)
                    WLANReport['connectStatu'] = wifiSSID
                    return WLANReport
        return WLANReport


if __name__ == '__main__':
    sysStatu = systemStatu()
    # r1 = sysStatu.internetTest()
    # r2 = sysStatu.connectWLAN([('WeShare', 'password'), 'CQUST-M-4523',
    #                            'CQUST', 'CQUST-T', 'CQUST-2.4G',
    #                            'CQUST-5G'])
    # print(r1)
    # print("====================")
    # print(r2)
    print(sysStatu.startTime)
    time.sleep(5)
    print(sysStatu.startTime)
    print(sysStatu.relaxTime(sysStatu.startTime))
