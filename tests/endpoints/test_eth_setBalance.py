def test_eth_setBalance(rpc_client, accounts):
    before_balance = rpc_client("eth_getBalance", [accounts[0]])

    rpc_client("eth_setBalance", [accounts[0], 1234])

    after_balance = rpc_client("eth_getBalance", [accounts[0]])
    
    assert before_balance == 1000000000000000000000000
    assert after_balance  == 1234
