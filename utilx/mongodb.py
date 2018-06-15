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

    def __getitem__(self, key):
        return self.client[key]

    def use(self, name):
        self._db_name = name

    @property
    def table(self):
        if "." in self._table:
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


def main():
    uri = 'mongodb://data:datadata@centos:27017/data'
    db = MongoDB(uri)
    db.table = "test.lyt2"
    # db.insert({"test": "123"})
    print(list(db.find()))
    db.table = "lyt"
    db.insert({'lyt': "test"})
    print(db.find_one())

if __name__ == '__main__':
    main()