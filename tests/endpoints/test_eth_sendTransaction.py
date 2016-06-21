import requests
import json


def test_server_listens(rpc_server, accounts):
    host, port = rpc_server.server_address

    endpoint = "http://{host}:{port}".format(host=host, port=port)
    response = requests.post(endpoint, data=json.dumps({
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_sendTransaction",
        "params": [{
            "from": accounts[0],
            "to": accounts[1],
        }],
    }))

    assert response.status_code == 200

    result = response.json()

    assert set(result.keys()) == {"id", "jsonrpc", "result"}

    assert len(result["result"]) == 66
