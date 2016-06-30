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


def test_cannot_send_with_locked_account(client):
    assert False


def test_send_with_unlocked_account(client):
    assert False


def test_locking_an_unlocked_account(client):
    assert False


def test_unlock_with_duration(client):
    assert False
