from datetime import datetime

import pytest
import plantagenet
from plantagenet import app


def test_index_returns_200(cl):
    response = cl.get('/')
    assert response.status_code == 200


def test_index_shows_published_post(cl):
    post = plantagenet.Post('Published', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/')
    assert b'Published' in response.data


@pytest.mark.parametrize('authenticated,visible', [
    (False, False),
    (True, True),
])
def test_index_draft_visibility(cl, login, authenticated, visible):
    post = plantagenet.Post('Secret', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()

    if authenticated:
        login()
    response = cl.get('/')
    assert (b'Secret' in response.data) == visible
