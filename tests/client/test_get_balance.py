def test_deploying_contract(client, hex_accounts):
    pre_balance = client.get_balance(hex_accounts[1])

    client.send_transaction(
        _from=hex_accounts[0],
        to=hex_accounts[1],
        value=1234,
    )

    post_balance = client.get_balance(hex_accounts[1])

    assert post_balance - pre_balance == 1234
