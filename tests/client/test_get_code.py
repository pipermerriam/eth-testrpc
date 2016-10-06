from testrpc.client.utils import (
    force_bytes,
)


CONTRACT_BIN = b'0x6060604052610114806100126000396000f360606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461004f578063a5f3c23b14610072578063dcf537b1146100a75761004d565b005b61005c60048050506100d3565b6040518082815260200191505060405180910390f35b61009160048080359060200190919080359060200190919050506100e6565b6040518082815260200191505060405180910390f35b6100bd60048080359060200190919050506100fd565b6040518082815260200191505060405180910390f35b6000600d905080508090506100e3565b90565b6000818301905080508090506100f7565b92915050565b6000600782029050805080905061010f565b91905056'


CONTRACT_BIN_RUNTIME = b'0x60606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461004f578063a5f3c23b14610072578063dcf537b1146100a75761004d565b005b61005c60048050506100d3565b6040518082815260200191505060405180910390f35b61009160048080359060200190919080359060200190919050506100e6565b6040518082815260200191505060405180910390f35b6100bd60048080359060200190919050506100fd565b6040518082815260200191505060405180910390f35b6000600d905080508090506100e3565b90565b6000818301905080508090506100f7565b92915050565b6000600782029050805080905061010f565b91905056'

CONTRACT_SOURCE = (
"""contract Math {
    uint public counter;

    event Increased(uint value);

    function increment() public returns (uint) {
        return increment(1);
    }

    function increment(uint amt) public returns (uint result) {
        counter += amt;
        result = counter;
        Increased(result);
        return result;
    }

    function add(int a, int b) public returns (int result) {
        result = a + b;
        return result;
    }

    function multiply7(int a) public returns (int result) {
        result = a * 7;
        return result;
    }

    function return13() public returns (int result) {
        result = 13;
        return result;
    }
}""")


def test_get_code(client, accounts):
    txn_hash = client.send_transaction(
        _from=accounts[0],
        data=CONTRACT_BIN,
        value=1234,
    )
    txn_receipt = client.get_transaction_receipt(txn_hash)
    contract_address = txn_receipt['contractAddress']

    assert contract_address

    code = client.get_code(contract_address)
    assert force_bytes(code) == force_bytes(CONTRACT_BIN_RUNTIME)


def test_get_code_non_contract(client, accounts):
    code = client.get_code('0xd3cda913deb6f67967b99d67acdfa1712c293601')
    assert force_bytes(code) == b'0x'
