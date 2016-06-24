def test_get_block_by_hash(client, accounts):
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

    block_hash = tx_receipt['blockHash']

    block = client.get_block_by_hash(block_hash)

    assert block['hash'] == block_hash
