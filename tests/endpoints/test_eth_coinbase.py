from testrpc.client.utils import (
    normalize_address,
)


def test_eth_coinbase(accounts, rpc_client):
    result = rpc_client('eth_coinbase')
    assert normalize_address(result) == normalize_address(accounts[0])
