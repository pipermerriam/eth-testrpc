from __future__ import print_function

import random
import codecs

from ethereum import slogging as slog


import click

from ethereum.tester import (
    accounts,
)

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
    default=False,
    type=bool,
)
def runserver(host, port, trace):
    application = get_application()

    print(application.rpc_methods.web3_clientVersion())

    print("\nAvailable Accounts\n==================")
    for account in accounts:
        print('0x' + codecs.decode(codecs.encode(account, 'hex'), 'utf8'))

    print("\nTransaction tracing is %s." % ( "enabled" if trace else "disabled"  ))
    print("\nListening on %s:%s" % (host, port))

    server = make_server(
        host,
        port,
        application,
    )

    if trace:
        slog.configure('eth.vm.op:trace', True, False)
        #out_hdlr = log.StreamHandler(sys.stdout)
        #out_hdlr.setFormatter(log.Formatter('%(message)s'))
        #out_hdlr.setLevel(log.DEBUG)
        #slog.addHandler(out_hdlr)

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
