def test_get_earliest_block(client, hex_accounts):
    client.mine_block()
    client.mine_block()

    block = client.get_block_by_number("earliest")

    assert block['number'] == b'0x0'


def test_get_latest_block(client, hex_accounts):
    client.mine_block() # finalizes the genesis block
    client.mine_block() # finalizes block #1
    client.mine_block() # finalizes block #2

    block = client.get_block_by_number("latest")

    assert block['number'] == b'0x2'
    assert int(block['number'], 16) == client.get_block_number()


def test_get_pending_block(client, hex_accounts):
    client.mine_block() # finalizes the genesis block
    client.mine_block() # finalizes block #1
    client.mine_block() # finalizes block #2

    block = client.get_block_by_number("pending")

    assert block['number'] == b'0x3'
    assert int(block['number'], 16) == client.get_block_number() + 1
