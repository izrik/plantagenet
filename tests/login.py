import plantagenet
from plantagenet import app


def _set_password(password):
    hashed = plantagenet.hash_password(password).decode()
    opt = plantagenet.Option('hashed_password', hashed)
    app.db.session.add(opt)
    app.db.session.commit()


def test_login_get_returns_200(cl):
    response = cl.get('/login')
    assert response.status_code == 200


def test_login_post_no_password_option_raises_503(cl):
    response = cl.post('/login', data={'password': 'test'})
    assert response.status_code == 503


def test_login_post_empty_stored_password_raises_503(cl):
    opt = plantagenet.Option('hashed_password', '')
    app.db.session.add(opt)
    app.db.session.commit()
    response = cl.post('/login', data={'password': 'test'})
    assert response.status_code == 503


def test_login_post_wrong_password_redirects_to_login(cl):
    _set_password('correct')
    response = cl.post('/login', data={'password': 'wrong'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_post_correct_password_redirects_to_index(cl):
    _set_password('correct')
    response = cl.post('/login', data={'password': 'correct'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_redirects_to_index(cl, login):
    login()
    response = cl.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_unauthenticated_redirects(cl):
    response = cl.get('/logout')
    assert response.status_code == 302
