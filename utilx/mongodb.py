from pymongo import MongoClient
import urllib
import os


class MongoDB(object):
    def __init__(self, uri=None, table=None):
        if "://" in uri:
            self.client = MongoClient(uri)
            self._db_name = os.path.split(uri)[-1]
            self._src_db_name = self._db_name
        else:
            self.client = MongoClient()
            self._db_name = uri
            self._src_db_name = self._db_name
        self._table = table

    def __getattr__(self, name):
        if self.table:
            return getattr(self.client[self._db_name][self.table], name)
        else:
            return getattr(self.client[self._db_name], name)

    def get(self, table):
        pass

    def __getitem__(self, key):
        return self.client[key]

    def use(self, name):
        self._db_name = name

    @property
    def table(self):
        if self._table and "." in self._table:
            self._db_name, _table = self._table.split(".")
            self.use(self._db_name)
            return _table
        else:
            if self._db_name == self._src_db_name:
                return self._table
            else:
                self._db_name = self._src_db_name
                return self._table

    @table.setter
    def table(self, value):
        self._table = value

    def close(self):
        self.client.close()


class MongoUtil(MongoClient):
    """
    创建方法
    db = MongoUtil(host="centos")

    查询方法
    db.use("$test.students").find_one()
    """
    # def __init__(self,
    #         host=None,
    #         port=None,
    #         document_class=dict,
    #         tz_aware=None,
    #         connect=None,
    #         **kwargs):
    #     # if host is None:
    #     #     self._uri = URI("")
    #     # else:
    #     #     self._uri = URI(host)
    #     # self.default_db = self._uri.db
    #     super(MongoDB, self).__init__(host, port, document_class, tz_aware, connect, **kwargs)

    # # def get_default_database(self):
    # #     if self.default_db:
    # #         return self.get_database(self.default_db)
    # #     else:
    # #         raise ValueError("没有默认的数据库")

    def use(self, name):
        name = NameParser(name)
        if name.db:
            self = self.get_database(name.db)
        else:
            self = self.get_default_database()
        if name.table:
            self = self.get_collection(name.table)
        return self

    def get_now(self):
        return datetime.datetime.now()

    def get_utcnow(self):
        return datetime.datetime.utcnow()


def main():
    uri = 'mongodb://data:datadata@loc213:27017/data'
    db = MongoDB(uri)
    db.table = "test.lyt2"
    print(list(db.find()))
    db.table = "lyt"
    print(list(db.find()))
    print(db["test"]["lyt"].find_one())
    # uri = 'mongodb://data:datadata@10.108.129.213:27017/data'
    # db = MongoDB(uri)
    # db.table = "lyt"
    # print(db.find_one())

if __name__ == '__main__':
    main()
