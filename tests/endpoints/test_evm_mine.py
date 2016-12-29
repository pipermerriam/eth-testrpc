def test_evm_mine(rpc_client):
    assert rpc_client('eth_blockNumber') == "0x0"

    rpc_client('evm_mine')
    rpc_client('evm_mine')

    assert rpc_client('eth_blockNumber') == "0x1"

    rpc_client('evm_mine')
    rpc_client('evm_mine')
    rpc_client('evm_mine')

    assert rpc_client('eth_blockNumber') == "0x4"


def test_evm_mine_with_num_blocks(rpc_client):
    assert rpc_client('eth_blockNumber') == "0x0"

    rpc_client('evm_mine', [2])

    assert rpc_client('eth_blockNumber') == "0x1"

    rpc_client('evm_mine', [3])

    assert rpc_client('eth_blockNumber') == "0x4"
