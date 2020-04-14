from bson import ObjectId
from pymongo import MongoClient
import datetime


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
    collection = MongoUtil(host="centos")

    查询方法
    collection.use("$test.students").find_one()
    """

    def use(self, name):
        name = NameParser(name)
        if name.db:
            instance = self.get_database(name.db)
        else:
            instance = self.get_database()
        if name.table:
            instance = instance.get_collection(name.table)
        return instance

    @property
    def now(self):
        return datetime.datetime.now()

    @property
    def utcnow(self):
        return datetime.datetime.utcnow()


class _ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name != "Document":
            attrs["client"] = attrs["__connect__"]
            attrs['collection'] = attrs["client"].use(attrs["__table__"])
        return type.__new__(mcs, name, bases, attrs)


class Document(dict, metaclass=_ModelMetaclass):
    """
    client 文档操作
    client = MongoUtil(host="localhost")
    class User(Document):
        __connect__ = client
        __table__ = "access_user"

    class UserUTC(Document):
        __connect__ = client
        __table__ = "access_user"
        # 时间切换到标准时区，默认本地时间
        utc = True

    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    user.update_one({"$set": {"password": "123456"}})
    """
    utc = False
    client = None
    collection = None

    def save(self):
        now = self.now
        self.update({"create_time": now, "update_time": now})
        rs = self.collection.insert_one(self)
        _id = rs.inserted_id
        self.update({"_id": _id})
        return _id

    @classmethod
    def find_one(cls, condition=None, *args, **kwargs):
        doc = cls.collection.find_one(condition, *args, **kwargs)
        if doc:
            return cls(**doc)
        else:
            return cls()

    @classmethod
    def find(cls, *args, **kwargs):
        docs = cls.collection.find(*args, **kwargs)
        return (cls(**doc) for doc in docs)

    def update_one(self, update=None, upsert=False,
                   bypass_document_validation=False,
                   collation=None, array_filters=None, session=None):
        _id = self.get("_id", ObjectId())
        if update:
            if "_id" not in self:
                now = self.now
                self.update({"_id": _id, "create_time": now, "update_time": now})
                update.setdefault("$set", {}).update(self)
            else:
                update.setdefault("$set", {}).update({"update_time": self.now})
            self.collection.update_one({"_id": _id}, update, upsert, bypass_document_validation, collation, array_filters, session)
        else:
            self.update({"update_time": self.now})
            self.collection.update_one({"_id": _id}, {"$set": self}, upsert, bypass_document_validation, collation, array_filters, session)

    @property
    def now(self):
        if self.utc:
            return self.client.utcnow
        else:
            return self.client.now


def main():
    uri = 'mongodb://data:datadata@loc213:27017/data'
    mongo = MongoUtil(uri)

    class User(Document):
        utc = True
        __connect__ = mongo
        __table__ = "access_user"
    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    print(user)
    import time
    time.sleep(1)
    user.update_one()
    user.update_one({"$set": {"append": "new"}})
    for user in User.find():
        print(user)


if __name__ == '__main__':
    main()
