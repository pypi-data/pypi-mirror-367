from ingress.caddy import render


def test_render(proxy_map):
    actual = render(proxy_map)
    assert 'foo.0-main.de' in actual


def test_render_duplicates(proxy_map_with_duplicates):
    actual = render(proxy_map_with_duplicates)
    assert 'dup.0-main.de:80 {\n\trespond "duplicate ingress.host" 500' in actual
