import os


def is_using_gevent():
    return 'TESTRPC_ASYNC_GEVENT' in os.environ


if is_using_gevent():
    from .gevent_async import (  # noqa
        Timeout,
        spawn,
        sleep,
        subprocess,
        socket,
        threading,
        make_server,
    )
else:
    from .stdlib_async import (  # noqa
        Timeout,
        spawn,
        sleep,
        subprocess,
        socket,
        threading,
        make_server,
    )
