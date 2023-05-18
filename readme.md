# <img src="./resources/icon.ico" alt="icon" style="zoom:50%;" /> Auto Connect

[English](./readme_EN.md)

这是一个自动联网程序,可以帮助你连接WIFI[^1],帮助你登录校园网,让你的电脑时刻处于联网状态[^2]~  

**目前仅支持CQUST校园网登录**  



## 功能

目前该程序为测试版本，已经支持以下功能

1.  网络连通性检测（基础）
2.  登录状态检测（基础）
3.  主动连接预设WLAN（需要且支持时）（无法考虑考虑钓鱼WLAN）
4.  自动登录账号
5.  密码加密
6.  通知栏弹窗消息
7.  运行日志记录
8.  程序异常记录
9.  实时的配置

## 使用

### 安全说明

尽管在第一次正常运行后我们会对你的密码进行加密，我们使用的是贵校提供的密钥，加密后的密码仍然可以被使用。同时，贵校的信息传输为明文传输，类似这些非我能控制的安全问题还请不要为难我

**在任何时候都请保管好您的设备，避免本程序和配置文件被读取或相关文件被替换等，导致您的密码泄露。**我无法为此承担任何责任，程序目前还存在一些容错性和程序自身安全性的不足，希望您能提供帮助

如果您的配置存在危险配置，特别是预设WIFI中存在钓鱼WIFI的您可能会遇到危险。连接时我们无法告诉您网络的安全性，但是会提醒您我们使用了哪个WLAN（您自行连接WLAN可能不会提示）。

您可以阅读日志 schoolInt.log 和 tmp.log[^log]来了解程序进行了哪些事

[^log]: schoolInt.log是本次程序运行实时产生的日志，tmp.log是程序上次运行的日志，保留至程序下次执行以备检查。

### 试用

在[release]()中下载最新版

根据程序提示来使用

> 第一次使用请用管理员权限运行，程序需要在“开始菜单”（重要）和“桌面”（常规）创建快捷方式。第一次使用还需要调用记事本来帮助您填写所需的信息。
>
> 程序会提醒你。

您可以通过自行编译该项目来获得更安全的试用版本。**请不要违规发行本项目的任何内容！**

### 研究

请 [阅读开发者文档](develop.md)，程序的设计和各个模块的解释也在开发者文档中

### 参考数据

| 序号 |                   情况                   | 模拟性质 | 用时(s) |
| :--: | :--------------------------------------: | :------: | :-----: |
|  1   | 上一次断网检测未结束且认为网络正常(有线) | 用户断网 |   20    |
|  2   |         刚开机登录，组件加载不全         | 正常断网 |    9    |
|  3   |    有线已连接，但未登录(刚开机并解锁)    | 正常断网 |    5    |
|  4   |          需要连接WLAN，且未登录          | 正常断网 |   18    |
|  5   |          需要连接WLAN，但已登录          | 用户断网 |    9    |

| 序号 | 状态              | 内存(MB)      | 网络(Mbps) | CPU使用率(%相对) |
| ---- | ----------------- | ------------- | ---------- | ---------------- |
| 1    | 刚启动(非刚开机)  | 34            | 0.1        | 0.1              |
| 2    | 刚启动(刚开机)    | 34            | 0.1        | 1.2              |
| 3    | 后台连接网络/检测 | <31           | 0.1-0      | 0.1-0            |
| 4    | 后台检测网络连接  | ->10.9[^最低] | 0.1-0      | 0.1-0            |

*仅在作者及其朋友电脑上测试，数据来自计时器或者任务管理器，仅供参考*

目前使用起来接近无感（除了提示电脑组件加载不全，这是可以取消的）

## 作者

电脑打开时没有网络是一件不顺畅的事，学校服务器应该不支持频繁的请求，否则我们可以一直请求登录来保证时刻在线，并在断网后再次持续请求登录。但是有时我们也会手动登录或者存在不需要登录的情况，我自认为检查网络断开后尝试一次登录可以有效减少计算机及网络资源的浪费（可能就我这么认为，哈哈哈）

作者 **kai**<img src="https://avatars.githubusercontent.com/u/88734046?v=4" alt="myHeadPic" style="zoom: 5%;" /> 

如果您能给予赞助，请允许我在此感谢你。

## 未来

1. - [ ] 添加多线程支持，让检测与连接更迅速
2. 添加配置界面，让配置更简单：
   - [ ] 更好地配置文件
   - [ ] 自定义网络适配器的优先级
   - [ ] 自定义是否自启
   - [ ] 自定义是否弹窗
   - [ ] 自定义是否需要自动登录
   - [ ] 自定义网络安全检查（目前不支持网络安全检查）
3. - [ ] 托盘程序
4. - [ ] Win7弹窗（界面）
5. - [ ] 断网提示
6. - [ ] 设置自启策略
7. - [ ] 使用C语言设置打开WLAN功能的模块
8.  暂时没有其他计划了

## 常见问题

目前有一下可能的问题：

* Q: 开机后程序退出

  A: 目前已经检测到这个问题。它是一个bug：在电脑刚刚开机时系统组件还未完全加载，这时候我们无法发送网络请求。而我还没有处理这个问题

* Q: 弹窗消息缺失图标

  A: 在Windows需要程序注册AUMID[^AUMID],我们会在你的“开始·菜单”中创建程序快捷方式来达到这个目的。如果没有显示图标，1. 可能是系统参数没有更新，重启电脑可以解决这个问题； 2.  可能在“开始·菜单”中的快捷方式缺失，再您下次运行程序时程序会提醒你的；3. 最不可能的就是您手动修改了有关参数

* Q: 连接速度似乎有点慢

  A: 非常抱歉，我希望较好的节约系统资源，因此很多检测并非真正的**实时**。另外，程序的运行速度还与您的设备、网络、服务器状态有关。

* Q: 我的密码没有被加密

  A: 请您修改<code>set.yaml</code>中<code>isEncrypted</code>的值为<code>'False'</code>，像这样（请注意冒号后面有个空格）：

  > <code>isEncrypted: False</code>

  程序会在下次运行时使用服务器提供的密钥来加密你的信息
  
* Q: WLAN和有线同时使用的时候电脑没有网络却不帮我自动连接

  A: 前提应该是您的WLAN可以上网，此时可能是程序刚检查完一次网络，尚未开始下一次检测；也有可能您的WLAN比有线网络跳数更低（更快）以至于系统选择WLAN（非本程序设置）。



[^1]: 这取决于你的设备是否支持以及你是否启用它

[^2]: 我们只能在程序层面帮您操作,在物理环境不支持的情况下这个程序无法帮助你
[^AUMID]: Application User Model ID
[^最低]: 低于30MB，但在一段时间后会低于20MB，目前有记录的常见最低占用为10.9MB

[img, icon]: 很抱歉，这张图是在米游社获取的，我使用了很多工具都找不到他的作者，还请作者联系我并希望作者允许我使用它



