def test_get_accounts(client, accounts):
    assert client.get_accounts() == accounts
