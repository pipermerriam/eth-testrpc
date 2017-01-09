import requests


def test_server_listens(rpc_server):
    try:
        host, port = rpc_server.address
    except AttributeError:
        host, port = rpc_server.server_address

    endpoint = "http://{host}:{port}".format(host=host, port=port)
    response = requests.post(endpoint)

    assert response.status_code == 200
