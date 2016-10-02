import pytest

from ethereum import tester


CONTRACT_BIN = b'0x6060604052610114806100126000396000f360606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461004f578063a5f3c23b14610072578063dcf537b1146100a75761004d565b005b61005c60048050506100d3565b6040518082815260200191505060405180910390f35b61009160048080359060200190919080359060200190919050506100e6565b6040518082815260200191505060405180910390f35b6100bd60048080359060200190919050506100fd565b6040518082815260200191505060405180910390f35b6000600d905080508090506100e3565b90565b6000818301905080508090506100f7565b92915050565b6000600782029050805080905061010f565b91905056'


CONTRACT_BIN_RUNTIME = b'0x60606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461004f578063a5f3c23b14610072578063dcf537b1146100a75761004d565b005b61005c60048050506100d3565b6040518082815260200191505060405180910390f35b61009160048080359060200190919080359060200190919050506100e6565b6040518082815260200191505060405180910390f35b6100bd60048080359060200190919050506100fd565b6040518082815260200191505060405180910390f35b6000600d905080508090506100e3565b90565b6000818301905080508090506100f7565b92915050565b6000600782029050805080905061010f565b91905056'


@pytest.mark.parametrize(
    'txn_kwargs',
    (
        {},
        {'to': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1'},
        {'_from': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1'},
    )
)
def test_send_transaction(client, txn_kwargs):
    kwargs = {
        '_from': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'to': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'value': 1,
    }
    kwargs.update(txn_kwargs)

    txn_hash = client.send_transaction(**kwargs)
    assert txn_hash


def test_default_gas_is_full_gas_limit(client):
    kwargs = {
        '_from': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'to': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'value': 1,
    }

    txn_hash = client.send_transaction(**kwargs)
    assert txn_hash

    txn = client.get_transaction_by_hash(txn_hash)
    txn_gas = int(txn['gas'], 16)
    assert txn_gas == tester.gas_limit


def test_can_specify_gas(client):
    kwargs = {
        '_from': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'to': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'value': 1,
        'gas': 123456,
    }
    initial_tester_gas_limit = tester.gas_limit

    txn_hash = client.send_transaction(**kwargs)
    assert txn_hash

    txn = client.get_transaction_by_hash(txn_hash)
    txn_gas = int(txn['gas'], 16)
    assert txn_gas != tester.gas_limit
    assert txn_gas == 123456
    assert tester.gas_limit == initial_tester_gas_limit


def test_can_specify_gas_price(client):
    kwargs = {
        '_from': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'to': b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1',
        'value': 1,
        'gas_price': 1234,
    }
    initial_tester_gas_price = tester.gas_price

    txn_hash = client.send_transaction(**kwargs)
    assert txn_hash

    txn = client.get_transaction_by_hash(txn_hash)
    txn_gas_price = int(txn['gasPrice'], 16)
    assert txn_gas_price != tester.gas_price
    assert txn_gas_price == 1234
    assert tester.gas_price == initial_tester_gas_price


def test_deploying_contract(client, accounts):
    txn_hash = client.send_transaction(
        _from=accounts[0],
        data=CONTRACT_BIN,
        value=1234,
    )
    txn_receipt = client.get_transaction_receipt(txn_hash)
    contract_address = txn_receipt['contractAddress']

    assert contract_address

    balance = client.get_balance(contract_address)
    assert balance == 1234

    code = client.get_code(contract_address)
    assert code == CONTRACT_BIN_RUNTIME
