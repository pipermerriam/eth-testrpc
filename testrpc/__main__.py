from __future__ import print_function

import time
import threading
import codecs

from wsgiref.simple_server import make_server
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

    server = make_server(host, port, application)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()  # noqa
