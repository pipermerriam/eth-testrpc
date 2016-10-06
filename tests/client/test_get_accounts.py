def test_get_accounts(client, hex_accounts):
    assert client.get_accounts() == hex_accounts
