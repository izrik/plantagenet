from datetime import datetime

import plantagenet
from plantagenet import app


def test_list_pages_returns_200(cl):
    response = cl.get('/page')
    assert response.status_code == 200


def test_list_pages_shows_published_page(cl):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page')
    assert b'My Page' in response.data


def test_list_pages_hides_draft_from_unauthenticated(cl):
    page = plantagenet.Page('Secret Page', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page')
    assert b'Secret Page' not in response.data


def test_list_pages_shows_draft_to_authenticated(cl, login):
    page = plantagenet.Page('Secret Page', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    login()
    response = cl.get('/page')
    assert b'Secret Page' in response.data
