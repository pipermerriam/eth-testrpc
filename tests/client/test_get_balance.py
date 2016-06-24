def test_deploying_contract(client, accounts):
    pre_balance = client.get_balance(accounts[1])

    client.send_transaction(
        _from=accounts[0],
        to=accounts[1],
        value=1234,
    )

    post_balance = client.get_balance(accounts[1])

    assert post_balance - pre_balance == 1234
