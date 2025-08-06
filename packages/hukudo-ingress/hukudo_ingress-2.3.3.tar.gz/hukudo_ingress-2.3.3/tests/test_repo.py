from ingress.repo import InMemoryRepo, PickleRepo


def test_in_memory(proxy_map):
    repo = InMemoryRepo()
    repo.save(proxy_map)
    assert repo.load() == proxy_map


def test_pickle(tmp_path, proxy_map):
    repo = PickleRepo(tmp_path / 'repo.dat')
    repo.save(proxy_map)

    assert repo.load() == proxy_map
