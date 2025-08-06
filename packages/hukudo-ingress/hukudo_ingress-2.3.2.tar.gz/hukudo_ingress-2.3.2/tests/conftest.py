import pytest

from ingress.models import ProxyMap, Proxy


@pytest.fixture
def proxies() -> list[Proxy]:
    return [
        Proxy('foo.0-main.de', '82eb654ad00b', 8000),
        Proxy('bar.0-main.de', 'a4d8d436465b', 5000),
    ]


@pytest.fixture
def proxy_map(proxies) -> ProxyMap:
    return ProxyMap(proxies)


@pytest.fixture
def proxy_map_with_duplicates() -> ProxyMap:
    return ProxyMap(
        [
            Proxy(host='ok.0-main.de', target='foo', port=8000),
            Proxy(host='dup.0-main.de', target='bar', port=8001),
            Proxy(host='dup.0-main.de', target='baz', port=8002),
        ]
    )
