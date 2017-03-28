from __future__ import print_function

import random
import codecs

import click

from ethereum.tester import (
    accounts,
)
from ethereum.trace import Trace

from .server import get_application
from .compat import (
    make_server,
    spawn,
    sleep,
)

@click.command()
@click.option(
    '--host',
    '-h',
    default='localhost',
)
@click.option(
    '--port',
    '-p',
    default=8545,
    type=int,
)
@click.option(
    '--trace',
    '-t',
    is_flag=True,
)
def runserver(host, port, trace):
    application = get_application()

    print(application.rpc_methods.web3_clientVersion())

    print("\nAvailable Accounts\n==================")
    for account in accounts:
        print('0x' + codecs.decode(codecs.encode(account, 'hex'), 'utf8'))

    print("\nTransaction tracing is %s." % ("enabled" if trace else "disabled"))

    print("\nListening on %s:%s" % (host, port))

    server = make_server(
        host,
        port,
        application,
    )

    Trace.enabled = trace

    spawn(server.serve_forever)

    try:
        while True:
            sleep(random.random())
    except KeyboardInterrupt:
        try:
            server.stop()
        except AttributeError:
            server.shutdown()


if __name__ == "__main__":
    main()  # noqa
