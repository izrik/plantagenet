from datetime import datetime

import plantagenet
from plantagenet import app


def test_published_date_none_for_draft(ctx):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    assert page.published_date is None


def test_published_date_set_on_create_when_not_draft(cl, login):
    login()
    cl.post('/new-page', data={
        'title': 'My Page',
        'content': 'content',
        'notes': '',
    })
    page = app.db.session.execute(
        plantagenet.db.select(plantagenet.Page)).scalar()
    assert page.published_date is not None


def test_published_date_not_set_on_create_when_draft(cl, login):
    login()
    cl.post('/new-page', data={
        'title': 'My Page',
        'content': 'content',
        'notes': '',
        'is_draft': 'on',
    })
    page = app.db.session.execute(
        plantagenet.db.select(plantagenet.Page)).scalar()
    assert page.published_date is None


def test_published_date_set_when_draft_is_published(cl, login):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1),
                            is_draft=True)
    app.db.session.add(page)
    app.db.session.commit()
    assert page.published_date is None

    login()
    cl.post('/page/{}/edit'.format(page.slug), data={
        'title': page.title,
        'content': page.content,
        'notes': '',
    })
    app.db.session.refresh(page)
    assert page.published_date is not None


def test_published_date_not_overwritten_on_re_save(cl, login):
    original_date = datetime(2020, 6, 15)
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    page.published_date = original_date
    app.db.session.add(page)
    app.db.session.commit()

    login()
    cl.post('/page/{}/edit'.format(page.slug), data={
        'title': page.title,
        'content': 'updated content',
        'notes': '',
    })
    app.db.session.refresh(page)
    assert page.published_date == original_date
