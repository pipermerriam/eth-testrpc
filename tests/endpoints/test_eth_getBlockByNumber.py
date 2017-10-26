def test_eth_getBlockByNumber(rpc_client):
    block_0 = rpc_client("eth_getBlockByNumber", [0, False])

    assert block_0

    assert len(block_0['nonce']) == 2 + 2 * 8  # nonce is 8 bytes
    assert block_0['number'] == "0x0"
