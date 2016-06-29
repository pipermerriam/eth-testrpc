def test_eth_blockNumber(accounts, rpc_client):
    assert rpc_client('eth_blockNumber') == "0x0"

    rpc_client('evm_mine')

    assert rpc_client('eth_blockNumber') == "0x1"

    rpc_client('evm_mine')
    rpc_client('evm_mine')
    rpc_client('evm_mine')

    assert rpc_client('eth_blockNumber') == "0x4"
