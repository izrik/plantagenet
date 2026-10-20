import plantagenet
from plantagenet import app


def test_admin_unauthenticated_returns_401(cl):
    response = cl.get('/admin')
    assert response.status_code == 401


def test_admin_authenticated_returns_200(cl, login):
    login()
    response = cl.get('/admin')
    assert response.status_code == 200


def test_admin_non_admin_user_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.get('/admin')
    assert response.status_code == 403


def test_admin_post_non_admin_user_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.post('/admin', data={'sitename': 'New Name'})
    assert response.status_code == 403
    assert plantagenet.Options.get('sitename') is None


def test_admin_shows_current_sitename(cl, login):
    app.db.session.add(plantagenet.Option('sitename', 'My Blog'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'My Blog' in response.data


def test_admin_post_updates_sitename(cl, login):
    login()
    response = cl.post('/admin', data={'sitename': 'New Name'})
    assert response.status_code == 302

    assert plantagenet.Options.get('sitename') == 'New Name'


def test_admin_post_ignores_empty_sitename(cl, login):
    app.db.session.add(plantagenet.Option('sitename', 'Original'))
    app.db.session.commit()

    login()
    cl.post('/admin', data={'sitename': ''})

    assert plantagenet.Options.get('sitename') == 'Original'


def test_admin_shows_current_extra_links(cl, login):
    app.db.session.add(plantagenet.Option('extra_links',
                                          'About:/pages/about.html'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'About:/pages/about.html' in response.data


def test_admin_post_updates_extra_links(cl, login):
    login()
    cl.post('/admin', data={'sitename': '',
                            'extra_links': 'About:/pages/about.html'})

    assert plantagenet.Options.get('extra_links') == 'About:/pages/about.html'


def test_admin_post_clears_extra_links_when_empty(cl, login):
    app.db.session.add(plantagenet.Option('extra_links', 'About:/about'))
    app.db.session.commit()

    login()
    cl.post('/admin', data={'sitename': '', 'extra_links': ''})

    assert plantagenet.Options.get('extra_links') == ''
