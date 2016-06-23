import pytest


def test_get_receipt_for_unknown_tx(client):
    with pytest.raises(ValueError):
        client.get_transaction_receipt("0x0000000000000000000000000000000000000000000000000000000000000000")


def test_get_transaction_receipt(client, accounts):
    tx_hash = client.send_transaction(
        _from=accounts[0],
        to=accounts[1],
        value=1234,
        data="0x1234",
        gas=100000,
    )
    tx_receipt = client.get_transaction_receipt(tx_hash)

    assert tx_receipt
    assert tx_receipt['transactionHash'] == tx_hash
