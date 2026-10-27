import types

import pytest

import plantagenet
from plantagenet import app


def _fake_args(**kwargs):
    defaults = dict(
        create_db=False,
        hash_password=None,
        count_posts=False,
        reset_slug=None,
        set_date=None,
        set_last_updated_date=None,
        reset_summary=None,
        set_option=None,
        clear_option=None,
        create_admin=None,
        create_user=None,
        set_user_password=None,
        list_users=False,
        name=None,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _set_args(monkeypatch, **kwargs):
    monkeypatch.setattr(plantagenet, 'args', _fake_args(**kwargs),
                        raising=False)


def test_run_create_db(ctx, monkeypatch):
    _set_args(monkeypatch, create_db=True)
    plantagenet.run()


def test_run_hash_password(ctx, monkeypatch):
    _set_args(monkeypatch, hash_password='mypassword')
    plantagenet.run()


def test_run_count_posts(ctx, monkeypatch):
    _set_args(monkeypatch, count_posts=True)
    plantagenet.run()


def test_run_reset_slug(ctx, monkeypatch):
    from datetime import datetime
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()
    _set_args(monkeypatch, reset_slug=str(post.id))
    plantagenet.run()


def test_run_reset_slug_not_found(ctx, monkeypatch):
    _set_args(monkeypatch, reset_slug='999')
    plantagenet.run()


def test_run_set_option_new(ctx, monkeypatch):
    _set_args(monkeypatch, set_option=('mykey', 'myvalue'))
    plantagenet.run()


def test_run_set_option_existing(ctx, monkeypatch):
    opt = plantagenet.Option('mykey', 'oldvalue')
    app.db.session.add(opt)
    app.db.session.commit()
    _set_args(monkeypatch, set_option=('mykey', 'newvalue'))
    plantagenet.run()


def test_run_clear_option(ctx, monkeypatch):
    opt = plantagenet.Option('mykey', 'value')
    app.db.session.add(opt)
    app.db.session.commit()
    _set_args(monkeypatch, clear_option='mykey')
    plantagenet.run()


def test_run_clear_option_not_found(ctx, monkeypatch):
    _set_args(monkeypatch, clear_option='nonexistent')
    with pytest.raises(SystemExit):
        plantagenet.run()


def test_run_create_admin(ctx, monkeypatch):
    monkeypatch.setattr(plantagenet, 'getpass', lambda prompt: 'password123')
    _set_args(monkeypatch, create_admin='cli-admin@example.com',
              name='CLI Admin')
    plantagenet.run()

    with plantagenet.app.app_context():
        user = plantagenet.User.get_by_email('cli-admin@example.com')
        assert user is not None
        assert user.is_admin is True


def test_run_create_user(ctx, monkeypatch):
    monkeypatch.setattr(plantagenet, 'getpass', lambda prompt: 'password123')
    _set_args(monkeypatch, create_user='cli-user@example.com')
    plantagenet.run()

    with plantagenet.app.app_context():
        user = plantagenet.User.get_by_email('cli-user@example.com')
        assert user is not None
        assert user.is_admin is False


def test_run_create_user_invalid_email_exits(ctx, monkeypatch):
    _set_args(monkeypatch, create_user='not-an-email')
    with pytest.raises(SystemExit):
        plantagenet.run()


def test_run_set_user_password(ctx, monkeypatch):
    monkeypatch.setattr(plantagenet, 'getpass', lambda prompt: 'password123')
    _set_args(monkeypatch, create_user='cli-pw@example.com')
    plantagenet.run()

    monkeypatch.setattr(plantagenet, 'getpass', lambda prompt: 'newpassword')
    _set_args(monkeypatch, set_user_password='cli-pw@example.com')
    plantagenet.run()

    with plantagenet.app.app_context():
        user = plantagenet.User.get_by_email('cli-pw@example.com')
        assert user.check_password('newpassword')


def test_run_set_user_password_unknown_email_exits(ctx, monkeypatch):
    _set_args(monkeypatch, set_user_password='nobody@example.com')
    with pytest.raises(SystemExit):
        plantagenet.run()


def test_run_list_users(ctx, monkeypatch):
    _set_args(monkeypatch, list_users=True)
    plantagenet.run()
