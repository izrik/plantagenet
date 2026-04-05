from datetime import datetime

import pytest
import plantagenet
from plantagenet import app


def test_list_tags_returns_200(cl):
    response = cl.get('/tags')
    assert response.status_code == 200


def test_list_tags_shows_tag_with_published_post(cl):
    tag = plantagenet.Tag('mytag')
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/tags')
    assert b'mytag' in response.data


@pytest.mark.parametrize('authenticated,visible', [
    (False, False),
    (True, True),
])
def test_list_tags_draft_post_visibility(cl, login, authenticated, visible):
    tag = plantagenet.Tag('drafttag')
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            is_draft=True)
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    if authenticated:
        login()
    response = cl.get('/tags')
    assert (b'drafttag' in response.data) == visible
