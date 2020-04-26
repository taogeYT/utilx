# Utils For Python

## Installation:
    pip install utilx

## 基于supervisor让项目一键自启动挂后台工具
确保环境中已经正确安装supervisor
项目路径下新建 task.py 下面代码演示将ping example网站任务通过supervisor挂载成为后台进程

    from utilx.deploy import Deployment
    commands = [("ping_example", "ping www.example.com")] # 元祖中第一个表示任务名称，第二个是需要挂后台的启动命令
    Deployment(commands=commands).deploy()

python task.py start # 启动任务到supervisor后台    
supervisorctl status # 查看ping example网站任务状态     
python task.py stop # 任务从supervisor后台移除   

## 工具类mongo操作封装
	from utilx.mongodb import MongoUtil
	mongo = MongoUtil('mongodb://user:password@host:27017/db')
	print(db.use("collection_name").find_one())

    class User(Document):
        __connect__ = mongo
        __table__ = "user"
    User(username="lyt", password="111111").save()
    user = User.find_one()  