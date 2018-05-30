from pymongo import MongoClient
import os


class MongoDB(object):
    def __init__(self, uri=None, table=None):
        if "://" in uri:
            self.client = MongoClient(uri)
            self._db_name = os.path.split(uri)[-1]
        else:
            self.client = MongoClient()
            self._db_name = uri
        self.table = table

    def __getattr__(self, name):
        if self.table:
            return getattr(self.client[self._db_name][self.table], name)
        else:
            return getattr(self.client[self._db_name], name)

    def use(self, name):
        self._db_name = name

    def close(self):
        self.client.close()


def create_db():
    uri = 'mongodb://test:test@localhost:20223/test'
    table = "test"
    db = MongoDB(uri, table)
    return db
