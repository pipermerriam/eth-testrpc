def test_eth_sendTransaction(rpc_client, accounts):
    for _ in range(3):
        rpc_client(
            method="eth_sendTransaction",
            params=[{
                "from": accounts[0],
                "to": accounts[1],
                "value": 1,
            }],
        )

    for _ in range(5):
        rpc_client(
            method="eth_sendTransaction",
            params=[{
                "from": accounts[1],
                "to": accounts[0],
                "value": 1,
            }],
        )

    account_0_txn_count = rpc_client(
        method="eth_getTransactionCount",
        params=[accounts[0]],
    )
    assert account_0_txn_count == "0x3"

    account_1_txn_count = rpc_client(
        method="eth_getTransactionCount",
        params=[accounts[1]],
    )
    assert account_1_txn_count == "0x5"

    account_2_txn_count = rpc_client(
        method="eth_getTransactionCount",
        params=[accounts[2]],
    )
    assert account_2_txn_count == "0x0"
