import requests
import json


def test_server_listens(rpc_server, accounts):
    host, port = rpc_server.server_address

    endpoint = "http://{host}:{port}".format(host=host, port=port)
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_sendTransaction",
        "params": [{
            "from": accounts[0],
            "to": accounts[1],
        }],
    }
    response = requests.post(endpoint, data=json.dumps(payload))

    assert response.status_code == 200

    result = response.json()

    assert set(result.keys()) == {"id", "jsonrpc", "result"}, result['error']

    assert len(result["result"]) == 66
