def test_get_block_number(client):
    assert client.get_block_number() == 0

    client.wait_for_block(10)

    assert client.get_block_number() == 10
