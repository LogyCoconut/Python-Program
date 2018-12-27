from .db import Database
import json
import requests
import datetime

# 数据库配置
HOST = '******'
USER = '******'
PWD = '******'
DATABASE = '******'
TABLE = '******'

# 调用SendCloud的WEBAPI所需参数
API_USER = "******"
API_KEY = "******"
url = "http://api.sendcloud.net/apiv2/mail/sendtemplate"

# 邮箱的有效认证时长为1天(s)
one_day_in_second = 5184000


def write_data(name, email):
    """
    写入数据库
    :param name: 用户名
    :param email:  邮箱
    :return:
    """
    database = Database(HOST, USER, PWD, DATABASE)
    database.set_table(TABLE)
    outcome = database.insert_record(name, email)
    database.close()
    return outcome


def send_email(name, email):
    """
    给邮箱发送验证信息
    :param name:
    :param email:
    :return:
    """
    database = Database(HOST, USER, PWD, DATABASE)
    database.set_table(TABLE)

    # 使用name以及email查询数据库
    record = database.query_by_email(name, email)
    database.close()
    print(record)
    name = record[1]
    email = record[2]
    token = record[3]
    authcode = record[5]

    # 构造认证链接
    link = "http:127.0.0.1:5000/do_verification?token=%s&authcode=%s" % (token, authcode)

    # "to"：指定目标邮箱s
    # 将模板中定义的变量 %name% 和 %url% 分别进行替换成真实值
    xsmtpapi = {
        'to': [email],
        'sub': {
            '%name%': [name],
            '%url%': [link],
        }
    }

    params = {
        "apiUser": API_USER,  # 使用apiUser和apiKey进行验证
        "apiKey": API_KEY,
        "templateInvokeName": "test_template_send",
        "xsmtpapi": json.dumps(xsmtpapi),
        "from": "sendcloud@sendcloud.org",  # 发信人, 用正确邮件地址替代
        "fromName": "椰子呆呆",
        "subject": "SendCloud python template"
    }

    # 使用POST请求
    r = requests.post(url, data=params)
    if r.status_code == 200:
        return True
    else:
        return False


def verify_mail(token, authcode):
    """
    验证邮箱
    :param token:
    :param authcode:
    :return:
    """
    database = Database(HOST, USER, PWD, DATABASE)
    database.set_table(TABLE)
    record = database.query_by_token(token, authcode)
    created_time = record[6]

    # 如果时间差大于一天，则验证无效
    d = (datetime.datetime.now() - created_time).total_seconds()
    if d > one_day_in_second:
        database.close()
        return False
    else:
        database.update(token, authcode)
        database.close()
        return True
