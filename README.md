## Utils For Python

### Installation:
    pip install utilx

#### usage:
	from utilx.mongodb import MongoDB
	uri = 'mongodb://user:password@host:27017/db'
	db = MongoDB(uri, "test")
	print(db.find_one())
