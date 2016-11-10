import rlp

from ethereum import tester
from ethereum.transactions import Transaction

from testrpc.client.utils import encode_data


def test_eth_sendRawTransaction(accounts, rpc_client):
    tx = Transaction(0, tester.gas_price, tester.gas_limit, accounts[1], 1234, '')
    tx.sign(tester.keys[0])

    raw_tx = rlp.encode(tx)
    raw_tx_hex = encode_data(raw_tx)

    result = rpc_client('eth_sendRawTransaction', params=[raw_tx_hex])
    assert len(result) == 66
