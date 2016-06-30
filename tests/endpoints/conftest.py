import pytest


@pytest.fixture()
def account_password():
    return "a-password"


@pytest.fixture()
def account_private_key():
    from eth_tester_client.utils import mk_random_privkey
    return mk_random_privkey()


@pytest.fixture()
def account_public_key(account_private_key):
    from ethereum.utils import privtoaddr
    from eth_tester_client.utils import encode_address
    return encode_address(privtoaddr(account_private_key))


@pytest.fixture()
def password_account(rpc_client, accounts, account_password,
                     account_private_key, account_public_key):
    from eth_tester_client.utils import normalize_address
    address = rpc_client(
        'personal_importRawKey',
        [account_private_key, account_password],
    )
    assert normalize_address(address) == normalize_address(account_public_key)

    initial_balance = 1000000000000000000000  # 1,000 ether

    rpc_client('eth_sendTransaction', [{
        'from': accounts[0],
        'to': address,
        'value': initial_balance,
    }])

    assert rpc_client('eth_getBalance', [address]) == initial_balance
    return address
