def test_eth_sendTransactionReceipt_for_unknown_receipt(rpc_client):
    result = rpc_client(
        method="eth_getTransactionReceipt",
        params=["0x0000000000000000000000000000000000000000000000000000000000000000"],
    )

    assert result is None


def test_eth_sendTransactionReceipt(rpc_client, accounts):
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
    tx_receipt = rpc_client(
        method="eth_getTransactionReceipt",
        params=[tx_hash]
    )

    assert tx_receipt
    assert tx_receipt['transactionHash'] == tx_hash
