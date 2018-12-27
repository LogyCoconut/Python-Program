# 此文档是对项目的整体说明
>* 项目功能基于Flask、MySQL以及SendCloud完成
>* 项目是对实验楼实验的完全复刻，[原地址在此](https://www.shiyanlou.com/courses/622/labs/2063/document)

### **func文件夹说明**
`db.py` *数据库对象的封装，实现了对数据库的基本操作*

`process.py` *写数据库、发送邮件、验证邮件*

`assist.py` *生成token(个人唯一标识ID)与authcode(随机验证码)*

### **templates文件夹说明**
`display.html` *展示信息页面*

`register.html` *注册页面*

### **主函数说明**
`main.py` *url配置、网络请求的处理*

### **SendCloudAPI说明**
* 在[官网](https://www.sendcloud.net/)注册账号
* 配置模板页面,将类型改为触发型，记住调用名称 -- *SendCloud测试模板*
* 向SendCloud接口发送一个json数据，格式如下：*(如果正确则返回200)*
```
    url = "http://api.sendcloud.net/apiv2/mail/sendtemplate"
    xsmtpapi = {
        'to': [email],
        # sub里%%是模板里的变量
        'sub': {
            '%name%': [name],
            '%url%': [link],
        }
    }

    params = {
        "apiUser": API_USER,  # 使用apiUser和apiKey进行验证
        "apiKey": API_KEY,
        "templateInvokeName": "test_template_send",  # 调用名称
        "xsmtpapi": json.dumps(xsmtpapi),
        "from": "sendcloud@sendcloud.org",  # 发信人, 用正确邮件地址替代
        "fromName": "",
        "subject": "SendCloud python template"
    }
    requests.post(url, data=params)
```

*这里因为官方API更新了，所以和实验楼的有出入：）*
[文档中心](http://www.sendcloud.net/doc/) -- [测试接口](https://www.sendcloud.net/doc/test/#!/mail/post_mail_sendtemplate) -- [代码示例](http://www.sendcloud.net/doc/email_v2/code/)
