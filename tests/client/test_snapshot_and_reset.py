def test_resetting_evm(client):
    assert client.get_block_number() == 0

    client.wait_for_block(10)

    assert client.get_block_number() == 10

    client.reset_evm()

    assert client.get_block_number() == 0


def test_reverting_to_snapshot(client):
    assert client.get_block_number() == 0

    client.wait_for_block(10)

    assert client.get_block_number() == 10

    snapshot_idx = client.snapshot_evm()

    client.wait_for_block(20)

    assert client.get_block_number() == 20

    client.revert_evm(snapshot_idx)

    assert client.get_block_number() == 10
