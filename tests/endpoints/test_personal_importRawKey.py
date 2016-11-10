from testrpc.client.utils import (
    normalize_address,
    mk_random_privkey,
)


def test_personal_importRawKey(accounts, rpc_client):
    initial_accounts = rpc_client('personal_listAccounts')

    private_key = mk_random_privkey()

    new_account = rpc_client('personal_importRawKey', [private_key, 'a-password'])
    n_new_account = normalize_address(new_account)

    assert n_new_account in {normalize_address(acct) for acct in rpc_client('personal_listAccounts')}
    assert rpc_client('personal_unlockAccount', [new_account, 'a-password']) is True
