import pytest


@pytest.fixture(scope="session")
def accounts():
    from ethereum import tester
    from rlp.utils import encode_hex
    return [b"0x" + encode_hex(acct) for acct in tester.accounts]


@pytest.fixture
def client():
    from eth_tester_client import EthTesterClient
    return EthTesterClient()
