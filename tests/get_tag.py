from datetime import datetime

import pytest
import plantagenet
from plantagenet import app


def test_get_tag_returns_200(cl):
    tag = plantagenet.Tag('python')
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/tags/{}'.format(tag.id))
    assert response.status_code == 200


def test_get_tag_shows_post(cl):
    tag = plantagenet.Tag('python')
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/tags/{}'.format(tag.id))
    assert b'My Post' in response.data


@pytest.mark.parametrize('authenticated,visible', [
    (False, False),
    (True, True),
])
def test_get_tag_draft_visibility(cl, login, authenticated, visible):
    tag = plantagenet.Tag('python')
    post = plantagenet.Post('Secret', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    if authenticated:
        login()
    response = cl.get('/tags/{}'.format(tag.id))
    assert (b'Secret' in response.data) == visible
