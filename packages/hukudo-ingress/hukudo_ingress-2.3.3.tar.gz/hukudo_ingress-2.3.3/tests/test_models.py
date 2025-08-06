from ingress.models import ProxyMap, Proxy


def test_proxy_map(proxy_map):
    assert (
        str(proxy_map)
        == """
https://foo.0-main.de http://82eb654ad00b:8000
https://bar.0-main.de http://a4d8d436465b:5000
""".strip()
    )


def test_proxy_map_empty():
    x = ProxyMap.empty()
    assert str(x) == ''
    assert len(x.proxies) == 0


def test_proxy_map_duplicates(proxy_map_with_duplicates):
    assert proxy_map_with_duplicates.proxies == [Proxy(host='ok.0-main.de', target='foo', port=8000)]
    assert proxy_map_with_duplicates.duplicates == ['dup.0-main.de']
