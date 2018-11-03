## Utils For Python

### Installation:
    pip install utilx

#### usage:
	from utilx.mongodb import MongoDB
	uri = 'mongodb://user:password@host:27017/db'
	db = MongoUtil(uri)
	print(db.use("$test.user").find_one())

	from utilx.mongodb import MongoUtil
	mongo = MongoUtil(uri)
    class User(Document):
        __connect__ = mongo
        __table__ = "access_user"
    _id = User(username="lyt", password="111111").save()
    user = User.find_one({"_id": _id})
    print(user)