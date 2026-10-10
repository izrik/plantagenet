import plantagenet
from plantagenet import app


def test_admin_unauthenticated_returns_401(cl):
    response = cl.get('/admin')
    assert response.status_code == 401


def test_admin_authenticated_returns_200(cl, login):
    login()
    response = cl.get('/admin')
    assert response.status_code == 200


def test_admin_shows_current_sitename(cl, login):
    app.db.session.add(plantagenet.Option('sitename', 'My Blog'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'My Blog' in response.data


def test_admin_post_updates_sitename(cl, login):
    login()
    response = cl.post('/admin',
                       data={'sitename': 'New Name', 'new_password': ''})
    assert response.status_code == 302

    assert plantagenet.Options.get('sitename') == 'New Name'


def test_admin_post_updates_password(cl, login):
    login()
    cl.post('/admin', data={'sitename': '', 'new_password': 'secret123'})

    stored = plantagenet.Options.get('hashed_password')
    assert stored is not None
    assert plantagenet.bcrypt.check_password_hash(stored, 'secret123')


def test_admin_post_ignores_empty_sitename(cl, login):
    app.db.session.add(plantagenet.Option('sitename', 'Original'))
    app.db.session.commit()

    login()
    cl.post('/admin', data={'sitename': '', 'new_password': ''})

    assert plantagenet.Options.get('sitename') == 'Original'


def test_admin_post_ignores_empty_password(cl, login):
    app.db.session.add(plantagenet.Option('hashed_password', 'oldhash'))
    app.db.session.commit()

    login()
    cl.post('/admin', data={'sitename': '', 'new_password': '',
                            'extra_links': ''})

    assert plantagenet.Options.get('hashed_password') == 'oldhash'


def test_admin_shows_current_extra_links(cl, login):
    app.db.session.add(plantagenet.Option('extra_links',
                                          'About:/pages/about.html'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'About:/pages/about.html' in response.data


def test_admin_post_updates_extra_links(cl, login):
    login()
    cl.post('/admin', data={'sitename': '', 'new_password': '',
                            'extra_links': 'About:/pages/about.html'})

    assert plantagenet.Options.get('extra_links') == 'About:/pages/about.html'


def test_admin_post_clears_extra_links_when_empty(cl, login):
    app.db.session.add(plantagenet.Option('extra_links', 'About:/about'))
    app.db.session.commit()

    login()
    cl.post('/admin', data={'sitename': '', 'new_password': '',
                            'extra_links': ''})

    assert plantagenet.Options.get('extra_links') == ''


def test_admin_shows_current_copyright(cl, login):
    app.db.session.add(plantagenet.Option('copyright', '2012 - 2026'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'2012 - 2026' in response.data


def test_admin_post_updates_copyright(cl, login):
    login()
    cl.post('/admin', data={'sitename': '', 'new_password': '',
                            'extra_links': '', 'copyright': '2012 - 2026'})

    assert plantagenet.Options.get('copyright') == '2012 - 2026'


def test_admin_shows_copyright_warning_when_year_missing(cl, login):
    from datetime import datetime
    current_year = str(datetime.now().year)
    old_year = str(int(current_year) - 1)

    app.db.session.add(plantagenet.Option('copyright', f'2012 - {old_year}'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'Warning' in response.data


def test_admin_no_copyright_warning_when_year_present(cl, login):
    from datetime import datetime
    current_year = str(datetime.now().year)

    app.db.session.add(
        plantagenet.Option('copyright', f'2012 - {current_year}'))
    app.db.session.commit()

    login()
    response = cl.get('/admin')
    assert b'Warning' not in response.data


def test_footer_shows_copyright_string(cl):
    app.db.session.add(plantagenet.Option('copyright', '2012 - 2026'))
    app.db.session.commit()

    response = cl.get('/')
    assert b'2012 - 2026' in response.data
