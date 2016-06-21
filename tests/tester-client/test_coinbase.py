def test_coinbase(client):
    assert client.get_coinbase() == b'0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1'
