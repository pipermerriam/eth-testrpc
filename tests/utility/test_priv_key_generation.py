from eth_tester_client.utils import mk_random_privkey


def test_priv_key_generation():
    for i in range(100):
        pk = mk_random_privkey()
        assert len(pk) == 32
