def test_eth_getTransactionByHash_for_unknown_hash(rpc_client):
    result = rpc_client(
        method="eth_getTransactionByHash",
        params=["0x0000000000000000000000000000000000000000000000000000000000000000"],
    )

    assert result is None


def test_eth_getTransactionByHash(rpc_client, accounts):
    tx_hash = rpc_client(
        method="eth_sendTransaction",
        params=[{
            "from": accounts[0],
            "to": accounts[1],
            "value": 1234,
            "data": "0x1234",
            "gas": 100000,
        }],
    )
    txn = rpc_client(
        method="eth_getTransactionByHash",
        params=[tx_hash]
    )

    assert txn
    assert txn['hash'] == tx_hash
