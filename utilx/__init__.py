__version__ = '1.1.0'


def _get_ip():
    import socket
    _ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    return _ip


ip = _get_ip()
