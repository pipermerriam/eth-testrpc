import pytest

from eth_tester_client.utils import (
    normalize_address,
    mk_random_privkey,
)


def test_personal_lockAccount(accounts, rpc_client, password_account, account_password):
    assert rpc_client('personal_unlockAccount', [password_account, account_password])

    initial_balance = rpc_client('eth_getBalance', [accounts[1]])

    # confirm it's unlocked
    rpc_client('eth_sendTransaction', [{
        'from': password_account,
        'to': accounts[1],
        'value': 1234,
    }])
    after_balance = rpc_client('eth_getBalance', [accounts[1]])

    assert after_balance - initial_balance == 1234

    assert rpc_client('personal_lockAccount', [password_account])

    # sanity check
    before_balance = rpc_client('eth_getBalance', [accounts[2]])

    with pytest.raises(AssertionError):
        # confirm it's now locked
        rpc_client('eth_sendTransaction', [{
            'from': password_account,
            'to': accounts[2],
            'value': 1234,
        }])

    # sanity check
    assert rpc_client('eth_getBalance', [accounts[2]]) == before_balance
