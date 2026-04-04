from datetime import datetime

import plantagenet
from plantagenet import app


def test_edit_post_get_returns_200(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    login()
    response = cl.get('/edit/{}'.format(post.slug))
    assert response.status_code == 200


def test_edit_post_get_returns_401_unauthenticated(cl):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    response = cl.get('/edit/{}'.format(post.slug))
    assert response.status_code == 401


def test_edit_post_get_404_for_missing(cl, login):
    login()
    response = cl.get('/edit/nonexistent')
    assert response.status_code == 404


def test_edit_post_post_updates_post(cl, login):
    post = plantagenet.Post('My Post', 'old content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()
    slug = post.slug

    login()
    response = cl.post('/edit/{}'.format(slug), data={
        'title': 'My Post',
        'content': 'new content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 302

    app.db.session.refresh(post)
    assert post.content == 'new content'


def test_edit_post_post_bad_title_raises_400(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    login()
    response = cl.post('/edit/{}'.format(post.slug), data={
        'title': '',
        'content': 'content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 400


def test_edit_post_post_404_for_missing(cl, login):
    login()
    response = cl.post('/edit/nonexistent', data={
        'title': 'Title',
        'content': 'content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 404


def test_edit_post_adds_tags(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()

    login()
    cl.post('/edit/{}'.format(post.slug), data={
        'title': 'My Post',
        'content': 'content',
        'notes': '',
        'tags': 'python, flask',
    })

    app.db.session.refresh(post)
    tag_names = {t.name for t in post.tags}
    assert 'python' in tag_names
    assert 'flask' in tag_names


def test_edit_post_removes_tags(cl, login):
    tag = plantagenet.Tag('python')
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    login()
    cl.post('/edit/{}'.format(post.slug), data={
        'title': 'My Post',
        'content': 'content',
        'notes': '',
        'tags': '',
    })

    app.db.session.refresh(post)
    assert len(post.tags) == 0
