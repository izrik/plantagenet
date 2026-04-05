from datetime import datetime

import plantagenet
from plantagenet import app


def test_view_page_returns_200(cl):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page/{}'.format(page.slug))
    assert response.status_code == 200


def test_view_page_shows_content(cl):
    page = plantagenet.Page('My Page', 'Hello World', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page/{}'.format(page.slug))
    assert b'Hello World' in response.data


def test_view_page_missing_returns_404(cl):
    response = cl.get('/page/no-such-page')
    assert response.status_code == 404


def test_view_draft_page_unauthenticated_returns_401(cl):
    page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page/{}'.format(page.slug))
    assert response.status_code == 401


def test_view_draft_page_authenticated_returns_200(cl, login):
    page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    login()
    response = cl.get('/page/{}'.format(page.slug))
    assert response.status_code == 200
