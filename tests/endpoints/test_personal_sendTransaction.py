import pytest


def test_personal_sendTransaction(accounts, rpc_client, password_account, account_password):
    initial_balance = rpc_client('eth_getBalance', [accounts[1]])

    # confirm it fails with a bad password
    with pytest.raises(AssertionError):
        rpc_client('personal_sendTransaction', [{
            'from': password_account,
            'to': accounts[1],
            'value': 1234,
        }, "incorrect-password"])
    assert rpc_client('eth_getBalance', [accounts[1]]) == initial_balance

    rpc_client('personal_sendTransaction', [{
        'from': password_account,
        'to': accounts[1],
        'value': 1234,
    }, account_password])
    after_balance = rpc_client('eth_getBalance', [accounts[1]])

    assert after_balance - initial_balance == 1234
