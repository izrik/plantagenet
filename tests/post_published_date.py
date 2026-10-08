from datetime import datetime

import plantagenet
from plantagenet import app


def test_published_date_none_for_draft(ctx):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    assert post.published_date is None


def test_published_date_set_on_create_when_not_draft(cl, login):
    login()
    cl.post('/new', data={
        'title': 'My Post',
        'content': 'content',
        'notes': '',
        'tags': '',
    })
    post = app.db.session.execute(
        plantagenet.db.select(plantagenet.Post)).scalar()
    assert post.published_date is not None
    assert post.published_date == post.date


def test_published_date_not_set_on_create_when_draft(cl, login):
    login()
    cl.post('/new', data={
        'title': 'My Post',
        'content': 'content',
        'notes': '',
        'tags': '',
        'is_draft': 'on',
    })
    post = app.db.session.execute(
        plantagenet.db.select(plantagenet.Post)).scalar()
    assert post.published_date is None


def test_published_date_set_when_draft_is_published(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()
    assert post.published_date is None

    login()
    cl.post('/edit/{}'.format(post.slug), data={
        'title': post.title,
        'content': post.content,
        'notes': '',
        'tags': '',
    })
    app.db.session.refresh(post)
    assert post.published_date is not None
    assert post.published_date > datetime(2024, 1, 1)


def test_published_date_not_overwritten_on_re_save(cl, login):
    original_date = datetime(2020, 6, 15)
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1))
    post.published_date = original_date
    app.db.session.add(post)
    app.db.session.commit()

    login()
    cl.post('/edit/{}'.format(post.slug), data={
        'title': post.title,
        'content': 'updated content',
        'notes': '',
        'tags': '',
    })
    app.db.session.refresh(post)
    assert post.published_date == original_date


def test_published_date_kept_when_post_reverted_to_draft(cl, login):
    original_date = datetime(2020, 6, 15)
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1))
    post.published_date = original_date
    app.db.session.add(post)
    app.db.session.commit()

    login()
    cl.post('/edit/{}'.format(post.slug), data={
        'title': post.title,
        'content': post.content,
        'notes': '',
        'tags': '',
        'is_draft': 'on',
    })
    app.db.session.refresh(post)
    assert post.is_draft
    assert post.published_date == original_date


def test_display_date_is_created_date_for_draft(ctx):
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1),
                            is_draft=True)
    post.published_date = datetime(2021, 1, 1)
    assert post.display_date == datetime(2020, 1, 1)


def test_display_date_is_published_date_for_published_post(ctx):
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1))
    post.published_date = datetime(2021, 1, 1)
    assert post.display_date == datetime(2021, 1, 1)


def test_display_date_falls_back_to_created_date(ctx):
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1))
    assert post.published_date is None
    assert post.display_date == datetime(2020, 1, 1)


def test_index_shows_published_date(cl):
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1))
    post.published_date = datetime(2021, 3, 4)
    app.db.session.add(post)
    app.db.session.commit()
    rv = cl.get('/')
    assert b'2021-03-04' in rv.data
    assert b'2020-01-01' not in rv.data


def test_get_post_shows_created_date_for_draft(cl, login):
    post = plantagenet.Post('My Post', 'content', datetime(2020, 1, 1),
                            is_draft=True)
    app.db.session.add(post)
    app.db.session.commit()
    login()
    rv = cl.get('/post/{}'.format(post.slug))
    assert b'on 2020-01-01' in rv.data
