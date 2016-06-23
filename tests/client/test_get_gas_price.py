def test_get_gas_price(client):
    assert client.get_gas_price() == 1

