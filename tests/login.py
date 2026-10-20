from datetime import datetime

import plantagenet
from plantagenet import app


def test_login_get_returns_200(cl):
    response = cl.get('/login')
    assert response.status_code == 200


def test_login_post_no_users_raises_503(cl):
    response = cl.post('/login', data={'email': 'nobody@example.com',
                                       'password': 'password123'})
    assert response.status_code == 503


def test_login_post_unknown_email_redirects_to_login(cl, regular_user):
    response = cl.post('/login', data={'email': 'nobody@example.com',
                                       'password': 'password123'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_post_wrong_password_redirects_to_login(cl, regular_user):
    response = cl.post('/login', data={'email': regular_user.email,
                                       'password': 'wrong'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_post_missing_email_redirects_to_login(cl, regular_user):
    response = cl.post('/login', data={'password': 'password123'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_post_correct_credentials_redirects_to_index(cl, regular_user):
    response = cl.post('/login', data={'email': regular_user.email,
                                       'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_login_post_correct_credentials_authenticates(cl, regular_user):
    cl.post('/login', data={'email': regular_user.email,
                            'password': 'password123'})
    with cl.session_transaction() as sess:
        assert sess['_user_id'] == str(regular_user.id)


def test_login_post_email_of_other_user_does_not_match(cl, make_user):
    make_user('one@example.com', password='password111')
    make_user('two@example.com', password='password222')
    response = cl.post('/login', data={'email': 'one@example.com',
                                       'password': 'password222'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_get_renders_next_url_in_form(cl):
    response = cl.get('/login?next=/page/some-page')
    assert response.status_code == 200
    assert b'name="next" value="/page/some-page"' in response.data


def test_login_get_ignores_non_local_next_url(cl):
    response = cl.get('/login?next=http://example.com/evil')
    assert response.status_code == 200
    assert b'name="next"' not in response.data


def test_login_post_returns_to_next_url(cl, regular_user):
    response = cl.post('/login',
                       data={'email': regular_user.email,
                             'password': 'password123', 'next': '/tags'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/tags'


def test_login_post_ignores_non_local_next_url(cl, regular_user):
    response = cl.post(
        '/login',
        data={'email': regular_user.email, 'password': 'password123',
              'next': 'http://example.com/evil'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_login_post_ignores_next_url_of_login_page(cl, regular_user):
    response = cl.post('/login',
                       data={'email': regular_user.email,
                             'password': 'password123', 'next': '/login'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_login_post_wrong_password_keeps_next_url(cl, regular_user):
    response = cl.post('/login', data={'email': regular_user.email,
                                       'password': 'wrong', 'next': '/tags'})
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


def test_logout_ignores_next_url_of_the_users_page(cl, login):
    login()
    response = cl.get('/logout?next=/users')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_logout_ignores_next_url_of_the_account_page(cl, login):
    login()
    response = cl.get('/logout?next=/account')
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
