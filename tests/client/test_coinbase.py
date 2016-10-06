def test_coinbase(client, hex_accounts):
    assert client.get_coinbase() == hex_accounts[0]
