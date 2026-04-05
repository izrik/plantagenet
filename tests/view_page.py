from datetime import datetime

import pytest
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


@pytest.mark.parametrize('authenticated,expected_status', [
    (False, 401),
    (True, 200),
])
def test_view_draft_page_access(cl, login, authenticated, expected_status):
    page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()

    if authenticated:
        login()
    response = cl.get('/page/{}'.format(page.slug))
    assert response.status_code == expected_status
