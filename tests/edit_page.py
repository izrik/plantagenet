from datetime import datetime

import plantagenet
from plantagenet import app


def test_edit_page_get_returns_200(cl, login):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    login()
    response = cl.get('/page/{}/edit'.format(page.slug))
    assert response.status_code == 200


def test_edit_page_get_returns_401_unauthenticated(cl):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    response = cl.get('/page/{}/edit'.format(page.slug))
    assert response.status_code == 401


def test_edit_page_get_404_for_missing(cl, login):
    login()
    response = cl.get('/page/nonexistent/edit')
    assert response.status_code == 404


def test_edit_page_post_updates_page(cl, login):
    page = plantagenet.Page('My Page', 'old content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()
    slug = page.slug

    login()
    response = cl.post('/page/{}/edit'.format(slug), data={
        'title': 'My Page',
        'content': 'new content',
        'notes': '',
    })
    assert response.status_code == 302

    app.db.session.refresh(page)
    assert page.content == 'new content'


def test_edit_page_post_bad_title_raises_400(cl, login):
    page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page)
    app.db.session.commit()

    login()
    response = cl.post('/page/{}/edit'.format(page.slug), data={
        'title': '',
        'content': 'content',
        'notes': '',
    })
    assert response.status_code == 400


def test_edit_page_post_404_for_missing(cl, login):
    login()
    response = cl.post('/page/nonexistent/edit', data={
        'title': 'Title',
        'content': 'content',
        'notes': '',
    })
    assert response.status_code == 404


def test_create_new_page_get_returns_200(cl, login):
    login()
    response = cl.get('/new-page')
    assert response.status_code == 200


def test_create_new_page_get_returns_401_unauthenticated(cl):
    response = cl.get('/new-page')
    assert response.status_code == 401


def test_create_new_page_post_creates_page(cl, login):
    login()
    response = cl.post('/new-page', data={
        'title': 'New Page',
        'content': 'some content',
        'notes': '',
    })
    assert response.status_code == 302

    page = app.db.session.execute(
        plantagenet.db.select(plantagenet.Page)).scalar()
    assert page is not None
    assert page.title == 'New Page'


def test_create_new_page_post_bad_title_raises_400(cl, login):
    login()
    response = cl.post('/new-page', data={
        'title': '',
        'content': 'content',
        'notes': '',
    })
    assert response.status_code == 400


def test_create_new_page_post_returns_401_unauthenticated(cl):
    response = cl.post('/new-page', data={
        'title': 'New Page',
        'content': 'content',
        'notes': '',
    })
    assert response.status_code == 401
