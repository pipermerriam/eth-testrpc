import threading
import socket
import json
import requests

import pytest


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def accounts():
    from ethereum import tester
    from ethereum import utils
    return [utils.encode_hex(acct) for acct in tester.accounts]


@pytest.yield_fixture()
def rpc_server():
    from wsgiref.simple_server import make_server
    from testrpc.server import application
    from testrpc.testrpc import evm_reset

    evm_reset()

    port = get_open_port()

    server = make_server('127.0.0.1', port, application)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()


nonce = 0


@pytest.fixture()
def rpc_client(rpc_server):
    from eth_tester_client.utils import force_obj_to_text

    host, port = rpc_server.server_address
    endpoint = "http://{host}:{port}".format(host=host, port=port)

    def make_request(method, params=None, raise_on_error=True):
        global nonce
        nonce += 1  # NOQA
        payload = {
            "id": nonce,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
        }
        payload_data = json.dumps(force_obj_to_text(payload, True))
        response = requests.post(endpoint, data=payload_data)

        if raise_on_error:
            assert response.status_code == 200

            result = response.json()

            if 'error' in result:
                raise AssertionError(result['error'])

            assert set(result.keys()) == {"id", "jsonrpc", "result"}
        return response.json()['result']

    return make_request
