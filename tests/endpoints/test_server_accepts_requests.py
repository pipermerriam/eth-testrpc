import requests


def test_server_listens(rpc_server):
    host, port = rpc_server.address

    endpoint = "http://{host}:{port}".format(host=host, port=port)
    response = requests.post(endpoint)

    assert response.status_code == 200
