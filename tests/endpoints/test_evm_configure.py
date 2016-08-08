def test_homestead_fork_block_number(rpc_client):
    tester_client = rpc_client.server.application.testrpc.tester_client
    assert tester_client.evm.block.config['HOMESTEAD_FORK_BLKNUM'] == 0

    rpc_client('rpc_configure', ['homestead_block_number', 10])
    rpc_client('evm_mine')

    assert tester_client.evm.block.config['HOMESTEAD_FORK_BLKNUM'] == 10


def test_dao_fork_block_number(rpc_client):
    tester_client = rpc_client.server.application.testrpc.tester_client
    assert tester_client.evm.block.config['DAO_FORK_BLKNUM'] == 0

    rpc_client('rpc_configure', ['dao_fork_block_number', 10])
    rpc_client('evm_mine')

    assert tester_client.evm.block.config['DAO_FORK_BLKNUM'] == 10
