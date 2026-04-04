import pytest

from plantagenet import app


@pytest.fixture
def ctx():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    app.testing = True
    c = app.app_context()
    c.push()
    app.db.create_all()
    yield
    app.db.session.rollback()
    app.db.drop_all()
    c.pop()


@pytest.fixture
def cl(ctx):
    return app.test_client()


@pytest.fixture
def login(cl):
    def _login():
        with cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True
    return _login
