from testrpc.client.utils import (
    encode_number,
)


def test_eth_gasprice(accounts, rpc_client):
    result = rpc_client('eth_gasPrice')
    assert result == "0x1"
