def test_coinbase(client, accounts):
    assert client.get_coinbase() == accounts[0]
