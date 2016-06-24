def test_eth_getBalance(rpc_client, accounts):
    before_balance = rpc_client("eth_getBalance", [accounts[1]])

    rpc_client(
        method="eth_sendTransaction",
        params=[{
            "from": accounts[0],
            "to": accounts[1],
            "value": 1234,
        }],
    )

    after_balance = rpc_client("eth_getBalance", [accounts[1]])

    assert after_balance - before_balance == 1234
