import pytest

from plantagenet import create_app, db, User


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
def make_user(ctx):
    def _make_user(email='user@example.com', name=None,
                   password='password123', is_admin=False):
        user = User(email, name, password, is_admin)
        user.save()
        return user
    return _make_user


@pytest.fixture
def admin_user(make_user):
    return make_user('admin@example.com', 'Admin', is_admin=True)


@pytest.fixture
def regular_user(make_user):
    return make_user('user@example.com', 'User', is_admin=False)


@pytest.fixture
def login(cl, admin_user):
    def _login(user=None):
        user = admin_user if user is None else user
        with cl.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        return user
    return _login
