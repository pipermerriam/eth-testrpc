import pytest

from ethereum.utils import sha3

from testrpc.client.utils import (
    encode_number,
    encode_data,
    strip_0x,
)


@pytest.fixture()
def call_emitter_method(rpc_client, emitter_contract_address, accounts):
    def _call_emitter_method(method_signature, arguments=None):
        if arguments is None:
            arguments = []
        function_sig = encode_data(sha3(method_signature)[:4])
        data = function_sig + b''.join((strip_0x(encode_number(arg, 32)) for arg in arguments))
        assert len(data) == 2 + 8 + 64 * len(arguments)

        txn_hash = rpc_client(
            method="eth_sendTransaction",
            params=[{
                '_from': accounts[0],
                'to': emitter_contract_address,
                'data': data,
                'gas': 200000,
            }],
        )

        return txn_hash
    return _call_emitter_method
