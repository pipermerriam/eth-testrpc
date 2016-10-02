
def test_eth_sendTransaction(rpc_client, accounts, hex_accounts):
    result = rpc_client(
        method="eth_sendTransaction",
        params=[{
            "from": accounts[0],
            "to": accounts[1],
            "value": 1234,
            "data": "0x1234",
            "gas": 100000,
            "gasPrice": 4321,
        }],
    )

    assert len(result) == 66

    txn = rpc_client(
        method="eth_getTransactionByHash",
        params=[result],
    )
    assert txn['from'] == hex_accounts[0]
    assert txn['to'] == hex_accounts[1]
    assert txn['value'] == hex(1234)
    assert txn['input'] == '0x1234'
    assert txn['gas'] == hex(100000)
    assert txn['gasPrice'] == hex(4321)


def test_eth_sendTransaction_with_hex_values(rpc_client, accounts, hex_accounts):
    result = rpc_client(
        method="eth_sendTransaction",
        params=[{
            "from": accounts[0],
            "to": accounts[1],
            "value": hex(1234),
            "data": "0x1234",
            "gas": hex(100000),
            "gasPrice": hex(4321),
        }],
    )

    assert len(result) == 66

    txn = rpc_client(
        method="eth_getTransactionByHash",
        params=[result],
    )
    assert txn['from'] == hex_accounts[0]
    assert txn['to'] == hex_accounts[1]
    assert txn['value'] == hex(1234)
    assert txn['input'] == '0x1234'
    assert txn['gas'] == hex(100000)
    assert txn['gasPrice'] == hex(4321)
