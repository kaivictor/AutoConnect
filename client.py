#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   client.py
@Time    :   2023/05/18
@Author  :   kai
@Version :   0.2.1
@Contact :   https://github.com/kaivictor
@Desc    :   The shell of AutoConnect
'''

import os.path
import os
from tkinter.messagebox import askokcancel, showwarning
# import traceback
import sys


basicWord = """# Welcome to use my tool to help you set Internet
# Please enter your account >>> id
id: YourID

# Please enter your password >>> password
password: YourPassWord

# You can modify the preset SSID here, it is a list
# IF WLAN has Passward, you should write like:('SSID','password')
ssid: [CQUST-T, CQUST, CQUST-2.4G, CQUST-5G]

# isEncrypted Indicates whether your password is encrypted. \
Please enter an unencrypted password for the first time, \
and we will encrypt and save your password afterwards
isEncrypted: False

# When did you configure this document, like 2023-5-13
time: None
"""


def setBuglog():
    import logging
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)  # 获取应用程序exe的路径
    elif __file__:
        path = os.path.dirname(__file__)  # 获取脚本程序的路径
    else:
        path = '.\\'
    buglogPath = os.path.join(path, 'bug.log')
    logging.basicConfig(
        level=logging.ERROR,
        format=(
            'asctime:        %(asctime)s \n'  # 时间
            'filename_line:  %(filename)s_[line:%(lineno)d] \n'
            'level:          %(levelname)s \n'  # log级别
            'message:        %(message)s \n'),  # log信息
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename=buglogPath,
        # stream=sys.stdout,
        filemode='a')  # 如果模式为'a'，则为续写（不会抹掉之前的log）
    print("错误报告路径 ", buglogPath)
    logger = logging.getLogger(__name__)
    return logger


def main():
    bugloger = setBuglog()
    import main
    child = main.Program()
    while True:
        checkReport = child.check()
        if not checkReport[0]:
            if checkReport[1] == 'AppUserModelID set Error':
                showwarning("程序注册失败", "我们需要通过在“启动”中\
创建程序快捷方式来注册AppUserModelID,请以管理员模式重新运行")
            yamlFile = os.path.join(child.path, 'set.yaml')
            print(checkReport[1])
            if checkReport[1] == 'EncryptJs no found':
                showwarning("组件缺失", "程序无法运行,请更新程序")
                sys.exit(1)
            if checkReport[1] == 'Yaml no found':
                with open(yamlFile, 'w') as f:
                    f.write(basicWord)
            goon = askokcancel("设置", "配置文件有误,您可能是第一次使用本程序,请先进行配置")
            print(goon)
            if goon:
                os.system("notepad.exe {0}".format(yamlFile))
            else:
                return False
        else:
            break
    try:
        warn = child.main()
        print(warn)
        if warn:
            return False
    except Exception as e:
        print("更新错误日志")
        bugloger.error("%s" % (e))
        # traceback.print_exc(Exception)
        return False
    return True


if __name__ == '__main__':
    main()
