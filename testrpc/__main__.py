from __future__ import print_function

import random
import codecs

import gevent
from gevent.pywsgi import (
    WSGIServer,
)

import click

from ethereum.tester import (
    accounts,
)

from .server import application
from .testrpc import (
    web3_clientVersion,
    evm_reset,
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
def main(host, port):

    print(web3_clientVersion())

    evm_reset()

    print("\nAvailable Accounts\n==================")
    for account in accounts:
        print('0x' + codecs.decode(codecs.encode(account, 'hex'), 'utf8'))

    print("\nListening on %s:%s" % (host, port))

    server = WSGIServer(
        (host, port),
        application,
    )

    gevent.spawn(server.serve_forever)

    try:
        while True:
            gevent.sleep(random.random())
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()  # noqa
