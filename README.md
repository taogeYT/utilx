## Utils For Python

### Installation:
    pip install utilx

#### usage:
	from utilx.mongodb import MongoDB
	uri = 'mongodb://user:password@host:27017/db'
	db = MongoDB(uri, "test")
	print(db.find_one())

	from utilx.mongodb import MongoUtil
	mongo = MongoUtil(uri)
    class User(Document):
        __connect__ = mongo
        __table__ = "access_user"
    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    print(user)