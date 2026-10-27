from datetime import datetime

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


def test_login_get_renders_next_url_in_form(cl):
    response = cl.get('/login?next=/page/some-page')
    assert response.status_code == 200
    assert b'name="next" value="/page/some-page"' in response.data


def test_login_get_ignores_non_local_next_url(cl):
    response = cl.get('/login?next=http://example.com/evil')
    assert response.status_code == 200
    assert b'name="next"' not in response.data


def test_login_post_returns_to_next_url(cl):
    _set_password('correct')
    response = cl.post('/login',
                       data={'password': 'correct', 'next': '/tags'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/tags'


def test_login_post_ignores_non_local_next_url(cl):
    _set_password('correct')
    response = cl.post(
        '/login',
        data={'password': 'correct', 'next': 'http://example.com/evil'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_login_post_ignores_next_url_of_login_page(cl):
    _set_password('correct')
    response = cl.post('/login',
                       data={'password': 'correct', 'next': '/login'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_login_post_wrong_password_keeps_next_url(cl):
    _set_password('correct')
    response = cl.post('/login', data={'password': 'wrong', 'next': '/tags'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/login?next=/tags'


def test_logout_redirects_to_index(cl, login):
    login()
    response = cl.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_returns_to_next_url(cl, login):
    login()
    response = cl.get('/logout?next=/tags')
    assert response.status_code == 302
    assert response.headers['Location'] == '/tags'


def test_logout_ignores_non_local_next_url(cl, login):
    login()
    response = cl.get('/logout?next=http://example.com/evil')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_ignores_next_url_that_requires_login(cl, login):
    login()
    response = cl.get('/logout?next=/admin')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_ignores_unknown_next_url(cl, login):
    login()
    response = cl.get('/logout?next=/no-such-page')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_returns_to_published_post(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    login()
    response = cl.get('/logout?next=/post/{}'.format(post.slug))
    assert response.status_code == 302
    assert response.headers['Location'] == '/post/{}'.format(post.slug)


def test_logout_ignores_next_url_of_draft_post(cl, login):
    post = plantagenet.Post('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()

    login()
    response = cl.get('/logout?next=/post/{}'.format(post.slug))
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_ignores_next_url_of_draft_page(cl, login):
    page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    login()
    response = cl.get('/logout?next=/page/{}'.format(page.slug))
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_unauthenticated_redirects(cl):
    response = cl.get('/logout')
    assert response.status_code == 302


def test_login_link_includes_current_url(cl):
    response = cl.get('/tags')
    assert response.status_code == 200
    assert b'href="/login?next=/tags"' in response.data


def test_login_link_includes_current_query_string(cl):
    response = cl.get('/tags?foo=bar')
    assert response.status_code == 200
    assert b'href="/login?next=/tags?foo%3Dbar"' in response.data


def test_logout_link_includes_current_url(cl, login):
    login()
    response = cl.get('/tags')
    assert response.status_code == 200
    assert b'href="/logout?next=/tags"' in response.data
