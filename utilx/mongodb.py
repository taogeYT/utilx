from pymongo import MongoClient
import os
import datetime


class MongoDB(object):
    """
    db = MongoDB()
    db.table = "lyt2"
    print(list(db.find()))
    print(db["test"]["lyt"].find_one())
    db.table = "test.lyt1"
    print(list(db.find()))
    """
    def __init__(self, uri=None, table=None):
        if "://" in uri:
            self.client = MongoClient(uri)
            self._db_name = os.path.split(uri)[-1].split("?")[0]
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


class NameParser(object):
    def __init__(self, name):
        name = name.strip()
        names = name.split(".", 1)
        names.reverse()
        if name.startswith("$"):
            self._db = names.pop().lstrip("$")
            self._table = names[0] if names else ""
        else:
            self._db = ""
            self._table = name

    @property
    def db(self):
        return self._db

    @property
    def table(self):
        return self._table


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

    def use(self, name):
        name = NameParser(name)
        if name.db:
            self = self.get_database(name.db)
        else:
            self = self.get_database()
        if name.table:
            self = self.get_collection(name.table)
        return self

    @property
    def now(self):
        return datetime.datetime.now()

    @property
    def utcnow(self):
        return datetime.datetime.utcnow()


class _ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name != "Document":
            attrs["mongo"] = attrs["__connect__"]
            attrs['db'] = attrs["mongo"].use(attrs["__table__"])
        return type.__new__(mcs, name, bases, attrs)


class Document(dict, metaclass=_ModelMetaclass):
    """
    mongo 文档操作
    mongo = MongoUtil(host="localhost")
    class User(Document):
        __connect__ = mongo
        __table__ = "access_user"

    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    user.update_one({"$set": {"password": "123456"}})
    """

    def save(self):
        now = self.now
        self.update({"create_time": now, "update_time": now})
        rs = self.db.insert_one(self)
        return rs.inserted_id

    @classmethod
    def find_one(cls, condition):
        doc = cls.db.find_one(condition)
        if doc:
            return cls(doc)
        else:
            return {}

    @classmethod
    def find(cls, condition):
        docs = cls.db.find(condition)
        return (cls(doc) for doc in docs)

    def update_one(self, update=None):
        _id = self.get("_id")
        if update:
            update.setdefault("$set", {}).update({"update_time": self.now})
            self.db.update_one({"_id": _id}, update)
        else:
            self.update({"update_time": self.now})
            self.db.update({"_id": _id}, self)

    @property
    def now(self):
        return datetime.datetime.now()

    @property
    def utcnow(self):
        return datetime.datetime.utcnow()


def main():
    uri = 'mongodb://data:datadata@loc213:27017/data'
    mongo = MongoUtil(uri)

    class User(Document):
        __connect__ = mongo
        __table__ = "access_user"
    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    print(user)


if __name__ == '__main__':
    main()
