def test_personal_newAccount(rpc_client):
    initial_accounts = rpc_client('personal_listAccounts')

    new_account = rpc_client('personal_newAccount', ['some-password'])

    assert new_account not in initial_accounts
    assert new_account in rpc_client('personal_listAccounts')
