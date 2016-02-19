import pytest


@pytest.fixture
def client():
    from eth_tester_client import EthTesterClient
    return EthTesterClient()
