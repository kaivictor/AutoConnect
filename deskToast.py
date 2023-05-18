#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   deskToast.py
@Time    :   2023/05/18
@Author  :   kai
@Version :   0.2.1
@Contact :   https://github.com/kaivictor
@Desc    :   The windows toast
'''


import time
from windows_toasts import InteractableWindowsToaster, ToastProgressBar
from windows_toasts import ToastText1, ToastButton, ToastActivatedEventArgs
# https://windows-toasts.readthedocs.io/en/latest/index.html


class Popup:
    def __init__(self,
                 toastSet={
                     'title': 'Unfind', 'body': 'loading...',
                     'head': 'Unfind', 'left': 'Unfind',
                     'progress': None, 'right': 'Unfind'},
                 callbackFunc=None, notifierAUMID=None):
        self.times = 0
        self.toastSet = toastSet
        self.toaster = InteractableWindowsToaster(
            self.toastSet['body'], notifierAUMID)
        self.newToast = ToastText1()  # 进度条模式
        self.newToast.SetBody(self.toastSet['title'])
        self.progressBar = ToastProgressBar(
            self.toastSet['head'], self.toastSet['left'],
            progress=self.toastSet['progress'],
            progress_override=self.toastSet['right'])
        self.newToast.SetProgressBar(self.progressBar)
        self.basicNewToast = ToastText1()  # 基础模式
        self.callbackFunc = callbackFunc
        if callbackFunc is None:
            self.callbackFunc = self.setCallback

    def Process(self, title='', body='',
                head='', left='', progress=None, right='',
                update=False):
        if not update:  # 用于确认用户是否正确调用函数
            return ValueError
        arguments = [(title, 'title'), (body, 'body'),
                     (head, 'head'),
                     (left, 'left'),
                     (progress, 'progress'),
                     (right, 'right')]
        for argument in arguments:  # 更新数据
            if argument[0]:
                self.toastSet[argument[1]] = argument[0]
        if self.times == 0:
            self.times += 1
            self.toaster.show_toast(self.newToast)
            return
        self.toastReset(self.newToast)
        self.toaster.update_toast(self.newToast)

    def Basic(self, title='', body='', head=''):
        arguments = [(title, 'title'), (body, 'body'),
                     (head, 'head')]
        for argument in arguments:  # 更新数据
            if argument[0]:
                self.toastSet[argument[1]] = argument[0]
        self.basicNewToast = ToastText1()
        self.toastReset(self.basicNewToast)
        # self.basicNewToast.SetExpirationTime = 10
        self.toaster.clear_toasts()
        self.toaster.show_toast(self.basicNewToast)

    def ActionBasic(self, title='', body='', head=''):
        arguments = [(title, 'title'), (body, 'body'),
                     (head, 'head')]
        for argument in arguments:  # 更新数据
            if argument[0]:
                self.toastSet[argument[1]] = argument[0]
        self.basicNewToast = ToastText1()
        self.toastReset(self.basicNewToast)
        self.basicNewToast.AddAction(ToastButton('Again', 'info=again'))
        self.basicNewToast.on_activated = self.callbackFunc
        self.basicNewToast.SetExpirationTime = 10
        self.toaster.clear_toasts()
        self.toaster.show_toast(self.basicNewToast)

    def setCallback(self, activatedEventArgs: ToastActivatedEventArgs):
        print(activatedEventArgs.arguments)

    def toastReset(self, toastBody):
        if toastBody == self.basicNewToast:  # 基础模式下的更新
            self.basicNewToast.SetBody(f"{self.toastSet['title']}\n" +
                                       f"{self.toastSet['body']}")
        elif toastBody == self.newToast:  # 进度条模式下的更新
            self.toaster.applicationText = self.toastSet['body']
            toastBody.SetBody(self.toastSet['title'])
            self.progressBar.status = self.toastSet['head']
            self.progressBar.caption = self.toastSet['left']
            self.progressBar.progress = self.toastSet['progress']
            self.progressBar.progress_override = self.toastSet['right']
            toastBody.progressBar = self.progressBar


if __name__ == '__main__':
    test = Popup()
    test.Process(update=True)
    time.sleep(2)
    test.Process(title='AutoNeting',
                 body='We are helping you connect Internet',
                 head='Connecting...',
                 left='Checking Setting', progress=0.1,
                 right='will Login',
                 update=True)
    time.sleep(2)
    test.Process(head='Logining...',
                 left='logining', progress=0.7,
                 right='soon',
                 update=True)
    time.sleep(1)
    test.Basic(title='Sucess', body='Finish')
    print(test.toastSet)
    time.sleep(1)
    test.ActionBasic(title='Fail', body='Check to retry')
    time.sleep(2)
    test.Basic(title='Sucess', body='Finish')
