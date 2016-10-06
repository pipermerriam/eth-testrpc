import rlp

from ethereum import tester
from ethereum.transactions import Transaction

from testrpc.client.utils import (
    encode_data,
)


def test_eth_sendRawTransaction(hex_accounts, client):
    tx = Transaction(0, tester.gas_price, tester.gas_limit, tester.accounts[1], 1234, '')
    tx.sign(tester.keys[0])

    raw_tx = rlp.encode(tx)
    raw_tx_hex = encode_data(raw_tx)

    tx_hash = client.send_raw_transaction(raw_tx_hex)
    assert tx_hash

    tx_data = client.get_transaction_by_hash(tx_hash)

    assert tx_data['hash'] == tx_hash
    assert tx_data['from'] == hex_accounts[0]
    assert tx_data['to'] == hex_accounts[1]
