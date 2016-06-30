import time
import pytest

from ethereum import tester
from eth_tester_client.utils import mk_random_privkey


def test_import_raw_key(client):
    pk = mk_random_privkey()

    initial_accounts = client.get_accounts()

    address = client.import_raw_key(pk, 'some-password')

    assert address not in initial_accounts
    assert address in client.get_accounts()


def test_new_account(client):
    initial_accounts = client.get_accounts()

    address = client.new_account("some-password")

    assert address
    assert address not in initial_accounts
    assert address in client.get_accounts()

    assert not client.unlocked_account(address, "wrong-password")
    assert client.unlocked_account(address, "some-password")


def test_cannot_send_with_locked_account(client, accounts):
    sender = client.new_account("some-password")

    amt = 1000000000000

    # fund account
    client.send_transaction(_from=accounts[0], to=sender, value=amt)
    balance = client.get_balance(sender)
    assert balance >= amt

    with pytest.raises(ValueError):
        client.send_transaction(_from=sender, to=accounts[1], value=12345)

    # ensure balance didn't change
    assert balance == client.get_balance(sender)


def test_send_with_unlocked_account(client, accounts):
    sender = client.new_account("some-password")

    # fund account
    amt = 1000000000000
    client.send_transaction(_from=accounts[0], to=sender, value=amt)
    assert client.get_balance(sender) >= amt

    assert client.unlocked_account(sender, "some-password")

    before_bal = client.get_balance(accounts[1])

    client.send_transaction(_from=sender, to=accounts[1], value=12345)

    after_bal = client.get_balance(accounts[1])

    assert after_bal == before_bal + 12345


def test_locking_an_unlocked_account(client, accounts):
    sender = client.new_account("some-password")

    # fund account
    amt = 1000000000000
    client.send_transaction(_from=accounts[0], to=sender, value=amt)
    assert client.get_balance(sender) >= amt

    assert client.unlocked_account(sender, "some-password")

    client.send_transaction(_from=sender, to=accounts[1], value=12345)

    assert client.lock_account(sender)

    with pytest.raises(ValueError):
        client.send_transaction(_from=sender, to=accounts[1], value=12345)


def test_unlock_with_duration(client, accounts):
    sender = client.new_account("some-password")

    # fund account
    amt = 1000000000000
    client.send_transaction(_from=accounts[0], to=sender, value=amt)
    assert client.get_balance(sender) >= amt

    assert client.unlocked_account(sender, "some-password", 1)

    client.send_transaction(_from=sender, to=accounts[1], value=12345)

    time.sleep(1)

    with pytest.raises(ValueError):
        client.send_transaction(_from=sender, to=accounts[1], value=12345)


def test_send_and_sign_transaction(client, accounts):
    sender = client.new_account("some-password")

    # fund account
    amt = 1000000000000
    client.send_transaction(_from=accounts[0], to=sender, value=amt)
    assert client.get_balance(sender) >= amt

    before_bal = client.get_balance(accounts[1])

    client.send_and_sign_transaction(
        "some-password",
        _from=sender,
        to=accounts[1],
        value=12345,
    )

    after_bal = client.get_balance(accounts[1])

    assert after_bal == before_bal + 12345
