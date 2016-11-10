def test_get_max_gas(client):
    assert client.get_max_gas() == 3141592
