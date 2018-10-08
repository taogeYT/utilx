__version__ = '1.0.6'


def _single(func):
    import functools
    ip = None
    @functools.wraps(func)
    def wrapper():
        nonlocal ip
        if ip is None:
            ip = func()
        return ip
    return wrapper

@_single
def _get_ip():
    import socket
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    return ip

ip = _get_ip()
