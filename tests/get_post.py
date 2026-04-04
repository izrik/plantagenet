from datetime import datetime

import plantagenet
from plantagenet import app


def test_get_post_returns_200(cl):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/post/{}'.format(post.slug))
    assert response.status_code == 200


def test_get_post_404_for_missing(cl):
    response = cl.get('/post/nonexistent')
    assert response.status_code == 404


def test_get_post_401_for_draft_unauthenticated(cl):
    post = plantagenet.Post('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/post/{}'.format(post.slug))
    assert response.status_code == 401


def test_get_post_shows_draft_to_authenticated(cl, login):
    post = plantagenet.Post('Draft', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()

    login()
    response = cl.get('/post/{}'.format(post.slug))
    assert response.status_code == 200


def test_get_post_shows_prev_next_when_authenticated(cl, login):
    post1 = plantagenet.Post('Post 1', 'c1', datetime(2024, 1, 1))
    post2 = plantagenet.Post('Post 2', 'c2', datetime(2024, 2, 1))
    post3 = plantagenet.Post('Post 3', 'c3', datetime(2024, 3, 1))
    app.db.session.add_all([post1, post2, post3])
    app.db.session.commit()

    login()
    response = cl.get('/post/{}'.format(post2.slug))
    assert response.status_code == 200
    assert b'post-1' in response.data
    assert b'post-3' in response.data


def test_get_post_shows_prev_next_unauthenticated(cl):
    post1 = plantagenet.Post('Post 1', 'c1', datetime(2024, 1, 1))
    post2 = plantagenet.Post('Post 2', 'c2', datetime(2024, 2, 1))
    post3 = plantagenet.Post('Post 3', 'c3', datetime(2024, 3, 1))
    app.db.session.add_all([post1, post2, post3])
    app.db.session.commit()

    response = cl.get('/post/{}'.format(post2.slug))
    assert response.status_code == 200
