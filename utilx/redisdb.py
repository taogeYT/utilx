import redis
from log4py import create_logger


@create_logger()
class RedisDB(object):
    def __init__(self, host='127.0.0.1', port=6379, **kw):
        # print("kw:", host, port, kw)
        kw['host'] = host
        kw['port'] = port
        # pool = redis.ConnectionPool(**kw)
        # self.con = redis.StrictRedis(connection_pool=pool)
        self.con = redis.StrictRedis(**kw)
        self.ps = self.con.pubsub()
        # self.con.delete()

    def __getattr__(self, attr):
        return getattr(self.con, attr)

    def lpush(self, key, data):
        self.log.debug("%s: %s" % (key, data))
        self.con.lpush(key, data)

    def rpop(self, key):
        return self.con.rpop(key)

    def lpop(self, key):
        return self.con.lpop(key)

    def brpop(self, key):
        data = self.con.brpop(key, 0)  # data = (b'msg', b'hello')
        msg = data[1].decode()
        self.log.debug('queue msg: %s' % msg)
        return msg

    def publish(self, channel, msg):
        """
        发布订阅(pub/sub)：广播消息
        >>> channel = "channel1"
        >>> msg = "hello"
        >>> rd = RedisDB()
        >>> rd.publish(channel, msg)
        """
        self.con.publish(channel, msg)

    def is_listen(self, channel):
        if channel.encode() in self.ps.channels:
            return True
        else:
            return False

    def _pubsub_init(self, channel):
        self.ps.subscribe(channel)
        self.ps.listen()

    def subscribe(self, channel, timeout=60):
        """
        发布订阅(pub/sub)：订阅消息
        弊端：如果订阅者掉线，将会丢失所有在短线期间发布者发布的消息
        刚开始监听的时候，会收到一条消息：[b'subscribe', b'channel1', 1]
        >>> channel = "channel1"
        >>> rd = RedisDB()
        >>> rd.pubsub(channel)
        """
        if not self.is_listen(channel):
            self.log.debug('connecting channel: %s' % channel)
            self._pubsub_init(channel)
        msg = self.ps.parse_response(block=False, timeout=timeout)
        self.log.debug('pub/sub msg: %s' % msg)
        return msg

    def test(self):
        self.lpush("syc_task", "hello")


def test_pubsub():
    rd = RedisDB(debug=True)
    channel = "channel1"
    rd.subscribe(channel)
    rd.publish(channel, 'hello again')
    rd.publish(channel, 'hello subscribe')
    rd.subscribe(channel)
    rd.subscribe(channel)


def test():
    rd = RedisDB(debug=True)
    key = 'msg'
    rd.lpush(key, 'hello')
    rd.brpop(key)


if __name__ == '__main__':
    test()
    test_pubsub()
