from datetime import datetime

import pytest
from werkzeug.exceptions import NotFound

import plantagenet
from plantagenet import app

pytestmark = pytest.mark.usefixtures('ctx')


def test_reset_slug():
    # given a post with a non-standard slug is put into the db
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
    post.slug = 'slug12345'
    app.db.session.add(post)
    app.db.session.commit()

    # precondition: the post is in the db
    assert post.id is not None
    post2 = plantagenet.Post.query.first()
    assert post2.id is not None
    assert post2 is post

    # precondition: the post's slug is different from the title
    assert post.slug != 'title'

    # when the reset_slug function is called
    plantagenet.reset_slug(post.id)

    # then the post's slug is changed to match the title (plus counter, meh)
    assert post.slug == post.title


def test_reset_slug_missing():
    # precondition: no posts are in the db
    result = plantagenet.Post.query.first()
    assert result is None

    # when the function is called with the id of a nonexistent post,
    # then an exception is thrown
    with pytest.raises(NotFound):
        plantagenet.reset_slug(1)
