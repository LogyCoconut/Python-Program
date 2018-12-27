import hashlib
import random
import string


def get_token(id, name, time):
    """
    根据id、姓名、时间戳生成密文
    :param id:
    :param name:
    :param time:
    :return:
    """
    data = "%s%s%s" % (id, name, time)
    hash_md5 = hashlib.md5(data.encode("utf-8"))
    return hash_md5.hexdigest()


def get_authcode(length=20):
    """
    生成随机字符串
    :return:
    """
    charset = list(string.digits + string.ascii_letters)
    random.shuffle(charset)
    return "".join(charset[:length])
