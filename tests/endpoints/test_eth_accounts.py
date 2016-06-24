from eth_tester_client.utils import (
    normalize_address,
)


def test_eth_accounts(accounts, rpc_client):
    actual = rpc_client('eth_accounts')
    n_actual = {normalize_address(acct) for acct in actual}
    n_expected = {normalize_address(acct) for acct in accounts}

    assert n_actual == n_expected
