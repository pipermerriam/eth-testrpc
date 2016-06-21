import threading

import pytest


@pytest.fixture(scope="session")
def accounts():
    from ethereum import tester
    from ethereum import utils
    return [utils.encode_hex(acct) for acct in tester.accounts]


@pytest.fixture(scope="session")
def eth_coinbase(accounts):
    return accounts[0]


@pytest.yield_fixture()
def rpc_server():
    from wsgiref.simple_server import make_server
    from testrpc.server import application
    from testrpc.testrpc import evm_reset

    evm_reset()

    server = make_server('127.0.0.1', 8545, application)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()
