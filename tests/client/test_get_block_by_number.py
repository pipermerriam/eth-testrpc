def test_get_block_with_no_transactions(client, accounts):
    client.wait_for_block(1)

    block = client.get_block_by_number(1)

    assert block['number'] == b"0x1"
    assert block['miner'] == accounts[0]
    assert len(block['transactions']) == 0


def test_get_block_with_transactions(client, accounts):
    tx_hash = client.send_transaction(
        _from=accounts[0],
        to=accounts[1],
        value=1234,
        data="0x1234",
        gas=100000,
    )
    tx_receipt = client.get_transaction_receipt(tx_hash)

    assert tx_receipt
    assert tx_receipt['transactionHash'] == tx_hash

    block_number = tx_receipt['blockNumber']

    block = client.get_block_by_number(block_number)

    assert len(block['transactions']) == 1
