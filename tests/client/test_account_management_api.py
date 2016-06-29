from ethereum import tester
from eth_tester_client.utils import mk_random_privkey


def test_import_raw_key(client):
    pk = mk_random_privkey

    assert pk not in tester.keys

    client.import_raw_key(pk)

    assert pk in tester.keys


def test_new_account(client):
    prev_account_list = client.accounts

    address = client.new_account("some-password")

    updated_account_list = client.accounts

    assert address
    assert address not in prev_account_list
    assert address in updated_account_list

    assert not client.unlocked_account(address, "wrong-password")
    assert client.unlocked_account(address, "some-password")


def test_cannot_send_with_locked_account(client):
    assert False


def test_send_with_unlocked_account(client):
    assert False


def test_locking_an_unlocked_account(client):
    assert False


def test_unlock_with_duration(client):
    assert False
