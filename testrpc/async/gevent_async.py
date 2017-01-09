import gevent
from gevent.pywsgi import (  # noqa: F401
    WSGIServer,
)


sleep = gevent.sleep
socket = gevent.socket
spawn = gevent.spawn
subprocess = gevent.subprocess
threading = gevent.threading


class Timeout(gevent.Timeout):
    def check(self):
        pass


def make_server(host, port, application, *args, **kwargs):
    server = WSGIServer((host, port), application, *args, **kwargs)
    return server
