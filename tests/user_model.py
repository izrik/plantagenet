import pytest
from werkzeug.exceptions import BadRequest

import plantagenet


def test_user_defaults_name_to_email(ctx):
    user = plantagenet.User('alice@example.com')
    assert user.name == 'alice@example.com'
    assert user.get_name() == 'alice@example.com'


def test_user_is_not_admin_by_default(ctx):
    user = plantagenet.User('alice@example.com')
    assert user.is_admin is False


def test_user_set_password_hashes_it(ctx):
    user = plantagenet.User('alice@example.com', 'Alice', 'password123')
    assert user.hashed_password != 'password123'
    assert user.check_password('password123')


def test_user_check_password_wrong(ctx):
    user = plantagenet.User('alice@example.com', 'Alice', 'password123')
    assert not user.check_password('nope')


def test_user_check_password_without_a_password(ctx):
    user = plantagenet.User('alice@example.com', 'Alice')
    assert not user.check_password('password123')


def test_user_get_by_email(ctx, make_user):
    user = make_user('alice@example.com')
    assert plantagenet.User.get_by_email('alice@example.com') is user


def test_user_get_by_email_missing(ctx):
    assert plantagenet.User.get_by_email('nobody@example.com') is None


def test_user_get_by_id(ctx, make_user):
    user = make_user('alice@example.com')
    assert plantagenet.User.get(user.id) is user


def test_user_list_is_ordered_by_email(ctx, make_user):
    make_user('zoe@example.com')
    make_user('alice@example.com')
    emails = [u.email for u in plantagenet.User.list()]
    assert emails == ['alice@example.com', 'zoe@example.com']


def test_user_count(ctx, make_user):
    assert plantagenet.User.count() == 0
    make_user('alice@example.com')
    assert plantagenet.User.count() == 1


def test_user_count_admins(ctx, make_user):
    make_user('alice@example.com')
    make_user('bob@example.com', is_admin=True)
    assert plantagenet.User.count_admins() == 1


def test_user_delete(ctx, make_user):
    user = make_user('alice@example.com')
    user.delete()
    assert plantagenet.User.count() == 0


def test_user_validate_email_valid(ctx):
    plantagenet.User.validate_email('alice@example.com')


@pytest.mark.parametrize('email', ['', None, 'alice', 'alice@', '@example.com',
                                   'alice example@com', 'a@b@c'])
def test_user_validate_email_invalid(ctx, email):
    with pytest.raises(BadRequest):
        plantagenet.User.validate_email(email)


def test_user_validate_password_valid(ctx):
    plantagenet.User.validate_password('password123')


@pytest.mark.parametrize('password', ['', None, 'short'])
def test_user_validate_password_invalid(ctx, password):
    with pytest.raises(BadRequest):
        plantagenet.User.validate_password(password)


def test_load_user_returns_the_user(ctx, make_user):
    user = make_user('alice@example.com')
    assert plantagenet.load_user(str(user.id)) is user


def test_load_user_unknown_id_returns_none(ctx):
    assert plantagenet.load_user('12345') is None


def test_load_user_non_numeric_id_returns_none(ctx):
    assert plantagenet.load_user('admin') is None


def test_guest_is_not_an_admin(ctx):
    guest = plantagenet.Guest()
    assert guest.is_admin is False
    assert guest.is_authenticated is False
    assert guest.get_name() is None
