import pytest
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

import plantagenet

pytestmark = pytest.mark.usefixtures('ctx')


def test_cmd_create_user_creates_a_regular_user():
    user = plantagenet.cmd_create_user('alice@example.com', 'Alice',
                                       password='password123')

    assert user.id is not None
    assert user.email == 'alice@example.com'
    assert user.name == 'Alice'
    assert user.is_admin is False
    assert user.check_password('password123')


def test_cmd_create_user_creates_an_admin():
    user = plantagenet.cmd_create_user('alice@example.com', is_admin=True,
                                       password='password123')

    assert user.is_admin is True
    assert user.name == 'alice@example.com'


def test_cmd_create_user_strips_the_email():
    user = plantagenet.cmd_create_user('  alice@example.com  ',
                                       password='password123')

    assert user.email == 'alice@example.com'


def test_cmd_create_user_invalid_email_raises():
    with pytest.raises(BadRequest):
        plantagenet.cmd_create_user('not-an-email', password='password123')


def test_cmd_create_user_short_password_raises():
    with pytest.raises(BadRequest):
        plantagenet.cmd_create_user('alice@example.com', password='short')
    assert plantagenet.User.get_by_email('alice@example.com') is None


def test_cmd_create_user_duplicate_email_raises(make_user):
    make_user('alice@example.com')
    with pytest.raises(BadRequest):
        plantagenet.cmd_create_user('alice@example.com',
                                    password='password123')


def test_cmd_create_user_prompts_for_the_password(monkeypatch):
    monkeypatch.setattr(plantagenet, 'getpass',
                        lambda prompt: 'password123')
    user = plantagenet.cmd_create_user('alice@example.com')

    assert user.check_password('password123')


def test_cmd_create_user_mismatched_passwords_raise(monkeypatch):
    answers = iter(['password123', 'password456'])
    monkeypatch.setattr(plantagenet, 'getpass',
                        lambda prompt: next(answers))
    with pytest.raises(BadRequest):
        plantagenet.cmd_create_user('alice@example.com')


def test_cmd_set_user_password_changes_it(make_user):
    user = make_user('alice@example.com')
    plantagenet.cmd_set_user_password('alice@example.com',
                                      password='newpassword')

    assert plantagenet.User.get(user.id).check_password('newpassword')


def test_cmd_set_user_password_prompts(monkeypatch, make_user):
    user = make_user('alice@example.com')
    monkeypatch.setattr(plantagenet, 'getpass',
                        lambda prompt: 'newpassword')
    plantagenet.cmd_set_user_password('alice@example.com')

    assert plantagenet.User.get(user.id).check_password('newpassword')


def test_cmd_set_user_password_unknown_email_raises():
    with pytest.raises(NotFound):
        plantagenet.cmd_set_user_password('nobody@example.com',
                                          password='password123')


def test_cmd_set_user_password_short_password_raises(make_user):
    user = make_user('alice@example.com')
    with pytest.raises(BadRequest):
        plantagenet.cmd_set_user_password('alice@example.com',
                                          password='short')
    assert plantagenet.User.get(user.id).check_password('password123')


def test_cmd_list_users_empty(capsys):
    assert plantagenet.cmd_list_users() == []
    assert 'No users found' in capsys.readouterr().out


def test_cmd_list_users(capsys, make_user):
    make_user('alice@example.com', 'Alice', is_admin=True)
    make_user('bob@example.com', 'Bob')

    users = plantagenet.cmd_list_users()
    assert [u.email for u in users] == ['alice@example.com',
                                        'bob@example.com']

    out = capsys.readouterr().out
    assert 'alice@example.com' in out
    assert 'bob@example.com' in out


def test_run_user_command_reports_a_bad_request(capsys):
    with pytest.raises(SystemExit):
        plantagenet.run_user_command(plantagenet.cmd_create_user,
                                     'not-an-email', password='password123')

    assert 'not a valid email address' in capsys.readouterr().out


def test_run_user_command_returns_the_result():
    # this runs against the module-level app, not the test fixture's
    result = plantagenet.run_user_command(plantagenet.cmd_list_users)
    assert isinstance(result, list)
