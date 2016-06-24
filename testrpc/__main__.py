from __future__ import print_function
import argparse
from wsgiref.simple_server import make_server
import threading

from ethereum.tester import (
    accounts,
    set_logging_level,
)

from .server import application
from .testrpc import (
    web3_clientVersion,
    evm_reset,
)


parser = argparse.ArgumentParser(
    description='Simulate an Ethereum blockchain JSON-RPC server.'
)
parser.add_argument('-p', '--port', dest='port', type=int,
                    nargs='?', default=8545)
parser.add_argument('-d', '--domain', dest='domain', type=str,
                    nargs='?', default='localhost')


def main():
    args = parser.parse_args()

    print(web3_clientVersion())

    evm_reset()

    set_logging_level(2)

    print("\nAvailable Accounts\n==================")
    for account in accounts:
        print('0x%s' % account.encode("hex"))

    print("\nListening on %s:%s" % (args.domain, args.port))

    server = make_server(args.domain, args.port, application)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    main()
