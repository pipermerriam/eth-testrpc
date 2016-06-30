from eth_tester_client.utils import (
    normalize_address,
)


def test_personal_listAccounts(accounts, rpc_client):
    actual = rpc_client('personal_listAccounts')
    n_actual = {normalize_address(acct) for acct in actual}
    n_expected = {normalize_address(acct) for acct in accounts}

    assert n_actual == n_expected
