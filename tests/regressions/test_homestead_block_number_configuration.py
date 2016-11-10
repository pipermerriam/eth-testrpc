from testrpc.client import EthTesterClient


def test_homestead_block_defaults_to_0():
    client = EthTesterClient()
    assert client.evm.block.config['HOMESTEAD_FORK_BLKNUM'] == 0

    client.mine_block()
    client.mine_block()

    assert client.evm.block.config['HOMESTEAD_FORK_BLKNUM'] == 0


def test_dao_fork_block_defaults_to_0():
    client = EthTesterClient()
    assert client.evm.block.config['DAO_FORK_BLKNUM'] == 0

    client.mine_block()
    client.mine_block()

    assert client.evm.block.config['DAO_FORK_BLKNUM'] == 0
