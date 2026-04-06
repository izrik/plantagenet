import pytest
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
    response = cl.post('/admin', data={'sitename': 'New Name', 'new_password': ''})
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
    cl.post('/admin', data={'sitename': '', 'new_password': ''})

    assert plantagenet.Options.get('hashed_password') == 'oldhash'
