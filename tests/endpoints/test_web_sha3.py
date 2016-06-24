def test_web_sha3(rpc_client):
    result = rpc_client(method='web3_sha3', params=[''])
    assert result == '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

