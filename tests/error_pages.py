def test_404_returns_404(cl):
    response = cl.get('/nonexistent-route-xyz')
    assert response.status_code == 404


def test_404_shows_error_code(cl):
    response = cl.get('/nonexistent-route-xyz')
    assert b'404' in response.data


def test_404_contains_header(cl):
    response = cl.get('/nonexistent-route-xyz')
    assert b'navbar' in response.data


def test_404_contains_footer(cl):
    response = cl.get('/nonexistent-route-xyz')
    assert b'Powered by' in response.data


def test_404_contains_home_link(cl):
    response = cl.get('/nonexistent-route-xyz')
    assert b'home page' in response.data.lower()


def test_401_returns_401(cl):
    response = cl.get('/admin')
    assert response.status_code == 401


def test_401_shows_error_code(cl):
    response = cl.get('/admin')
    assert b'401' in response.data


def test_401_contains_header(cl):
    response = cl.get('/admin')
    assert b'navbar' in response.data
