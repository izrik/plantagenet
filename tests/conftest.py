import pytest

from plantagenet import create_app, db


@pytest.fixture
def ctx():
    test_app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'TESTING': True,
    })
    c = test_app.app_context()
    c.push()
    db.create_all()
    yield test_app
    db.session.rollback()
    db.drop_all()
    c.pop()


@pytest.fixture
def cl(ctx):
    return ctx.test_client()


@pytest.fixture
def login(cl):
    def _login():
        with cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True
    return _login
