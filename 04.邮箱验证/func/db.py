import pymysql
import datetime
from .assist import get_token, get_authcode


class Database:
    def __init__(self, host, user, pwd, database):
        self.db = pymysql.connect(host, user, pwd, database)
        self.cursor = self.db.cursor()
        self.database = database
        self.table = 'user'

    def set_table(self, table):
        self.table = table

    def query_by_id(self, id):
        """
        通过ID查询
        :param id:
        :return:
        """
        sql = "select * from %s where id='%s'" % (self.table, id)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            return data
        except Exception as e:
            print(e)

    def query_by_email(self, name, email):
        """
        通过name以及email查询
        :return:
        """
        sql = "select * from %s where name='%s' and email='%s'" % (self.table, name, email)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            return data
        except Exception as e:
            print(e)
            return None

    def query_by_token(self, token, authcode):
        """
        通过token以及authcode查询
        :return:
        """
        sql = "select * from %s where token='%s' and authcode='%s'" % (self.table, token, authcode)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            return data
        except Exception as e:
            print(e)
            return False

    def insert_record(self, name, email):
        """
        插入数据
        :param name:
        :param email:
        :return:
        """
        id = self.get_max_id()
        if not id:
            id = 0
        elif id == -1:
            return
        id += 1
        # 生成token
        current_time = datetime.datetime.now()
        token = get_token(id, name, current_time.strftime("%Y-%m-%d %H:%M:%S"))
        # 生成验证码
        authcode = get_authcode()

        sql = "insert into %s (name, email, token, authcode, created_time) values('%s', '%s', '%s', '%s', '%s')" % (self.table, name, email, token, authcode, current_time)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            self.db.rollback()
            return False

    def update(self, token, authcode):
        """
        更新状态
        :param token:
        :param authcode:
        :return:
        """
        status = 1
        sql = "update %s set verification_status=%s where token='%s' and authcode='%s'" % (self.table, status, token, authcode)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print("commit!")
        except Exception as e:
            print(e)
            self.db.rollback()

    def get_max_id(self):
        """
        获取当前数据库记录中的最大id
        :return:
        """
        sql = "select max(id) from %s" % self.table
        try:
            self.cursor.execute(sql)
            id = self.cursor.fetchone()
            return id[0]
        except Exception as e:
            return -1

    def close(self):
        """
        关闭数据库
        :return:
        """
        self.db.close()
