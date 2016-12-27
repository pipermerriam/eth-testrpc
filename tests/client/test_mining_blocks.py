def test_mine_block(client):
    initial_block_number = client.get_block_number()

    client.mine_block()
    client.mine_block()

    assert client.get_block_number() - initial_block_number == 1

    client.mine_block()
    client.mine_block()
    client.mine_block()

    assert client.get_block_number() - initial_block_number == 4
