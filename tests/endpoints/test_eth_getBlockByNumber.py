def test_eth_getBlockByNumber(rpc_client):
    block_0 = rpc_client("eth_getBlockByNumber", [0, False])

    assert block_0

    assert block_0['number'] == "0x0"
