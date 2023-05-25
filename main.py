#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023/05/18
@Author  :   kai
@Version :   0.2.1
@Contact :   https://github.com/kaivictor
@Desc    :   The main program of AutoConnect
'''

import control
import logonServer
import deskToast
from helpInfo import Report
import sys
import os.path
import yaml
import time
import datetime
import win32com.client
import getpass


class Program():
    def __init__(self):
        self.isYaml = False
        self.isChecked = False
        self.current_user = getpass.getuser()
        self.check(self)  # 自检

    def check(self, uer=None):
        # 检查环境
        if getattr(sys, 'frozen', False):
            self.path = os.path.dirname(sys.executable)  # 获取应用程序exe的路径
            self.name = sys.argv[0]
        elif __file__:
            self.path = os.path.dirname(__file__)  # 获取脚本程序的路径
            self.name = os.path.basename(__file__)
        else:
            self.path = '.\\'
            self.name = 'AutoConnect.exe'
        if uer is not None:
            return
        self.isChecked = True
        # 检查配置文件
        self.congifFile = os.path.join(self.path, 'set.yaml')
        if not os.path.exists(self.congifFile):
            return (False, 'Yaml no found')
        else:
            self.isYaml = True
        if not self.loadConfig().isTrue:
            return (False, 'Yaml is Wrong')
        deskLinkPath = (f"C:\\Users\\{self.current_user}\\Desktop\\\
AutoConnect.lnk")
        startLinkPath = (f"C:\\Users\\{self.current_user}\\AppData\\\
Roaming\\Microsoft\\Windows\\Start Menu\\\
Programs\\AutoConnect.lnk")
        if not os.path.exists(startLinkPath):
            setshortcut = self.setshortcut(deskLinkPath, startLinkPath)
            if not setshortcut:
                return (False, 'AppUserModelID set Error')
        return (True, '')

    def loadConfig(self):
        self.needKey = ['id', 'password', 'ssid', 'isEncrypted', 'time']
        if not self.isYaml:
            return Report(False, 'no config')
        with open(self.congifFile, 'r') as f:
            config = yaml.safe_load(f.read())
            # print(type(config), config)
        for keyName in self.needKey:
            if keyName == 'ssid' and 'ssid' not in config.keys():
                return Report(False, 'Missing Key')  # wifi可以不用
            elif keyName not in config.keys() or config[keyName] is None:
                return Report(False, 'Missing Key')
        if config['time'] is None:
            return Report(False, 'Config is not set')
        # print(config)
        return Report(True, config)

    def writeConfig(self, key, value):
        loadconfig = self.loadConfig()
        if not loadconfig:
            return loadconfig
        if key not in loadconfig.msg.keys():
            return 'Missing Key'
        loadconfig.msg[key] = value
        file = open(self.congifFile, 'w', encoding='utf-8')
        yaml.dump(loadconfig.msg, file)
        file.close()
        return True

    def writeLog(self, *args):
        if not self.systemInfo.runCount:
            # 日志文件处理
            self.logfile = os.path.join(self.path, 'schoolInt.log')
            if (os.path.exists(os.path.join(self.path, 'tmp.log'))):
                # 删除旧日志
                os.remove(os.path.join(self.path, 'tmp.log'))
            if (os.path.exists(self.logfile)):
                # 备份上次日志
                os.rename(os.path.join(self.path, 'schoolInt.log'),
                          os.path.join(self.path, 'tmp.log'))
            print("日志保存路径 ", self.logfile)
        startTime = datetime.datetime.now()
        recordTime = startTime.strftime("%Y-%m-%d_%H:%M:%S")
        logText = str(recordTime + " " + " ".join(args) + "\n")
        if "程序启动" in logText:
            logText = "\n" + logText
        print(logText)
        with open(self.logfile, mode='a', encoding='utf-8') as f:
            f.write(logText)

    def setshortcut(self, deskLinkPath, startLinkPath):
        # 使用os模块获得计算机名
        # computer_name = os.environ['COMPUTERNAME']
        # 使用getpass模块获得当前用户名
        # 注册AppUserModelID
        try:
            for path in [deskLinkPath, startLinkPath]:
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(path)
                shortcut.TargetPath = os.path.join(self.path, self.name)
                shortcut.Arguments = ""
                shortcut.IconLocation = os.path.join(self.path, 'icon.ico')
                shortcut.Save()
        except Exception as e:
            print(f"注册AppUserModelID时出错: {e}")
            return False
        else:
            print("已成功注册AppUserModelID")
            return True

    def checkInternet(self, config, popToast):
        print("网络检查被启动")
        netReport = self.systemInfo.internetTest()
        if netReport['internets']:
            print("网络状态良好")
            return Report(isTrue=True, msg="Is online")
        elif netReport is False:
            print("检测功能失效")
            return Report(isTrue=False, msg="Test Host Error")
        elif netReport['isLogin'] is True:  # 说明学校网络断开
            print("校园网异常")
            return Report(isTrue=False, msg="School net Error")
        elif netReport['isLogin'] is not None:  # 说明不在学校里
            print("非校园网络")
            return Report(isTrue=False, msg="Not school")
        popToast(title='校园网自连', body='我们正在帮你连接网络', head='正在检查网络',
                 left='正在检查网络', progress=0.2, right="检查即将结束", update=True)
        print("网络断开")
        if not netReport['drivers']['isDriver']:  # 说明无适配器
            self.writeLog("设备不存在可用网卡")
            return Report(isTrue=False, msg="not driver")
        popToast(left='正在检查WIRE', progress=0.4, right="检查即将结束", update=True)
        if 'wired' in netReport['drivers'].keys():  # 存在有线网卡
            print("检查有线网络适配器")
            if netReport['drivers']['wired'] == 'isup':  # 网线插着
                driver = 'WIRE'
            else:
                driver = False
        if 'WLAN' in netReport['drivers'].keys() and not driver:  # 存在无线网卡
            print("检查无线网络适配器")
            popToast(left='正在检查WLAN', progress=0.4, update=True)
            if netReport['drivers']['WLAN'] == 'isup':
                # 无线已连接,但是未登录
                driver = 'WLAN'
            else:
                # 无线未连接
                if config['ssid'] is None:
                    print("用户禁用了该功能")
                    return Report(False, "WLAN disallowed")
                wlanRport = self.systemInfo.connectWLAN(config['ssid'])
                if not wlanRport['driverStatu']:
                    self.writeLog("无线网络功能未打开")
                    return Report(False, "WLAN not open")
                # 无线网卡已打开
                if not wlanRport['connectStatu']:
                    self.writeLog("没有找到可用的WLAN")
                    return Report(False, "WLAN no found")
                driver = wlanRport['connectStatu']
                self.writeLog(f"无线已连接-{driver}")
                popToast(head="已连接{0}".format(driver), update=True)
        elif 'WLAN' not in netReport['drivers'].keys():  # 没有无线网卡
            print("无线适配器未找到")
            return Report(False, "No driver")
        # 再次检查网络
        time.sleep(0.5)
        print("网络连接结果测试")
        netReport = self.systemInfo.internetTest()
        if netReport['internets']:
            # 网络正常则不运行(已经登录或者不需要登录)
            self.deskToast.Basic(title='你已接入网络')
            print("网络状态良好")
            return Report(isTrue=True, msg="Is online")
        return Report(isTrue=True, msg=driver)

    def autoLogon(self, config: dict, popToast, driver):
        # 登录
        self.writeLog("登录函数被调用")
        popToast(left='正在登录', progress=0.6, right="请稍后", update=True)
        for i in range(0, 2):
            time.sleep(1)  # 需要缓冲一下
            logon = self.loginFunc.logonServer
            if config['isEncrypted']:
                print("正在使用加密密码登录")
                logReport = logon(config['id'], config['password'], 'true')
            else:
                print("正在使用原始密码登录")
                logReport = logon(config['id'], config['password'])
            if logReport.isTrue:
                self.writeLog(f"{config['id']} 登录成功")
                break
        if not logReport.isTrue:  # 出错啦
            self.deskToast.ActionBasic(str(logReport.msg))
            return Report(isTrue=False, msg=logReport.msg)
        if not config['isEncrypted']:
            self.writeLog("正在对密码加密")
            encrypt = self.loginFunc.EncryptPassword
            encryptReport = encrypt(config['password'], logReport.msg['query'])
            if encryptReport.isTrue:
                eqPSW = encryptReport.msg
                self.writeConfig('password', eqPSW)
                self.writeConfig('isEncrypted', True)
                self.writeLog("密码加密完成")
            else:
                self.writeLog(f"密码加密失败: {encryptReport.msg}")
        uerInfo = self.loginFunc.accontInfo(logReport.msg['userIndex'])
        if uerInfo.isTrue:
            successInfo = ("{0},{1}. 你已经连接网络".format(
                uerInfo.msg['welcomeTip'], uerInfo.msg['userName']))
            successTip = (f"使用{driver}通过{uerInfo.msg['userIp']}接入互联网")
            self.deskToast.Basic(title=successInfo, body=successTip)
            return Report(isTrue=True, msg='Login succeeded')
        return Report(isTrue=False, msg=uerInfo.msg)

    def program(self, checkInternet=True):
        popToast = self.deskToast.Process
        # 读取配置
        config = self.loadConfig()
        if not config.isTrue:
            self.writeLog("加载配置文件错误")
            return Report(False, 'config Error')
        # 登录
        if not checkInternet:
            print("即将尝试开机后的第一次登录")
            logon = self.autoLogon(config.value, popToast, "默认设备")
            if logon.isTrue is True:
                return logon
            print("第一次登录失败,系统检查后重试")
        # 检查连接
        physicalNetwork = self.checkInternet(config.value, popToast)
        if physicalNetwork.isTrue and physicalNetwork.msg == 'Is online':
            return Report(True, physicalNetwork.msg)
        elif physicalNetwork.isTrue:
            driver = physicalNetwork.msg
            logon = self.autoLogon(config.value, popToast, driver)
            return logon
        return Report(False, physicalNetwork.msg)

    def main(self, arguement=None):
        # raise SystemError('test')
        # 开机运行
        self.systemInfo = control.systemStatu()
        if not self.isChecked:  # 没有自检
            self.writeLog("程序(配置)存在错误,无法运行")
            return False
        self.writeLog("程序启动")
        toastSet = {'title': '校园网自连', 'body': '我们正在帮你连接网络',
                             'head': '准备中', 'left': '请稍后',
                             'progress': None, 'right': '即将检查网络'}
        self.package = os.path.join(self.path, self.name)
        self.writeLog(self.package)
        self.deskToast = deskToast.Popup(toastSet, self.main, self.package)
        self.loginFunc = logonServer.NetConnect()
        runtimes = 1  # 测试用
        while True:
            # 等待 3秒 重新执行
            # 值小可以实现休眠后连接，值大实现实时检测
            time.sleep(3)
            # if (arguement)  对参数进行处理,暂时用不到
            runTime = self.systemInfo.relaxTime()
            # 过滤以实时检测
            # if self.systemInfo.runCount > 1 and arguement is None:  # 第一次后
            #    if runTime[2] < 7:     # 说明期间没有休眠等情况
            #        continue
            if runTime[0] < 3:
                continue                # 等待时间不足
            if self.systemInfo.runCount == 1:
                step = self.program(False)
            else:
                step = self.program()
            print(self.systemInfo.runCount, step.isTrue, step.msg)
            print("runtimes %d" % runtimes)
            runtimes += 1
            # 为1,即第一次运行才会处理,只考虑一次,如果是用户自行断网,日志也不考虑
            if self.systemInfo.runCount > 1:
                continue
            self.systemInfo.relaxTime(True)                # 运行后更新时间
            if step.isTrue is True and step.msg == 'Login succeeded':
                self.writeLog("登录成功")
                if arguement is not None:
                    break  # 重试只运行一次
                continue
            if step.isTrue is True and step.msg == 'Is online':
                self.writeLog("网络连接成功")
                self.deskToast.Basic(title='你已连接网络', body='请合理使用')
                if arguement is not None:
                    break  # 重试只运行一次
                continue
            print(step.msg)
            if step.msg == 'WLAN not open':
                self.writeLog("网线未连接,WLAN未启用")
                self.deskToast.ActionBasic(
                        title='请检查你的设备',
                        body=('抱歉,在您的设备上我们没有找到合适的网络接口' +
                              ',请试着为您的电脑插上网线或者打开WLAN'))
            elif step.msg == 'No driver':
                self.writeLog("没有可用的网络适配器")
                self.deskToast.ActionBasic(
                        title='请检查你的设备',
                        body=('抱歉,在您的设备上我们没有找到合适网络适配器'))
            elif step.msg == 'Missing component':
                self.writeLog("无法连接到登录服务器")
                self.deskToast.Basic(title='无法连接登录服务器,将稍后再试',
                                     body='有可能是您使用的网络非校园网或' +
                                     '者是您的计算机还没准备好')
            elif step.msg == 'config Error':
                self.writeLog("配置文件存在错误")
                self.deskToast.Basic(title='配置文件存在错误',
                                     body='请你检查配置文件')
            elif "密码" in step.msg:
                self.writeLog("登录被拒绝,原因:密码错误")
                self.deskToast.Basic(title='密码错误',
                                     body='请你在配置文件中输入正确的密码,' +
                                     '并设置isEncrypted为False')
                yamlFile = os.path.join(self.path, 'set.yaml')
                os.system("notepad.exe {0}".format(yamlFile))
            elif "验证" in step.msg:
                self.writeLog("登录被拒绝,原因:需要验证码")
                self.deskToast.Basic(title='登录错误',
                                     body='服务器要求验证码,将自动打开浏览器')
                chromeCmd = ('''"C:\\Program Files\\Google\\Chrome\\App''' +
                             '''lication\\chrome.exe" http://aaa.cqust.''' +
                             '''edu.cn''')
                openChrome = os.system(chromeCmd)
                if not openChrome:
                    msEdgeCmd = ('''"C:\\Program Files (x86)\\Microsof''' +
                                 '''t\\Edge\\Application\\msedge.exe" ''' +
                                 '''http://aaa.cqust.edu.cn''')
                    openChrome = os.system(msEdgeCmd)
                if not openChrome:
                    self.deskToast.Basic(
                        title='哎呀,很抱歉',
                        body='我没能打开您设备上的浏览器,劳驾您自行打开了')
                    time.sleep(10)
            elif step.msg == 'WLAN no found':
                self.writeLog("通过WLAN没有找到可用的WLAN")
                self.deskToast.ActionBasic(
                    title='无法连接',
                    body='在您的周围不存在您设置的WLAN,您可以手动连接或者修改配置文件')
            else:
                self.writeLog(step.msg)
                self.deskToast.Basic(
                    title='不常见的错误', body=f'我们还是为您提供错误原因:{step.msg},' +
                    '我们将会稍后再做尝试.特殊原因下,请您及时结束本程序')


if __name__ == '__main__':
    test = Program()
    test.check()
    test.main()
    # print(test.loadConfig())
