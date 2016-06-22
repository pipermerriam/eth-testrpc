def test_eth_blockNumber(accounts, rpc_client):
    result = rpc_client('eth_blockNumber')
    assert result == "0x0"
