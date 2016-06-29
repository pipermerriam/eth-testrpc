def test_eth_getBlockByHash(rpc_client):
    block_0 = rpc_client("eth_getBlockByNumber", [0, False])

    block_0_by_hash = rpc_client("eth_getBlockByHash", [block_0['hash'], False])

    assert block_0_by_hash == block_0
