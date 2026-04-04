import plantagenet
from plantagenet import app


def test_create_new_get_returns_200(cl, login):
    login()
    response = cl.get('/new')
    assert response.status_code == 200


def test_create_new_get_returns_401_unauthenticated(cl):
    response = cl.get('/new')
    assert response.status_code == 401


def test_create_new_post_creates_post(cl, login):
    login()
    response = cl.post('/new', data={
        'title': 'New Post',
        'content': 'some content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 302

    post = app.db.session.execute(
        plantagenet.db.select(plantagenet.Post)).scalar()
    assert post is not None
    assert post.title == 'New Post'


def test_create_new_post_bad_title_raises_400(cl, login):
    login()
    response = cl.post('/new', data={
        'title': '',
        'content': 'content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 400


def test_create_new_post_returns_401_unauthenticated(cl):
    response = cl.post('/new', data={
        'title': 'New Post',
        'content': 'content',
        'notes': '',
        'tags': '',
    })
    assert response.status_code == 401


def test_create_new_post_with_draft(cl, login):
    login()
    cl.post('/new', data={
        'title': 'Draft Post',
        'content': 'content',
        'notes': '',
        'tags': '',
        'is_draft': 'on',
    })

    post = app.db.session.execute(
        plantagenet.db.select(plantagenet.Post)).scalar()
    assert post.is_draft is True


def test_create_new_post_with_tags(cl, login):
    login()
    cl.post('/new', data={
        'title': 'Tagged Post',
        'content': 'content',
        'notes': '',
        'tags': 'python, flask',
    })

    post = app.db.session.execute(
        plantagenet.db.select(plantagenet.Post)).scalar()
    tag_names = {t.name for t in post.tags}
    assert 'python' in tag_names
    assert 'flask' in tag_names
